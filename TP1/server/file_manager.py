import os

from RWLock import RWLock


class FileManager:
    def __init__(self, process_manager_lock):
        self.locks_lock = process_manager_lock
        self.locks = {}

    def get_lock(self, lock_name):
        with self.locks_lock:
            if lock_name not in self.locks:
                self.locks[lock_name] = RWLock()
            return self.locks[lock_name]

    def get(self):
        pass

    def append_line(self, filename, line):
        self.get_lock(filename).acquire_write()
        with open(os.path.join("/logs", filename), "a") as f:
            f.write(line)
        self.get_lock(filename).release_write()

    def get_lines(self, filename, start_timestamp=None, end_timestamp=None):
        self.get_lock(filename).acquire_read()
        with open(os.path.join("/logs", filename)) as f:
            lines = f.readlines()
        self.get_lock(filename).release_read()
        return lines

    def get_between(self, from_date, to_date):
        pass

    def aggregate(self, aggregate_op, aggregate_secs, from_date, to_date):
        pass

    def avg(self):
        pass

    def min(self):
        pass

    def max(self):
        pass

    def count(self):
        pass
