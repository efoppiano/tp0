from common.errors import ProtocolViolation
from common.utils import Bet

STORE_BET_PACKET_TYPE = "StoreBet"


class StoreBet:
    @staticmethod
    def parse_bet(data: bytes) -> Bet:
        """
        Parse bet from bytes received from agency.
        Each segment is delimited by a ';' character.
        Segments:
        - agency (utf-8).
        - first name (utf-8).
        - last name (utf-8).
        - document (utf-8).
        - birthdate (utf-8). Format "YYYY-MM-DD".
        - number (utf-8 encoded integer).
        """

        segments = data.split(b';')
        if len(segments) != 6:
            raise ProtocolViolation("Invalid number of segments in StoreBet packet.")

        agency = segments[0].decode("utf-8")
        first_name = segments[1].decode("utf-8")
        last_name = segments[2].decode("utf-8")
        document = segments[3].decode("utf-8")
        birthdate = segments[4].decode("utf-8")
        number = int(segments[5].decode("utf-8"))

        return Bet(agency, first_name, last_name, document, birthdate, number)


