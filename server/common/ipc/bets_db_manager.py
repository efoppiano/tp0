import logging
from typing import List

from common.ipc.FLock import FLock

from common.utils import Bet, store_bets

from common.utils import load_bets, has_won

BETS_CSV_LOCK_NAME = "bets.csv.lock"

class BetsDBManager:
    def __init__(self):
        self._lock = FLock(BETS_CSV_LOCK_NAME)
        self._winners_per_agency = None

    def store_bets(self, bets: List[Bet]):
        with self._lock:
            store_bets(bets)

    def get_winners_of_agency(self, agency: int) -> List[str]:
        if self._winners_per_agency is None:
            logging.info('action: populate_winners | result: in_progress')
            self._winners_per_agency = {}
            with self._lock(exclusive=False):
                for bet in load_bets():
                    if has_won(bet):
                        self._winners_per_agency.setdefault(bet.agency, [])
                        self._winners_per_agency[bet.agency].append(bet.document)

                logging.info(f'action: populate_winners | result: success | winners: {self._winners_per_agency}')
        return self._winners_per_agency.get(agency, [])
