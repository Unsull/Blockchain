// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import {Test} from "forge-std/Test.sol";
import {EvidenceRegistry} from "../contracts/EvidenceRegistry.sol";
import {IEvidenceRegistry} from "../contracts/interfaces/IEvidenceRegistry.sol";

contract EvidenceRegistryFuzzTest is Test {
    EvidenceRegistry internal registry;
    address internal admin = address(0xA11CE);
    address internal writer = address(0xB0B);

    function setUp() public {
        registry = new EvidenceRegistry(admin);
        vm.prank(admin);
        registry.grantRole(registry.WRITER_ROLE(), writer);
    }

    function testFuzzRecordEvidence(bytes32 evidenceRef, bytes32 staticHash) public {
        vm.assume(evidenceRef != bytes32(0));
        vm.assume(staticHash != bytes32(0));

        vm.prank(writer);
        registry.recordEvidence(evidenceRef, staticHash);

        (bytes32 storedHash,, address storedWriter, bool exists) = registry.getEvidence(evidenceRef);
        assertEq(storedHash, staticHash);
        assertEq(storedWriter, writer);
        assertTrue(exists);
    }

    function testFuzzRecordAccess(
        bytes32 evidenceRef,
        bytes32 staticHash,
        bytes32 officerRef,
        bytes32 accessSessionRef
    ) public {
        vm.assume(evidenceRef != bytes32(0));
        vm.assume(staticHash != bytes32(0));
        vm.assume(officerRef != bytes32(0));
        vm.assume(accessSessionRef != bytes32(0));

        vm.startPrank(writer);
        registry.recordEvidence(evidenceRef, staticHash);
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
        registry.recordEvidence(bytes32(0), nonZero);

        vm.expectRevert(IEvidenceRegistry.InvalidStaticHash.selector);
        registry.recordEvidence(nonZero, bytes32(0));
        vm.stopPrank();
    }
}
