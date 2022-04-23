import multiprocessing

# Mostly taken from:
# - https://www.oreilly.com/library/view/python-cookbook/0596001673/ch06s04.html
# - https://stackoverflow.com/a/52794817 (ideas to fix the writer starvation issue)
# Adapted to use multiprocessing.Lock() instead of threading.Lock()


class RWLock:
    """A lock object that allows many simultaneous "read locks", but
    only one "write lock." """

    def __init__(self):
        self._read_ready = multiprocessing.Condition(multiprocessing.Lock())
        self._readers = 0
        self._writers = 0

    def acquire_read(self):
        """Acquire a read lock. Blocks only if a thread has
        acquired the write lock."""
        self._read_ready.acquire()
        try:
            while self._writers > 0:
                self._read_ready.wait()
            self._readers += 1
        finally:
            self._read_ready.release()

    def release_read(self):
        """Release a read lock."""
        self._read_ready.acquire()
        try:
            self._readers -= 1
            if not self._readers:
                self._read_ready.notify_all()
        finally:
            self._read_ready.release()

    def acquire_write(self):
        """Acquire a write lock. Blocks until there are no
        acquired read or write locks."""
        self._read_ready.acquire()
        self._writers += 1
        while self._readers > 0:
            self._read_ready.wait()

    def release_write(self):
        """Release a write lock."""
        self._writers -= 1
        self._read_ready.notify_all()
        self._read_ready.release()
