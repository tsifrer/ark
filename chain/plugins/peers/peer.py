import json
import requests

from chain.crypto.objects.block import Block
from chain.config import Config


class Peer(object):
    def __init__(self,
                 ip,
                 port,
                 chain_version,
                 nethash,
                 os,
                 height=None,
                 status=None,
                 healthy=True,
                 no_common_blocks=False
                 ):
        super().__init__()
        self.ip = ip
        self.port = port
        self.chain_version = chain_version
        self.nethash = nethash
        self.os = os

        self.height = height
        self.status = status
        self.healthy = healthy
        self.no_common_blocks = no_common_blocks

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
                timeout=timeout or config['peers']['global_timeout'],
            )
        except requests.exceptions.ConnectTimeout as e:
            print('Request to {} failed because of {} {}'.format(full_url, e))
            self.healthy = False
            return {}

        # TODO: rewrite _parse_headers to make it more meaningful
        self._parse_headers(response)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print('Request to {} failed because of {} {}'.format(full_url, e, response.content))
            self.healthy = False
        else:
            body = response.json()
            if body['success']:
                self.healthy = True
                return body
            else:
                print('Request to {} failed because of {}'.format(full_url, body))
                self.healthy = False
        return {}

    def has_common_blocks(self, block_ids):
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
        return True if body.get('common') else False

    def ping(self):
        # TODO: Make this more obvious somehow. _get sets 'healthy' flag on self
        # which is then used elsewhere to check if ping was successful or not.
        self._get('/peer/status', timeout=3)

        # TODO: Peer verification (PeerVerifier)

    def download_blocks(self, from_height):
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
            'healthy': self.healthy,
            'no_common_blocks': self.no_common_blocks,
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
            healthy=data['healthy'],
            no_common_blocks=data['no_common_blocks'],
        )
