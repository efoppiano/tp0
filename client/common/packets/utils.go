package packets

import (
	"bufio"
	"fmt"
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
	bytesRead := 0
	for bytesRead < length {
		n, err := (*reader).Read(buf[bytesRead:])
		if err != nil {
			return buf, err
		}
		bytesRead += n
	}
	return buf, nil
}

func ReadUntilWithMax(reader *bufio.Reader, delimiter byte, maxBytes int) ([]byte, error) {
	buf := make([]byte, 0)
	bytesRead := 0
	for {
		if bytesRead >= maxBytes {
			return buf, PacketTooBigError{
				MaxSize: maxBytes,
			}
		}
		b, err := (*reader).ReadByte()
		if err != nil {
			return buf, err
		}
		bytesRead += 1
		if b == delimiter {
			break
		}
		buf = append(buf, b)
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
