// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import { Test } from "forge-std/Test.sol";
import { EvidenceRegistry } from "../contracts/EvidenceRegistry.sol";
import { IEvidenceRegistry } from "../contracts/interfaces/IEvidenceRegistry.sol";

contract EvidenceRegistryFuzzTest is Test {
    EvidenceRegistry internal registry;
    address internal admin = address(0xA11CE);
    address internal writer = address(0xB0B);

    function setUp() public {
        registry = new EvidenceRegistry(admin);
        bytes32 writerRole = registry.WRITER_ROLE();
        vm.prank(admin);
        registry.grantRole(writerRole, writer);
    }

    function testFuzzRecordEvidence(bytes32 evidenceRef, bytes32 evidenceHash, bytes32 uploaderRef)
        public
    {
        vm.assume(evidenceRef != bytes32(0));
        vm.assume(evidenceHash != bytes32(0));
        vm.assume(uploaderRef != bytes32(0));

        vm.prank(writer);
        registry.recordEvidence(evidenceRef, evidenceHash, uploaderRef);

        (bytes32 storedHash, bytes32 storedUploader,, address storedWriter, bool exists) =
            registry.getEvidence(evidenceRef);
        assertEq(storedHash, evidenceHash);
        assertEq(storedUploader, uploaderRef);
        assertEq(storedWriter, writer);
        assertTrue(exists);
    }

    function testFuzzRecordAccess(
        bytes32 evidenceRef,
        bytes32 evidenceHash,
        bytes32 uploaderRef,
        bytes32 officerRef,
        bytes32 accessSessionRef
    ) public {
        vm.assume(evidenceRef != bytes32(0));
        vm.assume(evidenceHash != bytes32(0));
        vm.assume(uploaderRef != bytes32(0));
        vm.assume(officerRef != bytes32(0));
        vm.assume(accessSessionRef != bytes32(0));

        vm.startPrank(writer);
        registry.recordEvidence(evidenceRef, evidenceHash, uploaderRef);
        registry.recordAccess(evidenceRef, officerRef, accessSessionRef);
        vm.stopPrank();

        (bytes32 storedEvidence, bytes32 storedOfficer,, address storedWriter) =
            registry.getAccessBySession(accessSessionRef);
        assertEq(storedEvidence, evidenceRef);
        assertEq(storedOfficer, officerRef);
        assertEq(storedWriter, writer);
    }

    function testFuzzRejectsZeroValues(bytes32 nonZero) public {
        vm.assume(nonZero != bytes32(0));

        vm.startPrank(writer);
        vm.expectRevert(IEvidenceRegistry.InvalidEvidenceRef.selector);
        registry.recordEvidence(bytes32(0), nonZero, nonZero);

        vm.expectRevert(IEvidenceRegistry.InvalidEvidenceHash.selector);
        registry.recordEvidence(nonZero, bytes32(0), nonZero);

        vm.expectRevert(IEvidenceRegistry.InvalidUploaderRef.selector);
        registry.recordEvidence(nonZero, nonZero, bytes32(0));
        vm.stopPrank();
    }
}
