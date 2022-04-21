import multiprocessing
import os


class FileManager:
    def __init__(self, process_manager_lock):
        self.locks_lock = process_manager_lock
        self.locks = {}

    def get_lock(self, lock_name):
        with self.locks_lock:
            if lock_name not in self.locks:
                self.locks[lock_name] = multiprocessing.Lock()
            return self.locks[lock_name]

    def get(self):
        pass

    def append_line(self, filename, line):
        with self.get_lock(filename):
            with open(os.path.join("/logs", filename), "a") as f:
                f.write(line)

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
