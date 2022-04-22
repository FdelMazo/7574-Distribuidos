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

    def append_line(self, filename, line):
        self.get_lock(filename).acquire_write()
        with open(os.path.join("/logs", filename), "a") as f:
            f.write(line)
        self.get_lock(filename).release_write()

    def get_lines(self, filename, start_time, end_time):
        lines = []
        self.get_lock(filename).acquire_read()
        with open(os.path.join("/logs", filename)) as f:
            if start_time is None:
                lines = f.readlines()
            else:
                for line in read_line_backwards(f):
                    time = line.split()[0]
                    if time < start_time:
                        break
                    lines.append(line.strip())
        self.get_lock(filename).release_read()
        if end_time:
            lines = filter(lambda line: line.split()[0] <= end_time, lines)
        return lines


# https://stackoverflow.com/a/37795096
def read_line_backwards(f, blksz=524288):
    "Act as a generator to return the lines in file f in reverse order."
    buf = ""
    f.seek(0, os.SEEK_END)
    pos = f.tell()
    lastn = 0
    if pos == 0:
        pos = -1
    while pos != -1:
        nlpos = buf.rfind("\n", 0, -1)
        if nlpos != -1:
            line = buf[nlpos + 1 :]
            if line[-1] != "\n":
                line += "\n"
            buf = buf[: nlpos + 1]
            yield line
        elif pos == 0:
            pos = -1
            yield buf
        else:
            n = min(blksz, pos)
            os.lseek(f.fileno(), -(n + lastn), os.SEEK_CUR)
            rdbuf = f.read(n)
            lastn = len(rdbuf)
            buf = rdbuf + buf
            pos -= n
