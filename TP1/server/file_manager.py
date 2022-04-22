import os

from RWLock import RWLock


class FileManager:
    """A File Manager optimized for log files
    Our file manager can be used makes sure we don't have
      to worry about two processes trying to access the same file.
    The way of handling concurrency is throughout locking each file, with our own RWLock (multiple readers, one writer).
    For this we'll dynamically create one lock per file, the first time we need to access them.
    We'll track each of this locks on a dict,
      and we also need to account for this dict access, as it needs to be thread safe
      (to avoid two processes racing to create the same lock)."""

    def __init__(self, process_manager_lock):
        """As our way of handling concurrency is through Python's multiprocessing module,
        we need our global lock to be a multiprocessing.Manager().Lock() object.
        In any other case, a simple threading.lock() would suffice."""
        self.locks_lock = process_manager_lock
        self.locks = {}

    def get_lock(self, filename):
        """Returns a file's lock, creating it if it doesn't exist."""
        with self.locks_lock:
            if filename not in self.locks:
                self.locks[filename] = RWLock()
            return self.locks[filename]

    def exists(self, filename):
        """Returns True if the file exists, False otherwise."""
        self.get_lock(filename).acquire_read()
        r = os.path.isfile(filename)
        self.get_lock(filename).release_read()
        return r

    def append_line(self, filename, line):
        """Appends a line to the file, and creates the file if it doesn't exist."""
        self.get_lock(filename).acquire_write()
        with open(filename, "a") as f:
            f.write(line)
        self.get_lock(filename).release_write()

    def get_lines(self, filename, start_time, end_time):
        """Returns every line in the file between start_time and end_time.
        Both start_time and end_time can be None, in which case we simply don't filter by them.

        For this to work, this method (heavily) assumes that each line
          starts with a comparable-as-string timestamp (in our case, iso timestamps)
          followed by a space, and that the lines are in ascending order.
          (this assumptions are typically true for log files...)

        This method is optimized for getting the last lines of a file (i.e, our start_time is 'young')
          (we want our most recent logs!).

          - Instead of reading the whole file and fitting it into memory,
              we'll read it line by line starting from the bottom until we reach the start_time
              and then we'll filter by the end_time. So, if the end_time is too 'old', we are 'over-reading' the file."""
        lines = []
        self.get_lock(filename).acquire_read()
        with open(filename) as f:
            if start_time is None:
                lines = f.readlines()
            else:
                for line in read_line_backwards(f):
                    time = line.split()[0]
                    if time < start_time:
                        break
                    lines.append(line.strip())
                lines.reverse()
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
