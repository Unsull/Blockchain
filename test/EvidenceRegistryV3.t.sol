// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import { IAccessControl } from "@openzeppelin/contracts/access/IAccessControl.sol";
import { Pausable } from "@openzeppelin/contracts/utils/Pausable.sol";
import { Test } from "forge-std/Test.sol";
import { EvidenceRegistryV3 } from "../contracts/EvidenceRegistryV3.sol";
import { IEvidenceRegistryV3 } from "../contracts/interfaces/IEvidenceRegistryV3.sol";

contract EvidenceRegistryV3Test is Test {
    EvidenceRegistryV3 private registry;
    address private admin = makeAddr("admin");
    address private writer = makeAddr("writer");
    address private outsider = makeAddr("outsider");

    bytes32 private constant EVIDENCE_REF = keccak256("evidence");
    bytes32 private constant EVIDENCE_HASH = keccak256("hash");
    bytes32 private constant UPLOADER_REF = keccak256("uploader");
    bytes32 private constant OFFICER_REF = keccak256("officer");
    bytes32 private constant SESSION_REF = keccak256("session");
    uint64 private constant OCCURRED_AT = 1_700_000_000;

    function setUp() public {
        registry = new EvidenceRegistryV3(admin);
        bytes32 writerRole = registry.WRITER_ROLE();
        vm.prank(admin);
        registry.grantRole(writerRole, writer);
        vm.prank(writer);
        registry.recordEvidence(EVIDENCE_REF, EVIDENCE_HASH, UPLOADER_REF);
    }

    function testRecordViewPreservesActionAndTimestamps() public {
        vm.warp(OCCURRED_AT + 30);
        vm.expectEmit(true, true, true, true);
        emit IEvidenceRegistryV3.EvidenceAccessRecorded(
            EVIDENCE_REF,
            OFFICER_REF,
            SESSION_REF,
            IEvidenceRegistryV3.AccessAction.VIEW,
            OCCURRED_AT,
            OCCURRED_AT + 30,
            writer
        );

        vm.prank(writer);
        registry.recordAccess(
            EVIDENCE_REF,
            OFFICER_REF,
            SESSION_REF,
            IEvidenceRegistryV3.AccessAction.VIEW,
            OCCURRED_AT
        );

        (
            bytes32 evidenceRef,
            bytes32 officerRef,
            IEvidenceRegistryV3.AccessAction action,
            uint64 occurredAt,
            uint64 recordedAt,
            address recordedWriter
        ) = registry.getAccessBySession(SESSION_REF);
        assertEq(evidenceRef, EVIDENCE_REF);
        assertEq(officerRef, OFFICER_REF);
        assertEq(uint8(action), uint8(IEvidenceRegistryV3.AccessAction.VIEW));
        assertEq(occurredAt, OCCURRED_AT);
        assertEq(recordedAt, OCCURRED_AT + 30);
        assertEq(recordedWriter, writer);
        assertTrue(registry.accessSessionExists(SESSION_REF));
    }

    function testRecordDownloadSucceeds() public {
        vm.prank(writer);
        registry.recordAccess(
            EVIDENCE_REF,
            OFFICER_REF,
            SESSION_REF,
            IEvidenceRegistryV3.AccessAction.DOWNLOAD,
            OCCURRED_AT
        );
        (,, IEvidenceRegistryV3.AccessAction action, uint64 occurredAt,,) =
            registry.getAccessBySession(SESSION_REF);
        assertEq(uint8(action), uint8(IEvidenceRegistryV3.AccessAction.DOWNLOAD));
        assertEq(occurredAt, OCCURRED_AT);
    }

    function testDuplicateSessionReverts() public {
        vm.startPrank(writer);
        registry.recordAccess(
            EVIDENCE_REF,
            OFFICER_REF,
            SESSION_REF,
            IEvidenceRegistryV3.AccessAction.VIEW,
            OCCURRED_AT
        );
        vm.expectRevert(
            abi.encodeWithSelector(
                IEvidenceRegistryV3.AccessSessionAlreadyExists.selector, SESSION_REF
            )
        );
        registry.recordAccess(
            EVIDENCE_REF,
            OFFICER_REF,
            SESSION_REF,
            IEvidenceRegistryV3.AccessAction.DOWNLOAD,
            OCCURRED_AT
        );
        vm.stopPrank();
    }

    function testValidationReverts() public {
        vm.startPrank(writer);
        vm.expectRevert(IEvidenceRegistryV3.InvalidEvidenceRef.selector);
        registry.recordAccess(
            bytes32(0), OFFICER_REF, SESSION_REF, IEvidenceRegistryV3.AccessAction.VIEW, OCCURRED_AT
        );
        vm.expectRevert(IEvidenceRegistryV3.InvalidOfficerRef.selector);
        registry.recordAccess(
            EVIDENCE_REF,
            bytes32(0),
            SESSION_REF,
            IEvidenceRegistryV3.AccessAction.VIEW,
            OCCURRED_AT
        );
        vm.expectRevert(IEvidenceRegistryV3.InvalidAccessSessionRef.selector);
        registry.recordAccess(
            EVIDENCE_REF,
            OFFICER_REF,
            bytes32(0),
            IEvidenceRegistryV3.AccessAction.VIEW,
            OCCURRED_AT
        );
        vm.expectRevert(IEvidenceRegistryV3.InvalidOccurredAt.selector);
        registry.recordAccess(
            EVIDENCE_REF, OFFICER_REF, SESSION_REF, IEvidenceRegistryV3.AccessAction.VIEW, 0
        );
        vm.expectRevert(
            abi.encodeWithSelector(
                IEvidenceRegistryV3.EvidenceNotFound.selector, keccak256("missing")
            )
        );
        registry.recordAccess(
            keccak256("missing"),
            OFFICER_REF,
            SESSION_REF,
            IEvidenceRegistryV3.AccessAction.VIEW,
            OCCURRED_AT
        );
        vm.stopPrank();
    }

    function testMissingSessionReverts() public {
        vm.expectRevert(
            abi.encodeWithSelector(IEvidenceRegistryV3.AccessSessionNotFound.selector, SESSION_REF)
        );
        registry.getAccessBySession(SESSION_REF);
    }

    function testInvalidEnumValueIsRejectedByAbiDecoder() public {
        bytes memory payload = abi.encodeWithSelector(
            registry.recordAccess.selector,
            EVIDENCE_REF,
            OFFICER_REF,
            SESSION_REF,
            uint8(2),
            OCCURRED_AT
        );
        vm.prank(writer);
        (bool success,) = address(registry).call(payload);
        assertFalse(success);
        assertFalse(registry.accessSessionExists(SESSION_REF));
    }

    function testPausedRegistryRejectsAccess() public {
        vm.prank(admin);
        registry.pause();
        vm.expectRevert(Pausable.EnforcedPause.selector);
        vm.prank(writer);
        registry.recordAccess(
            EVIDENCE_REF,
            OFFICER_REF,
            SESSION_REF,
            IEvidenceRegistryV3.AccessAction.VIEW,
            OCCURRED_AT
        );
    }

    function testWriterRoleIsRequired() public {
        vm.expectPartialRevert(IAccessControl.AccessControlUnauthorizedAccount.selector);
        vm.prank(outsider);
        registry.recordAccess(
            EVIDENCE_REF,
            OFFICER_REF,
            SESSION_REF,
            IEvidenceRegistryV3.AccessAction.VIEW,
            OCCURRED_AT
        );
    }
}
