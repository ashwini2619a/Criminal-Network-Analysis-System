package main

import (
	"crypto/subtle"
	"encoding/json"
	"fmt"
	"log"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

type IntrusionEvent struct {
	EventID    string `json:"eventId"`
	BopID      string `json:"bopId"`
	CameraID   string `json:"cameraId"`
	AlertType  string `json:"alertType"`
	SHA256Hash string `json:"sha256Hash"`
	Timestamp  string `json:"timestamp"`
	Verified   bool   `json:"verified"`
}

type IBVAPChaincode struct {
	contractapi.Contract
}

func (s *IBVAPChaincode) RecordIntrusion(ctx contractapi.TransactionContextInterface, eventId string, bopId string, cameraId string, alertType string, sha256Hash string, timestamp string) error {
	if eventId == "" || bopId == "" || cameraId == "" || alertType == "" || sha256Hash == "" || timestamp == "" {
		return fmt.Errorf("all parameters must be provided")
	}

	exists, err := s.EventExists(ctx, eventId)
	if err != nil {
		return err
	}
	if exists {
		return fmt.Errorf("the event %s already exists", eventId)
	}

	event := IntrusionEvent{
		EventID:    eventId,
		BopID:      bopId,
		CameraID:   cameraId,
		AlertType:  alertType,
		SHA256Hash: sha256Hash,
		Timestamp:  timestamp,
		Verified:   true,
	}

	eventJSON, err := json.Marshal(event)
	if err != nil {
		return err
	}

	err = ctx.GetStub().PutState(eventId, eventJSON)
	if err != nil {
		return err
	}

	indexName := "camera~event"
	cameraEventIndexKey, err := ctx.GetStub().CreateCompositeKey(indexName, []string{cameraId, eventId})
	if err != nil {
		return err
	}

	err = ctx.GetStub().PutState(cameraEventIndexKey, []byte{0x00})
	if err != nil {
		return err
	}

	bopIndexName := "bop~event"
	bopEventIndexKey, err := ctx.GetStub().CreateCompositeKey(bopIndexName, []string{bopId, eventId})
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState(bopEventIndexKey, []byte{0x00})
}

func (s *IBVAPChaincode) EventExists(ctx contractapi.TransactionContextInterface, eventId string) (bool, error) {
	eventJSON, err := ctx.GetStub().GetState(eventId)
	if err != nil {
		return false, fmt.Errorf("failed to read from world state: %v", err)
	}
	return eventJSON != nil, nil
}

func (s *IBVAPChaincode) VerifyEvidence(ctx contractapi.TransactionContextInterface, eventId string, testHash string) (bool, error) {
	eventJSON, err := ctx.GetStub().GetState(eventId)
	if err != nil {
		return false, fmt.Errorf("failed to read from world state: %v", err)
	}
	if eventJSON == nil {
		return false, fmt.Errorf("the event %s does not exist", eventId)
	}

	var event IntrusionEvent
	err = json.Unmarshal(eventJSON, &event)
	if err != nil {
		return false, err
	}

	match := subtle.ConstantTimeCompare([]byte(event.SHA256Hash), []byte(testHash)) == 1
	return match, nil
}

func (s *IBVAPChaincode) QueryCameraAuditTrail(ctx contractapi.TransactionContextInterface, cameraId string) ([]IntrusionEvent, error) {
	resultsIterator, err := ctx.GetStub().GetStateByPartialCompositeKey("camera~event", []string{cameraId})
	if err != nil {
		return nil, err
	}
	defer resultsIterator.Close()

	var events []IntrusionEvent
	for resultsIterator.HasNext() {
		responseRange, err := resultsIterator.Next()
		if err != nil {
			return nil, err
		}

		_, compositeKeyParts, err := ctx.GetStub().SplitCompositeKey(responseRange.Key)
		if err != nil {
			return nil, err
		}

		if len(compositeKeyParts) > 1 {
			returnedEventId := compositeKeyParts[1]
			eventJSON, err := ctx.GetStub().GetState(returnedEventId)
			if err != nil {
				return nil, err
			}
			if eventJSON != nil {
				var event IntrusionEvent
				err = json.Unmarshal(eventJSON, &event)
				if err != nil {
					return nil, err
				}
				events = append(events, event)
			}
		}
	}

	return events, nil
}

func (s *IBVAPChaincode) QueryBOPAuditTrail(ctx contractapi.TransactionContextInterface, bopId string) ([]IntrusionEvent, error) {
	resultsIterator, err := ctx.GetStub().GetStateByPartialCompositeKey("bop~event", []string{bopId})
	if err != nil {
		return nil, err
	}
	defer resultsIterator.Close()

	var events []IntrusionEvent
	for resultsIterator.HasNext() {
		responseRange, err := resultsIterator.Next()
		if err != nil {
			return nil, err
		}

		_, compositeKeyParts, err := ctx.GetStub().SplitCompositeKey(responseRange.Key)
		if err != nil {
			return nil, err
		}

		if len(compositeKeyParts) > 1 {
			returnedEventId := compositeKeyParts[1]
			eventJSON, err := ctx.GetStub().GetState(returnedEventId)
			if err != nil {
				return nil, err
			}
			if eventJSON != nil {
				var event IntrusionEvent
				err = json.Unmarshal(eventJSON, &event)
				if err != nil {
					return nil, err
				}
				events = append(events, event)
			}
		}
	}

	return events, nil
}

func (s *IBVAPChaincode) GetAllIntrusions(ctx contractapi.TransactionContextInterface) ([]IntrusionEvent, error) {
	resultsIterator, err := ctx.GetStub().GetStateByRange("", "")
	if err != nil {
		return nil, err
	}
	defer resultsIterator.Close()

	var events []IntrusionEvent
	for resultsIterator.HasNext() {
		queryResponse, err := resultsIterator.Next()
		if err != nil {
			return nil, err
		}

		var event IntrusionEvent
		err = json.Unmarshal(queryResponse.Value, &event)
		if err == nil && event.EventID != "" {
			events = append(events, event)
		}
	}

	return events, nil
}

func main() {
	chaincode, err := contractapi.NewChaincode(&IBVAPChaincode{})
	if err != nil {
		log.Panicf("Error creating IBVAP chaincode: %v", err)
	}

	if err := chaincode.Start(); err != nil {
		log.Panicf("Error starting IBVAP chaincode: %v", err)
	}
}
