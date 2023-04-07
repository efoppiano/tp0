package packets

const WinnersRequestPacketType string = "WinnersRequest"

type WinnersRequestPacker struct {
	Agency string
}

func NewWinnersRequestPacket(agency string) *WinnersRequestPacker {
	return &WinnersRequestPacker{
		Agency: agency,
	}
}

func (packet *WinnersRequestPacker) Encode() ([]byte, error) {
	bytes := make([]byte, 0)
	bytes = append(bytes, WinnersRequestPacketType...)
	bytes = append(bytes, ':')
	bytes = append(bytes, packet.Agency...)

	return AppendLengthToPacket(bytes)
}
