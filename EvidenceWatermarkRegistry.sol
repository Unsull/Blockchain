// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract EvidenceWatermarkRegistry {
    struct Evidence {
        string watermarkHash;
        uint256 timestamp;
        bool isRecorded;
    }

    struct AccessLog {
        string accessHash;
        string accessSessionId;
        uint256 timestamp;
    }

    mapping(string => Evidence) private evidenceRecords;
    mapping(string => AccessLog[]) private accessLogs;

    event EvidenceStored(string evidenceId, string watermarkHash, uint256 timestamp);
    event AccessRecorded(
        string evidenceId,
        string accessHash,
        string accessSessionId,
        uint256 timestamp
    );

    function recordEvidence(
        string memory _evidenceId,
        string memory _watermarkHash
    ) public {
        require(
            !evidenceRecords[_evidenceId].isRecorded,
            "This evidence ID has already been recorded."
        );

        evidenceRecords[_evidenceId] = Evidence({
            watermarkHash: _watermarkHash,
            timestamp: block.timestamp,
            isRecorded: true
        });

        emit EvidenceStored(_evidenceId, _watermarkHash, block.timestamp);
    }

    function recordAccess(
        string memory _evidenceId,
        string memory _accessHash,
        string memory _accessSessionId
    ) public {
        require(evidenceRecords[_evidenceId].isRecorded, "Evidence not found.");

        accessLogs[_evidenceId].push(AccessLog({
            accessHash: _accessHash,
            accessSessionId: _accessSessionId,
            timestamp: block.timestamp
        }));

        emit AccessRecorded(_evidenceId, _accessHash, _accessSessionId, block.timestamp);
    }

    function getEvidenceData(
        string memory _evidenceId
    ) public view returns (string memory, uint256, bool) {
        require(evidenceRecords[_evidenceId].isRecorded, "Evidence ID not found.");

        Evidence memory evidence = evidenceRecords[_evidenceId];
        return (evidence.watermarkHash, evidence.timestamp, evidence.isRecorded);
    }

    function getAccessLogs(
        string memory _evidenceId
    ) public view returns (AccessLog[] memory) {
        require(evidenceRecords[_evidenceId].isRecorded, "Evidence not found.");
        return accessLogs[_evidenceId];
    }
}
