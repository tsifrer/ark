import requests

from ark.crypto.models.block import Block


class Peer(object):

    def __init__(self, app, ip, port, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.ip = ip
        self.port = port
        self.healthy = True
        self.download_size = None
        self.no_common_blocks = False

        self.headers = {
            'version': self.app.version,
            'port': str(self.port),
            'nethash': self.app.config['network']['nethash'],
            'milestoneHash': self.app.config['milestone_hash'],
            'height': None,
            'Content-Type': 'application/json',
        }

        # if self.app.config['network']['name'] != 'mainnet':
        #     self.headers['hashid'] = 

    def _parse_headers(self, response):
        for field in ['nethash', 'os', 'version', 'hashid']:
            value = response.headers.get(field) or getattr(self, field, None)
            setattr(self, field, value)

        self.milestone_hash = response.headers.get('milestonehash')

    def _get(self, url, params=None, timeout=None):
        scheme = 'https' if self.port == 443 else 'http'
        full_url = '{}://{}:{}{}'.format(scheme, self.ip, self.port, url)
        response = requests.get(
            full_url,
            params=params,
            headers=self.headers,
            timeout=timeout or self.app.config['peers']['global_timeout']
        )
        # TODO: rewrite _parse_headers to make it more meaningful
        self._parse_headers(response)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print('Request to {} failed because of {}'.format(full_url, e))
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
            'ids': '11736050606814390998'#block_ids,
        }

        # TODO: This might not work as if only one block_id is passed in, othe relays
        # might not return what we want, based on the source code
        #
        # let url = `/peer/blocks/common?ids=${ids.join(",")}`;
        # if (ids.length === 1) {
        #     url += ",";
        # }
        body = self._get('/peer/blocks/common', params=params)
        return True if body.get('common') else False

    def download_blocks(self, from_height):
        params = {
            'lastBlockHeight': from_height,
        }
        body = self._get('/peer/blocks', params=params)
        blocks = body.get('blocks', [])
        return [Block(block) for block in blocks]
