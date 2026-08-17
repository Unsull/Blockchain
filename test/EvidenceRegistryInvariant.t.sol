// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import { Test } from "forge-std/Test.sol";
import { EvidenceRegistry } from "../contracts/EvidenceRegistry.sol";

contract EvidenceRegistryInvariantTest is Test {
    EvidenceRegistry internal registry;
    address internal admin = address(0xA11CE);
    address internal writer = address(0xB0B);
    bytes32 internal evidenceRef = keccak256("evidence");
    bytes32 internal evidenceHash = keccak256("evidence-hash");
    bytes32 internal uploaderRef = keccak256("uploader");
    bytes32 internal accessSessionRef = keccak256("session");

    function setUp() public {
        registry = new EvidenceRegistry(admin);
        bytes32 writerRole = registry.WRITER_ROLE();
        vm.prank(admin);
        registry.grantRole(writerRole, writer);

        vm.startPrank(writer);
        registry.recordEvidence(evidenceRef, evidenceHash, uploaderRef);
        registry.recordAccess(evidenceRef, keccak256("officer"), accessSessionRef);
        vm.stopPrank();
    }

    function invariantEvidenceHashAndUploaderAreImmutable() public view {
        (bytes32 storedHash, bytes32 storedUploader,,, bool exists) =
            registry.getEvidence(evidenceRef);
        assertTrue(exists);
        assertEq(storedHash, evidenceHash);
        assertEq(storedUploader, uploaderRef);
    }

    function invariantAccessSessionMapsToOneRecord() public view {
        (bytes32 storedEvidence, bytes32 storedOfficer,, address storedWriter) =
            registry.getAccessBySession(accessSessionRef);
        assertEq(storedEvidence, evidenceRef);
        assertEq(storedOfficer, keccak256("officer"));
        assertEq(storedWriter, writer);
    }
}
