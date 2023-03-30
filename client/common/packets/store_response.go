package packets

import "strconv"

const StoreResponsePacketType string = "StoreResponse"
const StatusOk = 0
const StatusError = 1

type StoreResponse struct {
	Status int
}

func newStoreResponse(data []byte) (StoreResponse, error) {
	/*
		Parse the message and return a StoreResponse struct
	*/
	status, err := strconv.Atoi(string(data))
	if err != nil {
		return StoreResponse{}, err
	}

	return StoreResponse{
		Status: status,
	}, nil
}
