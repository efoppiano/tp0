from common.errors import ProtocolViolation
from common.utils import Bet
from common.packets.store_bet import StoreBet
from typing import List

STORE_BATCH_PACKET_TYPE = "StoreBatch"


class StoreBatch:
    @staticmethod
    def parse_batch(data: bytes) -> List[Bet]:
        """
        Parse batch from bytes received from agency.
        Encoding: utf-8
        Each segment is delimited by a ':' character.
        Segments:
        - agency (string).
        - bet1 (string).
        - bet2 (string).
        - ...
        - betN (string).
        The batch contains a list of bet units separated by a ';' character.
        Each bet is encoded like a StoreBet packet, without the agency number.
        Example:
        2:JUAN;PEREZ;12345678;1980-01-01;4385:MARTA;GOMEZ;87654321;1980-01-01;934
        """

        segments = data.split(b':')
        if len(segments) < 2:
            raise ProtocolViolation(f"Invalid number of segments in StoreBatch packet.")

        agency = segments[0].decode("utf-8")
        batch_bytes = segments[1:]
        bets = []
        for bet_bytes in batch_bytes:
            bets.append(StoreBet.parse_bet_from_batch(bet_bytes, agency))

        return bets
