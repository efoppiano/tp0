package common

import (
	"bufio"
	"errors"
	"fmt"
	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/common/model"
	"io"
	"os"
	"strconv"
	"strings"
	"time"
)

type BetsReader struct {
	betsPerRead int
	file        *os.File
	scanner     *bufio.Scanner
}

func NewBetsReader(file *os.File, betsPerRead int) *BetsReader {
	scanner := bufio.NewScanner(file)
	return &BetsReader{
		betsPerRead: betsPerRead,
		file:        file,
		scanner:     scanner,
	}
}

func (b *BetsReader) Close() error {
	return b.file.Close()
}

func (b *BetsReader) ReadBets() ([]model.Bet, error) {
	bets := make([]model.Bet, 0)
	for len(bets) < b.betsPerRead && b.scanner.Scan() {
		bet, err := getBetFromLine(b.scanner.Text())
		if err != nil {
			return nil, err
		}
		bets = append(bets, bet)
	}
	if err := b.scanner.Err(); err != nil {
		if err == io.EOF {
			return bets, nil
		}
		return nil, err
	}
	return bets, nil
}

func getBetFromLine(line string) (model.Bet, error) {
	fields := strings.Split(line, ",")
	if len(fields) != 5 {
		return model.Bet{}, errors.New(fmt.Sprintf("invalid bet line: %s", line))
	}

	firstName := fields[0]
	lastName := fields[1]
	document := fields[2]
	birthdate, err := time.Parse("2006-01-02", fields[3])
	if err != nil {
		return model.Bet{}, errors.New(fmt.Sprintf("Invalid birthdate: %s", fields[3]))
	}
	number, err := strconv.Atoi(fields[4])
	if err != nil {
		return model.Bet{}, errors.New(fmt.Sprintf("Invalid bet number: %s", fields[4]))
	}

	return model.NewBet(firstName, lastName, document, birthdate, uint64(number))
}
