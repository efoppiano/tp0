package packets

import (
	"bufio"
	"net"
	"strings"
)

const MaxPacketSize = 8192

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

func ReadRawPacket(conn *net.Conn) ([]byte, error) {
	reader := bufio.NewReader(*conn)
	message, err := ReadUntilWithMax(reader, '\n', MaxPacketSize)
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
