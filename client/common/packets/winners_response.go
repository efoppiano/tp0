package packets

import (
	"strings"
)

const WinnersResponsePacketType string = "WinnersResponse"

type WinnersResponsePacket struct {
	Documents []string
}

func newWinnersResponse(data []byte) (WinnersResponsePacket, error) {
	/*
		Parse the message and
		return a WinnersResponsePacket struct

		Each document is separated by ';' character
	*/

	if len(data) == 0 {
		return WinnersResponsePacket{
			Documents: []string{},
		}, nil
	}
	documents := strings.Split(string(data), ";")

	return WinnersResponsePacket{
		Documents: documents,
	}, nil
}
