import fcntl
import os

LOCKS_DIR = "/shared-volume/locks/"


class FLock:
    """
    Wrapper for the fcntl.flock() function.
    """
    def __init__(self, name: str):
        self._lock_file = os.path.join(LOCKS_DIR, name)
        self._lock_file_fd = None
        self._exclusive = True

    def __acquire(self, exclusive=True):
        open_mode = os.O_RDWR | os.O_CREAT | os.O_TRUNC
        fd = os.open(self._lock_file, open_mode)
        try:
            if exclusive:
                fcntl.flock(fd, fcntl.LOCK_EX)
            else:
                fcntl.flock(fd, fcntl.LOCK_SH)
        except OSError:
            os.close(fd)
            raise
        else:
            self._lock_file_fd = fd

    def __release(self):
        if self._lock_file_fd is None:
            return
        fd = self._lock_file_fd
        self._lock_file_fd = None
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)

    def __call__(self, *args, **kwargs):
        self._exclusive = kwargs.pop("exclusive", True)
        return self

    def __enter__(self):
        self.__acquire(self._exclusive)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__release()
        return True
