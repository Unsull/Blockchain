// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import {Test} from "forge-std/Test.sol";
import {EvidenceRegistry} from "../contracts/EvidenceRegistry.sol";

contract EvidenceRegistryAccessControlTest is Test {
    EvidenceRegistry internal registry;
    address internal admin = address(0xA11CE);
    address internal writer = address(0xB0B);
    address internal pauser = address(0xCAFE);
    bytes32 internal evidenceRef = keccak256("evidence");
    bytes32 internal staticHash = keccak256("static");

    function setUp() public {
        registry = new EvidenceRegistry(admin);
    }

    function testAdminCanGrantAndRevokeWriter() public {
        vm.prank(admin);
        registry.grantRole(registry.WRITER_ROLE(), writer);
        assertTrue(registry.hasRole(registry.WRITER_ROLE(), writer));

        vm.prank(admin);
        registry.revokeRole(registry.WRITER_ROLE(), writer);
        assertFalse(registry.hasRole(registry.WRITER_ROLE(), writer));
    }

    function testNonAdminCannotGrantRole() public {
        vm.prank(writer);
        vm.expectRevert();
        registry.grantRole(registry.WRITER_ROLE(), writer);
    }

    function testRevokedWriterCannotWrite() public {
        vm.startPrank(admin);
        registry.grantRole(registry.WRITER_ROLE(), writer);
        registry.revokeRole(registry.WRITER_ROLE(), writer);
        vm.stopPrank();

        vm.prank(writer);
        vm.expectRevert();
        registry.recordEvidence(evidenceRef, staticHash);
    }

    function testPauserCanPauseAndUnpause() public {
        vm.prank(admin);
        registry.grantRole(registry.PAUSER_ROLE(), pauser);

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
        vm.startPrank(admin);
        registry.grantRole(registry.WRITER_ROLE(), writer);
        registry.pause();
        vm.stopPrank();

        vm.prank(writer);
        vm.expectRevert();
        registry.recordEvidence(evidenceRef, staticHash);
    }
}
