// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import { Test } from "forge-std/Test.sol";
import { EvidenceRegistry } from "../contracts/EvidenceRegistry.sol";

contract EvidenceRegistryAccessControlTest is Test {
    EvidenceRegistry internal registry;
    address internal admin = address(0xA11CE);
    address internal writer = address(0xB0B);
    address internal pauser = address(0xCAFE);
    bytes32 internal evidenceRef = keccak256("evidence");
    bytes32 internal evidenceHash = keccak256("evidence-hash");
    bytes32 internal uploaderRef = keccak256("uploader");

    function setUp() public {
        registry = new EvidenceRegistry(admin);
    }

    function testAdminCanGrantAndRevokeWriter() public {
        bytes32 writerRole = registry.WRITER_ROLE();
        vm.prank(admin);
        registry.grantRole(writerRole, writer);
        assertTrue(registry.hasRole(writerRole, writer));

        vm.prank(admin);
        registry.revokeRole(writerRole, writer);
        assertFalse(registry.hasRole(writerRole, writer));
    }

    function testNonAdminCannotGrantRole() public {
        bytes32 writerRole = registry.WRITER_ROLE();
        vm.prank(writer);
        vm.expectRevert();
        registry.grantRole(writerRole, writer);
    }

    function testRevokedWriterCannotWrite() public {
        bytes32 writerRole = registry.WRITER_ROLE();
        vm.startPrank(admin);
        registry.grantRole(writerRole, writer);
        registry.revokeRole(writerRole, writer);
        vm.stopPrank();

        vm.prank(writer);
        vm.expectRevert();
        registry.recordEvidence(evidenceRef, evidenceHash, uploaderRef);
    }

    function testPauserCanPauseAndUnpause() public {
        bytes32 pauserRole = registry.PAUSER_ROLE();
        vm.prank(admin);
        registry.grantRole(pauserRole, pauser);

        vm.prank(pauser);
        registry.pause();
        assertTrue(registry.paused());

        vm.prank(pauser);
        registry.unpause();
        assertFalse(registry.paused());
    }

    function testUnauthorizedAddressCannotPause() public {
        vm.prank(writer);
        vm.expectRevert();
        registry.pause();
    }

    function testPausedContractRejectsWrites() public {
        bytes32 writerRole = registry.WRITER_ROLE();
        vm.startPrank(admin);
        registry.grantRole(writerRole, writer);
        registry.pause();
        vm.stopPrank();

        vm.prank(writer);
        vm.expectRevert();
        registry.recordEvidence(evidenceRef, evidenceHash, uploaderRef);
    }
}
