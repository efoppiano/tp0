package packets

const AgencyClosePacketType string = "AgencyClose"

type AgencyClosePacket struct {
	Agency string
}

func NewAgencyClosePacket(agency string) *AgencyClosePacket {
	return &AgencyClosePacket{
		Agency: agency,
	}
}

func (packet *AgencyClosePacket) Encode() ([]byte, error) {
	bytes := make([]byte, 0)
	bytes = append(bytes, AgencyClosePacketType...)
	bytes = append(bytes, ':')
	bytes = append(bytes, packet.Agency...)

	return AppendLengthToPacket(bytes)
}
