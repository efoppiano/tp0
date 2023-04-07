package model

import (
	"errors"
	"time"
)

const MaxNameLength = 50
const MaxDocumentLength = 10
const MaxNumber = 9999

type Bet struct {
	FirstName string
	LastName  string
	Document  string
	BirthDate time.Time
	Number    uint64
}

func NewBet(firstName string, lastName string, document string, birthDate time.Time, number uint64) (Bet, error) {
	if len(firstName) > MaxNameLength {
		return Bet{}, errors.New("FirstName too long")
	}
	if len(lastName) > MaxNameLength {
		return Bet{}, errors.New("LastName too long")
	}
	if len(document) > MaxDocumentLength {
		return Bet{}, errors.New("document too long")
	}
	if number > MaxNumber {
		return Bet{}, errors.New("number too big")
	}
	if birthDate.Year() > 9999 {
		return Bet{}, errors.New("birthdate too big")
	}

	return Bet{
		FirstName: firstName,
		LastName:  lastName,
		Document:  document,
		BirthDate: birthDate,
		Number:    number,
	}, nil
}
