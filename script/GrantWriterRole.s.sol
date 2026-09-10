// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import { Script } from "forge-std/Script.sol";
import { EvidenceRegistryV3 } from "../contracts/EvidenceRegistryV3.sol";

contract GrantWriterRole is Script {
    function run() external {
        EvidenceRegistryV3 registry = EvidenceRegistryV3(vm.envAddress("CONTRACT_ADDRESS"));
        address writer = vm.envAddress("WRITER_ADDRESS");
        uint256 adminPrivateKey = vm.envUint("ADMIN_PRIVATE_KEY");
        uint256 expectedChainId = vm.envUint("CHAIN_ID");

        require(block.chainid == expectedChainId, "Invalid chain ID");
        require(address(registry).code.length > 0, "Contract not deployed");
        require(writer != address(0), "Writer cannot be zero address");

        vm.startBroadcast(adminPrivateKey);
        registry.grantRole(registry.WRITER_ROLE(), writer);
        vm.stopBroadcast();
    }
}
