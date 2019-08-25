import asyncio
import logging
from collections import Counter
from time import time

logger = logging.getLogger(__name__)


class AsyncRateLimiter(object):
    def __init__(self):
        super().__init__()
        self.blocked_ips = {}
        self.lock = asyncio.Lock()
        self.last_reset = time()
        self.period = 1  # 1 second
        self.block_duration = 10  # 60 seconds

        self.default_limit = 10
        # event, rate limit per second
        self.event_settings = {
            "p2p.peer.postBlock": 1,
            "p2p.peer.getBlocks": 1,
            "p2p.peer.getPeers": 1,
            "p2p.peer.getStatus": 2,
            "p2p.peer.getCommonBlocks": 5,
        }

        self.counter = Counter()

    def _create_key(self, ip, event=None):
        if event:
            return "{}:{}".format(ip, event)
        else:
            return str(ip)

    async def exceeds_rate_limit(self, ip, event=None):
        with await self.lock:
            if ip in self.blocked_ips:
                block_end = self.blocked_ips[ip]
                if block_end < time():
                    del self.blocked_ips[ip]
                else:
                    logger.info(
                        "%s: Exceeding rate limit blocks you for one minute.", ip
                    )
                    return True

            elapsed = time() - self.last_reset
            period_remaining = self.period - elapsed

            # If the time window has elapsed then reset.
            if period_remaining <= 0:
                self.counter = Counter()
                self.last_reset = time()

            key = self._create_key(ip, event)
            self.counter[key] += 1

            if self.counter[key] > self.event_settings.get(event, self.default_limit):
                self.blocked_ips[str(ip)] = time() + self.block_duration
                logger.info("%s: Rate limit exceeded", ip)
                return True
