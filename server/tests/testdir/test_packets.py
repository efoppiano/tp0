import datetime
import unittest

from common.packets.packet_factory import PacketFactory

from common.errors import ProtocolViolation, InvalidPacketTypeError

from common.packets.store_response import StoreResponse, STATUS_OK

from common.packets.winners_response import WinnersResponse


class TestPackets(unittest.TestCase):
    def test_store_bet_decode(self):
        data = b"StoreBet:1;Juan Martin;Perez;34843065;1984-03-23;548"
        bet = PacketFactory.parse_store_bet_packet(data)

        self.assertEqual(bet.agency, 1)
        self.assertEqual(bet.first_name, "Juan Martin")
        self.assertEqual(bet.last_name, "Perez")
        self.assertEqual(bet.document, "34843065")
        self.assertEqual(bet.birthdate, datetime.date(1984, 3, 23))
        self.assertEqual(bet.number, 548)

    def test_store_bet_wrong_amount_of_segments(self):
        data = b"StoreBet:1;Juan Martin;Perez;34843065;1984-03-23"
        with self.assertRaises(ProtocolViolation):
            PacketFactory.parse_store_bet_packet(data)

    def test_store_bet_wrong_packet_type(self):
        data = b"AnotherType:1;Juan Martin;Perez;34843065;1984-03-23;548"
        with self.assertRaises(InvalidPacketTypeError):
            PacketFactory.parse_store_bet_packet(data)

    def test_store_bet_wrong_agency(self):
        data = b"StoreBet:one;Juan Martin;Perez;34843065;1984-03-23;548"
        with self.assertRaises(ValueError):
            PacketFactory.parse_store_bet_packet(data)

    def test_store_bet_wrong_number(self):
        data = b"StoreBet:1;Juan Martin;Perez;34843065;1984-03-23;one"
        with self.assertRaises(ValueError):
            PacketFactory.parse_store_bet_packet(data)

    def test_store_bet_wrong_birthdate(self):
        data = b"StoreBet:1;Juan Martin;Perez;34843065;1984-85-23;548"
        with self.assertRaises(ValueError):
            PacketFactory.parse_store_bet_packet(data)

    def test_store_batch_decode_one_bet(self):
        data = b"StoreBatch:1:Juan Martin;Perez;34843065;1984-03-23;548"
        bets = PacketFactory.parse_store_batch_packet(data)

        self.assertEqual(bets[0].agency, 1)
        self.assertEqual(len(bets), 1)
        self.assertEqual(bets[0].first_name, "Juan Martin")
        self.assertEqual(bets[0].last_name, "Perez")
        self.assertEqual(bets[0].document, "34843065")
        self.assertEqual(bets[0].birthdate, datetime.date(1984, 3, 23))
        self.assertEqual(bets[0].number, 548)

    def test_store_batch_decode_multiple_bets(self):
        data = b"StoreBatch:1:Juan Martin;Perez;34843065;1984-03-23;548:Maria;Gomez;12345678;1980-01-01;123"
        bets = PacketFactory.parse_store_batch_packet(data)

        self.assertEqual(bets[0].agency, 1)
        self.assertEqual(len(bets), 2)
        self.assertEqual(bets[0].first_name, "Juan Martin")
        self.assertEqual(bets[0].last_name, "Perez")
        self.assertEqual(bets[0].document, "34843065")
        self.assertEqual(bets[0].birthdate, datetime.date(1984, 3, 23))
        self.assertEqual(bets[0].number, 548)
        self.assertEqual(bets[1].first_name, "Maria")
        self.assertEqual(bets[1].last_name, "Gomez")
        self.assertEqual(bets[1].document, "12345678")
        self.assertEqual(bets[1].birthdate, datetime.date(1980, 1, 1))
        self.assertEqual(bets[1].number, 123)

    def test_store_batch_without_bets_should_fail(self):
        data = b"StoreBatch:1"
        with self.assertRaises(ProtocolViolation):
            PacketFactory.parse_store_batch_packet(data)

    def test_store_batch_wrong_packet_type(self):
        data = b"AnotherType:1:Juan Martin;Perez;34843065;1984-03-23;548"
        with self.assertRaises(InvalidPacketTypeError):
            PacketFactory.parse_store_batch_packet(data)

    def test_store_batch_wrong_agency(self):
        data = b"StoreBatch:one:Juan Martin;Perez;34843065;1984-03-23;548"
        with self.assertRaises(ValueError):
            PacketFactory.parse_store_batch_packet(data)

    def test_agency_close_decode(self):
        data = b"AgencyClose:1"
        agency = PacketFactory.parse_agency_close_packet(data)

        self.assertEqual(agency, "1")

    def test_agency_close_wrong_packet_type(self):
        data = b"AnotherType:1"
        with self.assertRaises(InvalidPacketTypeError):
            PacketFactory.parse_agency_close_packet(data)

    def test_winners_request_decode(self):
        data = b"WinnersRequest:1"
        agency = PacketFactory.parse_winners_request_packet(data)

        self.assertEqual(agency, "1")

    def test_winners_request_wrong_packet_type(self):
        data = b"AnotherType:1"
        with self.assertRaises(InvalidPacketTypeError):
            PacketFactory.parse_winners_request_packet(data)

    def test_store_response_encode(self):
        data = StoreResponse(STATUS_OK).to_bytes()
        self.assertEqual(data, b"StoreResponse:0\n")

    def test_winners_response_encode(self):
        documents = ["34843065", "12345678", "87654321"]
        data = WinnersResponse(documents).to_bytes()
        self.assertEqual(data, b"WinnersResponse:34843065;12345678;87654321\n")

    def test_winners_response_encode_empty(self):
        data = WinnersResponse([]).to_bytes()
        self.assertEqual(data, b"WinnersResponse:\n")

