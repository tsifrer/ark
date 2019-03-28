import json
from datetime import datetime
from ipaddress import ip_address

import requests

from chain.config import Config
from chain.crypto.objects.block import Block
from .utils import ip_is_blacklisted, ip_is_whitelisted, verify_peer_status


class Peer(object):
    # TODO: Yeah, refactor this
    def __init__(self,
                 ip,
                 port,
                 chain_version,
                 nethash,
                 os,
                 height=None,
                 status=None,
                 no_common_blocks=False,
                 latency=None,
                 verification=None
                 ):
        super().__init__()
        self.ip = ip
        self.port = port
        self.chain_version = chain_version
        self.nethash = nethash
        self.os = os

        self.height = height
        self.status = status
        self.no_common_blocks = no_common_blocks
        self.latency = latency
        self.verification = verification

    @property
    def headers(self):
        return {
            'version': self.chain_version,
            'port': str(self.port),
            'nethash': self.nethash,
            'height': self.height,
            'Content-Type': 'application/json',
            'status': self.status,
        }

    def _parse_headers(self, response):
        for field in ['nethash', 'os', 'version']:
            value = response.headers.get(field) or getattr(self, field, None)
            setattr(self, field, value)

        self.milestone_hash = response.headers.get('milestonehash')

    def _get(self, url, params=None, timeout=None):
        scheme = 'https' if self.port == 443 else 'http'
        full_url = '{}://{}:{}{}'.format(scheme, self.ip, self.port, url)
        print(full_url)
        print(params)
        config = Config()
        try:
            response = requests.get(
                full_url,
                params=params,
                headers=self.headers,
                timeout=timeout or config['peers']['request_timeout'],
            )
        except requests.exceptions.RequestException as e:
            print('Request to {} failed because of {}'.format(full_url, e))
            self.latency = -1
            return {}

        self.latency = response.elapsed.total_seconds()
        # TODO: rewrite _parse_headers to make it more meaningful
        self._parse_headers(response)

        try:
            body = response.json()
        except ValueError:
            body = {}
            print('Request to {} returned HTTP {}. {}'.format(full_url, response.status_code, response.content))
        else:
            if body.get('success'):
                return body

        print('Request to {} failed. Response was {}'.format(full_url, body))
        return {}

    def is_valid(self):
        if ip_is_whitelisted(self.ip):
            return True

        if ip_is_blacklisted(self.ip):
            print('Peer is blacklisted {}'.format(self.ip))
            return False

        try:
            ip = ip_address(self.ip)
        except ValueError:
            print('Peer is invalid, because the IP is not a valid ip {}'.format(self.ip))
            return False

        if ip.is_private:
            print('Peer is invalid, because the IP is private IP')
            return False

        if self.no_common_blocks:
            print('Peer is invalid, as it has no common blocks')
            # TODO: This should be implemented as part of the guard thingy
            return False

        # TODO: check for valid network version

        return True

    def is_valid_network(self):
        config = Config()
        return self.nethash == config['network']['nethash']

    def get_common_block_by_ids(self, block_ids):
        print(block_ids)
        params = {
            'ids': ','.join(block_ids)
        }

        # TODO: This might not work as if only one block_id is passed in, othe relays
        # might not return what we want, based on the source code
        #
        # let url = `/peer/blocks/common?ids=${ids.join(",")}`;
        # if (ids.length === 1) {
        #     url += ",";
        # }
        body = self._get('/peer/blocks/common', params=params)
        print(body)
        return body.get('common')

    def fetch_blocks_from_height(self, from_height):
        params = {'lastBlockHeight': from_height}
        body = self._get('/peer/blocks', params=params)
        blocks = body.get('blocks', [])
        return [Block.from_dict(block) for block in blocks]

    def to_json(self):
        data = {
            'ip': self.ip,
            'port': self.port,
            'chain_version': self.chain_version,
            'nethash': self.nethash,
            'os': self.os,

            'height': self.height,
            'status': self.status,
            'no_common_blocks': self.no_common_blocks,
            'latency': self.latency,
            'verification': self.verification,
        }
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_data):
        data = json.loads(json_data)
        return cls(
            ip=data['ip'],
            port=data['port'],
            chain_version=data['chain_version'],
            nethash=data['nethash'],
            os=data['os'],
            height=data['height'],
            status=data['status'],
            no_common_blocks=data['no_common_blocks'],
            latency=data['latency'],
            verification=data['verification'],
        )




    def verify_peer(self, timeout=None):
        verification_start = datetime.now()
        if not timeout:
            config = Config()
            timeout = config['peers']['verification_timeout']

        body = self._get('/peer/status', timeout=timeout)

        # if not body:
        self.verification = verify_peer_status(self, body)
        if not self.verification:
            raise Exception('Peer not verified')



