// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import {AccessControl} from "@openzeppelin/contracts/access/AccessControl.sol";
import {Pausable} from "@openzeppelin/contracts/utils/Pausable.sol";
import {IEvidenceRegistry} from "./interfaces/IEvidenceRegistry.sol";

contract EvidenceRegistry is IEvidenceRegistry, AccessControl, Pausable {
    bytes32 public constant WRITER_ROLE = keccak256("WRITER_ROLE");
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");

    mapping(bytes32 => EvidenceRecord) private evidenceRecords;
    mapping(bytes32 => AccessRecord) private accessRecords;

    constructor(address admin) {
        if (admin == address(0)) revert InvalidAdminAddress();
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(PAUSER_ROLE, admin);
    }

    function recordEvidence(
        bytes32 evidenceRef,
        bytes32 staticHash
    ) external onlyRole(WRITER_ROLE) whenNotPaused {
        if (evidenceRef == bytes32(0)) revert InvalidEvidenceRef();
        if (staticHash == bytes32(0)) revert InvalidStaticHash();
        if (evidenceRecords[evidenceRef].exists) revert EvidenceAlreadyExists(evidenceRef);

        uint64 recordedAt = _currentTimestamp();
        evidenceRecords[evidenceRef] = EvidenceRecord({
            staticHash: staticHash,
            recordedAt: recordedAt,
            writer: msg.sender,
            exists: true
        });

        emit EvidenceRecorded(evidenceRef, staticHash, recordedAt, msg.sender);
    }

    function recordAccess(
        bytes32 evidenceRef,
        bytes32 officerRef,
        bytes32 accessSessionRef
    ) external onlyRole(WRITER_ROLE) whenNotPaused {
        if (evidenceRef == bytes32(0)) revert InvalidEvidenceRef();
        if (officerRef == bytes32(0)) revert InvalidOfficerRef();
        if (accessSessionRef == bytes32(0)) revert InvalidAccessSessionRef();
        if (!evidenceRecords[evidenceRef].exists) revert EvidenceNotFound(evidenceRef);
        if (accessRecords[accessSessionRef].recordedAt != 0) {
            revert AccessSessionAlreadyExists(accessSessionRef);
        }

        uint64 recordedAt = _currentTimestamp();
        accessRecords[accessSessionRef] = AccessRecord({
            evidenceRef: evidenceRef,
            officerRef: officerRef,
            recordedAt: recordedAt,
            writer: msg.sender
        });

        emit EvidenceAccessRecorded(evidenceRef, officerRef, accessSessionRef, recordedAt, msg.sender);
    }

    function getEvidence(
        bytes32 evidenceRef
    ) external view returns (bytes32 staticHash, uint64 recordedAt, address writer, bool exists) {
        EvidenceRecord memory record = evidenceRecords[evidenceRef];
        if (!record.exists) revert EvidenceNotFound(evidenceRef);
        return (record.staticHash, record.recordedAt, record.writer, record.exists);
    }

    function getAccessBySession(
        bytes32 accessSessionRef
    ) external view returns (bytes32 evidenceRef, bytes32 officerRef, uint64 recordedAt, address writer) {
        AccessRecord memory record = accessRecords[accessSessionRef];
        if (record.recordedAt == 0) revert AccessSessionNotFound(accessSessionRef);
        return (record.evidenceRef, record.officerRef, record.recordedAt, record.writer);
    }

    function evidenceExists(bytes32 evidenceRef) external view returns (bool) {
        return evidenceRecords[evidenceRef].exists;
    }

    function accessSessionExists(bytes32 accessSessionRef) external view returns (bool) {
        return accessRecords[accessSessionRef].recordedAt != 0;
    }

    function pause() external onlyRole(PAUSER_ROLE) {
        _pause();
    }

    function unpause() external onlyRole(PAUSER_ROLE) {
        _unpause();
    }

    function _currentTimestamp() private view returns (uint64) {
        return uint64(block.timestamp);
    }
}
