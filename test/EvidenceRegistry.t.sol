// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import { Test } from "forge-std/Test.sol";
import { EvidenceRegistry } from "../contracts/EvidenceRegistry.sol";
import { IEvidenceRegistry } from "../contracts/interfaces/IEvidenceRegistry.sol";

contract EvidenceRegistryTest is Test {
    EvidenceRegistry internal registry;
    address internal admin = address(0xA11CE);
    address internal writer = address(0xB0B);
    bytes32 internal evidenceRef = keccak256("evidence");
    bytes32 internal staticHash = keccak256("static");

    event EvidenceRecorded(
        bytes32 indexed evidenceRef, bytes32 staticHash, uint64 recordedAt, address indexed writer
    );

    event EvidenceAccessRecorded(
        bytes32 indexed evidenceRef,
        bytes32 indexed officerRef,
        bytes32 indexed accessSessionRef,
        uint64 recordedAt,
        address writer
    );

    function setUp() public {
        registry = new EvidenceRegistry(admin);
        bytes32 writerRole = registry.WRITER_ROLE();
        vm.prank(admin);
        registry.grantRole(writerRole, writer);
    }

    function testDeploymentGrantsAdmin() public view {
        assertTrue(registry.hasRole(registry.DEFAULT_ADMIN_ROLE(), admin));
        assertTrue(registry.hasRole(registry.PAUSER_ROLE(), admin));
    }

    function testRejectsZeroAdmin() public {
        vm.expectRevert(IEvidenceRegistry.InvalidAdminAddress.selector);
        new EvidenceRegistry(address(0));
    }

    function testWriterRecordsEvidence() public {
        vm.warp(1_700_000_000);
        vm.expectEmit(true, false, false, true);
        emit EvidenceRecorded(evidenceRef, staticHash, uint64(block.timestamp), writer);

        vm.prank(writer);
        registry.recordEvidence(evidenceRef, staticHash);

        (bytes32 storedHash, uint64 recordedAt, address storedWriter, bool exists) =
            registry.getEvidence(evidenceRef);
        assertEq(storedHash, staticHash);
        assertEq(recordedAt, uint64(block.timestamp));
        assertEq(storedWriter, writer);
        assertTrue(exists);
        assertTrue(registry.evidenceExists(evidenceRef));
    }

    function testRejectsUnauthorizedEvidenceWrite() public {
        vm.expectRevert();
        registry.recordEvidence(evidenceRef, staticHash);
    }

    function testRejectsZeroEvidenceRef() public {
        vm.prank(writer);
        vm.expectRevert(IEvidenceRegistry.InvalidEvidenceRef.selector);
        registry.recordEvidence(bytes32(0), staticHash);
    }

    function testRejectsZeroStaticHash() public {
        vm.prank(writer);
        vm.expectRevert(IEvidenceRegistry.InvalidStaticHash.selector);
        registry.recordEvidence(evidenceRef, bytes32(0));
    }

    function testRejectsDuplicateEvidenceRef() public {
        vm.startPrank(writer);
        registry.recordEvidence(evidenceRef, staticHash);
        vm.expectRevert(
            abi.encodeWithSelector(IEvidenceRegistry.EvidenceAlreadyExists.selector, evidenceRef)
        );
        registry.recordEvidence(evidenceRef, keccak256("new"));
        vm.stopPrank();
    }

    function testRecordsAccess() public {
        bytes32 officerRef = keccak256("officer");
        bytes32 accessSessionRef = keccak256("session");
        vm.prank(writer);
        registry.recordEvidence(evidenceRef, staticHash);

        vm.warp(1_700_000_100);
        vm.expectEmit(true, true, true, true);
        emit EvidenceAccessRecorded(
            evidenceRef, officerRef, accessSessionRef, uint64(block.timestamp), writer
        );

        vm.prank(writer);
        registry.recordAccess(evidenceRef, officerRef, accessSessionRef);

        (bytes32 storedEvidence, bytes32 storedOfficer, uint64 recordedAt, address storedWriter) =
            registry.getAccessBySession(accessSessionRef);
        assertEq(storedEvidence, evidenceRef);
        assertEq(storedOfficer, officerRef);
        assertEq(recordedAt, uint64(block.timestamp));
        assertEq(storedWriter, writer);
        assertTrue(registry.accessSessionExists(accessSessionRef));
    }

    function testRejectsAccessForMissingEvidence() public {
        bytes32 accessSessionRef = keccak256("session");
        vm.prank(writer);
        vm.expectRevert(
            abi.encodeWithSelector(IEvidenceRegistry.EvidenceNotFound.selector, evidenceRef)
        );
        registry.recordAccess(evidenceRef, keccak256("officer"), accessSessionRef);
    }

    function testRejectsDuplicateAccessSession() public {
        bytes32 accessSessionRef = keccak256("session");
        vm.startPrank(writer);
        registry.recordEvidence(evidenceRef, staticHash);
        registry.recordAccess(evidenceRef, keccak256("officer"), accessSessionRef);
        vm.expectRevert(
            abi.encodeWithSelector(
                IEvidenceRegistry.AccessSessionAlreadyExists.selector, accessSessionRef
            )
        );
        registry.recordAccess(evidenceRef, keccak256("officer-2"), accessSessionRef);
        vm.stopPrank();
    }
}
