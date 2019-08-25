import json
import logging
import uuid
from ipaddress import ip_address

from websocket import create_connection

from chain.common.config import config
from chain.crypto.objects.block import Block

from .utils import ip_is_blacklisted, ip_is_whitelisted, verify_peer_status

logger = logging.getLogger(__name__)


class PeerRateLimitExceeded(Exception):
    pass


class PeerErrorResponse(Exception):
    def __init__(self, message, data):
        super().__init__(message)
        self.data = data


class PeerConnectionRefused(Exception):
    def __init__(self, message, exception):
        super().__init__(message)
        self.exception = exception


class Peer(object):
    def __init__(
        self,
        ip,
        port,
        chain_version,
        nethash,
        os,
        height=None,
        status=None,
        latency=None,
        verification=None,
    ):
        super().__init__()
        self.ip = ip
        self.port = port
        self.chain_version = chain_version
        self.nethash = nethash
        self.os = os

        self.height = height
        self.status = status
        self.latency = latency
        self.verification = verification

    @property
    def headers(self):
        return {
            "version": self.chain_version,
            "port": str(self.port),
            "nethash": self.nethash,
            "height": self.height,
            "Content-Type": "application/json",
            "status": self.status,
        }

    def _parse_headers(self, response):
        for field in ["nethash", "os", "version"]:
            value = response.headers.get(field) or getattr(self, field, None)
            setattr(self, field, value)

        self.milestone_hash = response.headers.get("milestonehash")

    def _fetch(self, event, data=None):
        url = "ws://{}:{}/socketcluster/".format(self.ip, self.port)

        # TODO: Handle errors and timeouts
        try:
            ws = create_connection(url, timeout=5)
        except ConnectionRefusedError as e:
            raise PeerConnectionRefused("Connection refused", e)

        handshake_uuid = str(uuid.uuid4())
        handshake_obj = {
            "event": "#handshake",
            "data": {"authToken": None},
            "cid": handshake_uuid,
        }
        ws.send(json.dumps(handshake_obj))
        handshake = json.loads(ws.recv())
        if handshake_uuid != handshake["rid"]:
            raise Exception("Handshake failed: {}".format(json.dumps(handshake)))

        cid = str(uuid.uuid4())
        payload = {
            "event": event,
            "cid": cid,
            "data": {"headers": {"Content-Type": "application/json"}, "data": data},
        }
        ws.send(json.dumps(payload))
        result = json.loads(ws.recv())
        if cid != result["rid"]:
            raise Exception(
                "Got wrong response from peer: {}".format(json.dumps(result))
            )
        ws.close()

        if not result:
            logger.warning(
                "Got an empty response (%s) from peer %s:%s ",
                result,
                self.ip,
                self.port,
            )
            return []

        # TODO: Do something with headers and the rest of response data
        if "error" in result:
            if result["error"].get("message") == "Rate limit exceeded":
                raise PeerRateLimitExceeded("Rate limit exceeded")
            else:
                error = result["error"]
                raise PeerErrorResponse(
                    "{}: {}".format(error["name"], error["message"])
                )
        try:
            data = result["data"]["data"]
        except KeyError as e:
            logger.error(result)
            raise e
        return data

    def is_valid(self):
        if ip_is_whitelisted(self.ip):
            return True

        if ip_is_blacklisted(self.ip):
            logger.warning("Peer is blacklisted %s", self.ip)
            return False

        try:
            ip = ip_address(self.ip)
        except ValueError:
            logger.warning(
                "Peer is invalid, because the IP is not a valid ip %s", self.ip
            )
            return False

        if ip.is_private:
            logger.warning("Peer is invalid, because the IP is private IP")
            return False

        # TODO: check for valid network version
        return True

    def is_valid_network(self):
        return self.nethash == config.network["nethash"]

    def fetch_common_block_by_ids(self, block_ids):
        payload = {"ids": block_ids}
        response = self._fetch("p2p.peer.getCommonBlocks", payload)
        logger.info(response)
        return response.get("common")

    def fetch_blocks_from_height(self, from_height):
        payload = {"lastBlockHeight": from_height, "serialized": True}
        blocks = self._fetch("p2p.peer.getBlocks", payload)
        return [Block.from_dict(block) for block in blocks]

    def fetch_peers(self):
        logger.info("Fetching a fresh peer list from %s:%s", self.ip, self.port)
        response = self._fetch("p2p.peer.getPeers")
        logger.info(response)
        peers = []
        for peer in response:
            if not ip_is_blacklisted(peer["ip"]):
                peers.append(
                    Peer(
                        ip=peer["ip"],
                        port=4002,  # peer["port"],
                        chain_version=peer["version"],
                        nethash=None,
                        os=None,
                    )
                )
        return peers

    def to_json(self):
        data = {
            "ip": self.ip,
            "port": self.port,
            "chain_version": self.chain_version,
            "nethash": self.nethash,
            "os": self.os,
            "height": self.height,
            "status": self.status,
            "latency": self.latency,
            "verification": self.verification,
        }
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_data):
        data = json.loads(json_data)
        return cls(
            ip=data["ip"],
            port=data["port"],
            chain_version=data["chain_version"],
            nethash=data["nethash"],
            os=data["os"],
            height=data["height"],
            status=data["status"],
            latency=data["latency"],
            verification=data["verification"],
        )

    def verify_peer(self, timeout=None):
        # verification_start = datetime.now()
        if not timeout:
            timeout = config.peers["verification_timeout"]

        response = self._fetch("p2p.peer.getStatus")
        if not response.get("state"):
            raise Exception("Peer not verified")

        self.verification = verify_peer_status(self, response["state"])
        if not self.verification:
            raise Exception("Peer not verified")
