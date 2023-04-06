package packets

import (
	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/common/model"
)

const StoreBatchPacketType string = "StoreBatch"

type StoreBatchPacket struct {
	Bets []*StoreBetPacket
}

func NewStoreBatchFromBets(bets []model.Bet, agency string) *StoreBatchPacket {
	packet := &StoreBatchPacket{
		Bets: make([]*StoreBetPacket, 0),
	}
	for _, bet := range bets {
		packet.Bets = append(packet.Bets, NewStoreBetFromBet(&bet, agency))
	}
	return packet
}

func (packet *StoreBatchPacket) Encode() ([]byte, error) {
	bytes := make([]byte, 0)
	bytes = append(bytes, StoreBatchPacketType...)
	bytes = append(bytes, ':')
	bytes = append(bytes, packet.Bets[0].Agency...)

	for _, bet := range packet.Bets {
		bytes = append(bytes, ':')
		encodedBet, err := bet.EncodeForBatch()
		if err != nil {
			return nil, err
		}
		bytes = append(bytes, encodedBet...)
	}
	return AppendLengthToPacket(bytes)
}
