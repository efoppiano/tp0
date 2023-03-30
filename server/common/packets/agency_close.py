AGENCY_CLOSE_PACKET_TYPE = "AgencyClose"


class AgencyClose:
    """
    Parse the agency number from the packet bytes received from agency.
    """
    @staticmethod
    def parse_agency(data: bytes) -> str:
        """
        Parse agency name from packet bytes received from agency.
        It should only have the agency number, encoded in UTF-8.
        """

        agency = data.decode('utf-8')

        return agency
