################################################################################
# Description:
#  Non Blocking Stream Reader - read from stream/pipe without blocking
#
# original idea Eyal Arubas https://gist.github.com/EyalAr/7915597
# Copyright 2021 EtlamGit (for modifications)
################################################################################

from threading  import Thread
from queue      import Queue, Empty


# Exceptions we use in case our stream closes (EndOf)
class UnexpectedEndOfStream(Exception):
    pass


class NonBlockingStreamReader:

    def __init__(self, stream):
        self._s = stream    # the stream or pipe we connect to
        self._q = Queue()   # queue to hold received data
        self._run = True

        def _worker_to_fill_queue(w_stream, w_queue):
            while self._run:
                line = w_stream.readline()  # blocking read
                if line:
                    w_queue.put(line)
                else:
                    break
                    # raise UnexpectedEndOfStream

        # create separate thread with worker process
        self._t = Thread(target=_worker_to_fill_queue, args=(self._s, self._q))
        self._t.daemon = True
        self._t.start()

    def join(self):
        self._run = False
        self._t.join()

    # when timeout=None           -> non-blocking read
    # when timeout has some value ->     blocking read with timeout
    def readline(self, timeout=None):
        try:
            return self._q.get(block=(timeout is not None), timeout=timeout)
        except Empty:
            return None     # non-blocking 'empty' answer
