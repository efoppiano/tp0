package common

import (
	"fmt"
	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/common/model"
	log "github.com/sirupsen/logrus"
	"os"
	"strconv"
	"time"
)

func buildDatasetPath(agencyId string) string {
	return fmt.Sprintf("data/agency-%s.csv", agencyId)
}

func GetBetsFromFile(clientId string, betsPerRead int) (*BetsReader, error) {
	file, err := os.Open(buildDatasetPath(clientId))
	if err != nil {
		log.Fatalf("action: open_file | result: fail | error: %v", err)
		return &BetsReader{}, err
	}
	return NewBetsReader(file, betsPerRead), nil
}

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
