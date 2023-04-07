from typing import Set

from common.ipc.FLock import FLock

AGENCIES_CLOSED_LOCK_NAME = "agencies_closed.lock"
AGENCIES_CLOSED_FILE_PATH = "/shared-volume/agencies_closed.txt"


def write_all(file, data):
    chars_written = 0
    while chars_written < len(data):
        chars_written += file.write(data[chars_written:])


class ClosedAgencies:
    """
    Provides a safe way to read and write the list of closed agencies.
    This is necessary because the list of closed agencies is shared between the
    servers.
    """
    def __init__(self):
        self._file_lock = FLock(AGENCIES_CLOSED_LOCK_NAME)

    def get_closed_agencies(self) -> Set[int]:
        """
        Returns a set of the closed agencies.

        The set is empty if the file does not exist.
        """
        with self._file_lock(exclusive=False):
            try:
                file = open(AGENCIES_CLOSED_FILE_PATH, "r")
            except FileNotFoundError:
                return set()

            agencies_closed = set()
            for line in file:
                agencies_closed.add(int(line))
            file.close()
        return agencies_closed

    def contains(self, agency: int) -> bool:
        """
        Returns True if the agency is in the list of closed agencies.
        Returns False if the agency is not in the list of closed agencies or if the file does not exist.
        """

        with self._file_lock(exclusive=False):
            try:
                with open(AGENCIES_CLOSED_FILE_PATH, "r") as file:
                    for line in file:
                        if int(line) == agency:
                            file.close()
                            return True
                return False

            except FileNotFoundError:
                return False

    def add(self, agency: int):
        """
        Adds the agency to the list of closed agencies.
        """
        with self._file_lock, open(AGENCIES_CLOSED_FILE_PATH, "a+") as file:
            write_all(file, f"{agency}\n")
