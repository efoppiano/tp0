from typing import Set

class ClosedAgencies:
    """
    Provides a safe way to read and write the list of closed agencies.
    This is necessary because the list of closed agencies is shared between the
    servers.
    """
    def __init__(self):
        self._closed_agencies = set()

    def get_closed_agencies(self) -> Set[int]:
        """
        Returns a set of the closed agencies.
        """
        return self._closed_agencies

    def contains(self, agency: int) -> bool:
        """
        Returns True if the agency is in the list of closed agencies.
        Returns False if the agency is not in the list of closed agencies or if the file does not exist.
        """
        return agency in self._closed_agencies

    def add(self, agency: int):
        """
        Adds the agency to the list of closed agencies.
        """
        self._closed_agencies.add(agency)
