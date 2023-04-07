package packets

import (
	"bufio"
	"encoding/binary"
	"net"
	"strings"
)

const MaxPacketSize = 8192
const PacketLengthFieldSize = 2

func checkPacketType(data []byte, expected string) error {
	packetType := strings.Split(string(data), ":")[0]
	if packetType != expected {
		return PacketTypeMismatchError{
			Expected: expected,
			Received: packetType,
		}
	}

	return nil
}

func removePacketType(data []byte) []byte {
	packetType := strings.Split(string(data), ":")[0]
	return data[len(packetType)+1:]
}

func ReadValidLength(reader *bufio.Reader) (uint16, error) {
	lengthBytes, err := ReadExact(reader, 2)
	if err != nil {
		return 0, err
	}
	length := binary.BigEndian.Uint16(lengthBytes)
	if length > MaxPacketSize-PacketLengthFieldSize {
		return 0, PacketTooBigError{
			MaxSize: MaxPacketSize - PacketLengthFieldSize,
		}
	}

	return length, nil
}

func ReadRawPacket(conn *net.Conn) ([]byte, error) {
	reader := bufio.NewReader(*conn)
	length, err := ReadValidLength(reader)
	if err != nil {
		return nil, err
	}

	message, err := ReadExact(reader, int(length))
	if err != nil {
		return message, err
	}

	return message, nil
}

func DecodeStoreResponse(data []byte) (StoreResponse, error) {
	err := checkPacketType(data, StoreResponsePacketType)
	if err != nil {
		return StoreResponse{}, err
	}
	data = removePacketType(data)

	packet, err := newStoreResponse(data)
	if err != nil {
		return StoreResponse{}, err
	}

	return packet, nil
}

func DecodeWinnersResponsePacket(data []byte) (WinnersResponsePacket, error) {
	err := checkPacketType(data, WinnersResponsePacketType)
	if err != nil {
		return WinnersResponsePacket{}, err
	}
	data = removePacketType(data)

	packet, err := newWinnersResponse(data)
	if err != nil {
		return WinnersResponsePacket{}, err
	}

	return packet, nil
}
