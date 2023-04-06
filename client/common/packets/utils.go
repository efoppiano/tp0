package packets

import (
	"bufio"
	"encoding/binary"
	"fmt"
	"io"
	"net"
)

func WriteAll(conn *net.Conn, bytes []byte) error {
	bytesWritten := 0
	for bytesWritten < len(bytes) {
		n, err := fmt.Fprintf(*conn, string(bytes[bytesWritten:]))

		if err != nil {
			return err
		}
		bytesWritten += n
	}
	return nil
}

func ReadExact(reader *bufio.Reader, length int) ([]byte, error) {
	buf := make([]byte, length)
	_, err := io.ReadFull(reader, buf)
	if err != nil {
		return nil, err
	}
	return buf, nil
}

func AppendWithDelimiter(bytes []byte, delimiter string, elements ...string) []byte {
	for _, element := range elements[:len(elements)-1] {
		bytes = append(bytes, []byte(element)...)
		bytes = append(bytes, []byte(delimiter)...)
	}
	bytes = append(bytes, []byte(elements[len(elements)-1])...)

	return bytes
}

func AppendLengthToPacket(bytes []byte) ([]byte, error) {
	length := len(bytes)
	if length > MaxPacketSize-PacketLengthFieldSize {
		return bytes, PacketTooBigError{
			MaxSize: MaxPacketSize,
		}
	}

	lengthBytes := make([]byte, 2)
	binary.BigEndian.PutUint16(lengthBytes, uint16(length))
	bytes = append(lengthBytes, bytes...)

	return bytes, nil
}
