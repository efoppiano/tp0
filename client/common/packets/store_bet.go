package packets

import (
	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/common/model"
	log "github.com/sirupsen/logrus"
	"strconv"
	"time"
)

const PacketTypeStoreBet string = "StoreBet"

type StoreBetPacket struct {
	Agency    string
	FirstName string
	LastName  string
	Document  string
	BirthDate time.Time
	Number    uint64
}

func NewStoreBetFromBet(bet *model.Bet, agency string) *StoreBetPacket {
	return &StoreBetPacket{
		Agency:    agency,
		FirstName: bet.FirstName,
		LastName:  bet.LastName,
		Document:  bet.Document,
		BirthDate: bet.BirthDate,
		Number:    bet.Number,
	}
}

func (packet *StoreBetPacket) Encode() ([]byte, error) {
	bytes := make([]byte, 0)
	bytes = append(bytes, PacketTypeStoreBet...)
	bytes = append(bytes, ':')

	bytes = AppendWithDelimiter(bytes, ";",
		packet.Agency,
		packet.FirstName,
		packet.LastName,
		packet.Document,
		packet.BirthDate.Format("2006-01-02"),
		strconv.Itoa(int(packet.Number)),
	)
	log.Infof("action: encode_packet | result: success | client_id: %v | packet: %v", packet.Agency, string(bytes))
	return AppendLengthToPacket(bytes)
}

func (packet *StoreBetPacket) EncodeForBatch() ([]byte, error) {
	bytes := make([]byte, 0)
	bytes = AppendWithDelimiter(bytes, ";",
		packet.FirstName,
		packet.LastName,
		packet.Document,
		packet.BirthDate.Format("2006-01-02"),
		strconv.Itoa(int(packet.Number)),
	)
	return bytes, nil
}
