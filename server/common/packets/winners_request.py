WINNERS_REQUEST_PACKET_TYPE = "WinnersRequest"


class WinnersRequest:
    @staticmethod
    def parse_agency(data: bytes) -> str:
        """
        Parse agency name from bytes received from agency.
        It should only have the agency number, encoded in UTF-8.
        """

        agency = data.decode('utf-8')

        return agency
