package model

import (
	"time"
)

type Bet struct {
	FirstName string
	LastName  string
	Document  string
	BirthDate time.Time
	Number    uint64
}

func NewBet(firstName string, lastName string, document string, birthDate time.Time, number uint64) Bet {
	return Bet{
		FirstName: firstName,
		LastName:  lastName,
		Document:  document,
		BirthDate: birthDate,
		Number:    number,
	}
}
