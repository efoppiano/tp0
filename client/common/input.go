package common

import (
	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/common/model"
	"os"
	"strconv"
	"time"
)

func GetBetFromEnv() (model.Bet, error) {
	firstName := os.Getenv("NOMBRE")
	lastName := os.Getenv("APELLIDO")
	document := os.Getenv("DOCUMENTO")
	birthdate, err := time.Parse("2006-01-02", os.Getenv("NACIMIENTO"))
	if err != nil {
		return model.Bet{}, err
	}
	number, err := strconv.Atoi(os.Getenv("NUMERO"))
	if err != nil {
		return model.Bet{}, err
	}

	return model.NewBet(firstName, lastName, document, birthdate, uint64(number)), nil
}
