
import asyncio
import heapq
import logging
from ..common.peer import Peer
from ..client.http_client import ping


class PeerProber:
    def __init__(self, peers):
        self._peers = peers
        self._actives = set()
        self._updates = None
        self._probe_heap = []
        self._probing = False

    def get_actives(self):
        return list(self._actives)

    def update_peers(self, peers):
        self._updates = set(peers)

    def _reset_peer_heap(self):
        self._probe_heap = []
        for peer in self._peers:
            heapq.heappush(self._probe_heap, (peer.get_epoch(), peer))

    def _do_update_peers(self):
        if self._updates is not None:
            peers_removed = self._peers - self._updates
            self._peers = self._updates
            self._updates = None
            self._actives = self._actives - peers_removed
            self._reset_peer_heap()

    async def start_probe(self):
        """Start probing peers for liveness.

        This function uses asyncio to probe peers for liveness. It will wake up every 1 seconds, and 
        pop a peer from the heap. It will then send a ping request to the peer. The peer is taken out
        of the haep until we get a response from the peer or the ping request times out. After that,
        the peer is put back into the heap.
        """
        if self._probing:
            return

        self._probing = True

        # Initialize the heap with the peers, sorted by their epoch
        self._reset_peer_heap()

        if len(self._probe_heap) == 0:
            logging.info("No peers configured to probe")

        def probe_cb(task):
            try:
                peer = task.result()
                if isinstance(peer, Peer):
                    heapq.heappush(self._probe_heap, (peer.get_epoch(), peer))
                    if peer.is_alive() and peer in self._peers:
                        self._actives.add(peer)
                    else:
                        self._actives.discard(peer)
            except asyncio.exceptions.CancelledError:
                logging.debug("probing is canceled")

        while self._probing:
            await asyncio.sleep(3)

            self._do_update_peers()

            if len(self._probe_heap) == 0:
                continue

            _, peer = heapq.heappop(self._probe_heap)
            probe = asyncio.create_task(ping(peer))
            probe.add_done_callback(probe_cb)

    async def stop_probe(self):
        self._probing = False
        self._probe_heap = []
        self._actives = set()
