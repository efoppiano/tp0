package packets

import "fmt"

type PacketTooBigError struct {
	MaxSize int
}

func (e PacketTooBigError) Error() string {
	return fmt.Sprintf("Packet too big. Max size is %d", e.MaxSize)
}

type PacketTypeMismatchError struct {
	Expected string
	Received string
}

func (e PacketTypeMismatchError) Error() string {
	return fmt.Sprintf("Packet type mismatch. Expected %d, received %d", e.Expected, e.Received)
}
