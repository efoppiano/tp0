package common

import (
	"errors"
	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/common/model"
	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/common/packets"
	log "github.com/sirupsen/logrus"
	"math"
	"net"
	"os"
	"time"
)

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	BatchSize     int
	RetrySleep    time.Duration
	RetrySleepMax time.Duration
}

// Client Entity that encapsulates how
type Client struct {
	config       ClientConfig
	conn         net.Conn
	shutdownChan chan os.Signal
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig, shutdownChan chan os.Signal) *Client {
	client := &Client{
		config:       config,
		shutdownChan: shutdownChan,
	}
	return client
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Fatalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	c.conn = conn
	return nil
}

func (c *Client) SendBet(bet *model.Bet) error {
	packet := packets.NewStoreBetFromBet(bet, c.config.ID)
	bytes, err := packet.Encode()
	if err != nil {
		log.Errorf("action: encode_packet | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return err
	}
	err = packets.WriteAll(&c.conn, bytes)
	if err != nil {
		log.Errorf("action: send_packet | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return err
	}
	log.Infof("action: send_packet | result: success | client_id: %v | packet: %v",
		c.config.ID,
		packet,
	)

	return nil
}

func (c *Client) ReceiveBetResponse() error {
	rawPacket, err := packets.ReadRawPacket(&c.conn)
	if err != nil {
		log.Errorf("action: receive_bet_response | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return err
	}
	packet, err := packets.DecodeStoreResponse(rawPacket)
	if err != nil {
		log.Errorf("action: receive_bet_response | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return err
	}
	if packet.Status == packets.StatusError {
		log.Errorf("action: receive_bet_response | result: fail | client_id: %v",
			c.config.ID,
		)
		return errors.New("StoreResponse status is an error")
	}
	log.Infof("action: receive_bet_response | result: success | client_id: %v",
		c.config.ID,
	)

	return nil
}

var ErrShutdown = errors.New("shutdown")

func (c *Client) SendBets(bets []model.Bet) error {
	for _, bet := range bets {
		err := c.createClientSocket()
		if err != nil {
			return err
		}
		err = c.SendBet(&bet)
		if err != nil {
			return err
		}
		err = c.ReceiveBetResponse()
		if err != nil {
			return err
		}
		log.Infof("action: apuesta_enviada | result: success | dni: %v | numero: %v",
			bet.Document,
			bet.Number)
		err = c.conn.Close()
		if err != nil {
			return err
		}
		c.conn = nil
		select {
		case <-c.shutdownChan:
			return ErrShutdown
		default:
			continue
		}
	}

	log.Infof("action: send_bets | result: success | client_id: %v", c.config.ID)
	return nil
}

// Shutdown executes the shutdown of the client
func (c *Client) Shutdown() {
	// Socket is already closed by the loop
	log.Infof("action: shutdown | result: success | client_id: %v", c.config.ID)
}

func (c *Client) SendBetsInBatches(betsReader *BetsReader) error {
	bets, err := betsReader.ReadBets()
	for err == nil && len(bets) > 0 {
		err := c.createClientSocket()
		if err != nil {
			return err
		}
		err = c.SendBatch(bets)
		if err != nil {
			return err
		}
		bets, err = betsReader.ReadBets()
		if err != nil {
			return err
		}
		select {
		case <-c.shutdownChan:
			return ErrShutdown
		default:
			continue
		}
	}
	if err != nil {
		return err
	}
	log.Infof("action: send_bets_in_batches | result: success | client_id: %v", c.config.ID)
	return nil
}

func (c *Client) SendBatch(bets []model.Bet) error {
	packet := packets.NewStoreBatchFromBets(bets, c.config.ID)
	log.Infof("action: send_batch | result: in_progress | client_id: %v",
		c.config.ID,
	)
	bytes, err := packet.Encode()
	if err != nil {
		log.Errorf("action: encode_packet | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return err
	}
	err = packets.WriteAll(&c.conn, bytes)
	if err != nil {
		log.Errorf("action: encode_packet | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return err
	}
	log.Infof("action: send_batch | result: success | client_id: %v | packet: %v",
		c.config.ID,
		string(bytes),
	)

	err = c.ReceiveBetResponse()
	if err != nil {
		log.Errorf("action: receive_bet_response | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)

		return err
	}
	err = c.conn.Close()
	if err != nil {
		return err
	}
	c.conn = nil
	log.Infof("action: send_batch | result: success | client_id: %v | bets_sent: %v",
		c.config.ID,
		len(bets),
	)

	return nil
}

func (c *Client) CloseAgency() {
	err := c.createClientSocket()
	if err != nil {
		log.Errorf("action: close_agency | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return
	}
	packet := packets.NewAgencyClosePacket(c.config.ID)
	bytes, err := packet.Encode()
	if err != nil {
		log.Errorf("action: close_agency | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return
	}
	err = packets.WriteAll(&c.conn, bytes)
	if err != nil {
		log.Errorf("action: close_agency | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return
	}
	log.Infof("action: close_agency | result: success | client_id: %v",
		c.config.ID,
	)
	return
}

func (c *Client) GetWinners() ([]string, error) {
	retries := 0
	for {
		err := c.createClientSocket()
		if err != nil {
			return nil, err
		}
		log.Infof("action: get_winners | result: in_progress | client_id: %v",
			c.config.ID,
		)

		packet := packets.NewWinnersRequestPacket(c.config.ID)
		bytes, err := packet.Encode()
		if err != nil {
			log.Errorf("action: get_winners | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			return nil, err
		}
		err = packets.WriteAll(&c.conn, bytes)
		if err != nil {
			return nil, err
		}

		rawPacket, err := packets.ReadRawPacket(&c.conn)
		if err != nil {
			return nil, err
		}
		if packets.IsForNotReadyResponse(rawPacket) {
			log.Infof("action: get_winners | result: not_ready | client_id: %v",
				c.config.ID,
			)
			err = c.conn.Close()
			if err != nil {
				return nil, err
			}
			c.conn = nil
			waitTime := c.getWaitChan(retries)
			retries++
			select {
			case <-c.shutdownChan:
				return nil, ErrShutdown
			case <-waitTime:
				continue
			}
		} else {
			response, err := packets.DecodeWinnersResponsePacket(rawPacket)
			if err != nil {
				log.Errorf("action: receive_packet | result: fail | client_id: %v | error: %v",
					c.config.ID,
					err,
				)
				return nil, err
			}
			return response.Documents, nil
		}
	}
}

func (c *Client) getWaitChan(retries int) <-chan time.Time {
	waitTime := c.config.RetrySleep * time.Duration(math.Pow(2, float64(retries)))
	if waitTime > c.config.RetrySleepMax {
		waitTime = c.config.RetrySleepMax
	}
	log.Infof("action: get_wait_chan | result: success | client_id: %v | wait_time: %v",
		c.config.ID,
		waitTime,
	)

	return time.After(waitTime)
}
