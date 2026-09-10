// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

interface IEvidenceRegistryV3 {
    enum AccessAction {
        VIEW,
        DOWNLOAD
    }

    struct EvidenceRecord {
        bytes32 evidenceHash;
        bytes32 uploaderRef;
        uint64 recordedAt;
        address writer;
        bool exists;
    }

    struct AccessRecord {
        bytes32 evidenceRef;
        bytes32 officerRef;
        AccessAction action;
        uint64 occurredAt;
        uint64 recordedAt;
        address writer;
    }

    error InvalidAdminAddress();
    error InvalidEvidenceRef();
    error InvalidEvidenceHash();
    error InvalidUploaderRef();
    error InvalidOfficerRef();
    error InvalidAccessSessionRef();
    error InvalidOccurredAt();
    error EvidenceAlreadyExists(bytes32 evidenceRef);
    error EvidenceNotFound(bytes32 evidenceRef);
    error AccessSessionAlreadyExists(bytes32 accessSessionRef);
    error AccessSessionNotFound(bytes32 accessSessionRef);

    event EvidenceRecorded(
        bytes32 indexed evidenceRef,
        bytes32 evidenceHash,
        bytes32 indexed uploaderRef,
        uint64 recordedAt,
        address indexed writer
    );

    event EvidenceAccessRecorded(
        bytes32 indexed evidenceRef,
        bytes32 indexed officerRef,
        bytes32 indexed accessSessionRef,
        AccessAction action,
        uint64 occurredAt,
        uint64 recordedAt,
        address writer
    );

    function recordEvidence(bytes32 evidenceRef, bytes32 evidenceHash, bytes32 uploaderRef) external;

    function recordAccess(
        bytes32 evidenceRef,
        bytes32 officerRef,
        bytes32 accessSessionRef,
        AccessAction action,
        uint64 occurredAt
    ) external;

    function getEvidence(bytes32 evidenceRef)
        external
        view
        returns (
            bytes32 evidenceHash,
            bytes32 uploaderRef,
            uint64 recordedAt,
            address writer,
            bool exists
        );

    function getAccessBySession(bytes32 accessSessionRef)
        external
        view
        returns (
            bytes32 evidenceRef,
            bytes32 officerRef,
            AccessAction action,
            uint64 occurredAt,
            uint64 recordedAt,
            address writer
        );

    function evidenceExists(bytes32 evidenceRef) external view returns (bool);

    function accessSessionExists(bytes32 accessSessionRef) external view returns (bool);

    function pause() external;

    function unpause() external;
}
