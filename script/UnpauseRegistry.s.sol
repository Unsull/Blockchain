// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import { Script } from "forge-std/Script.sol";
import { EvidenceRegistryV3 } from "../contracts/EvidenceRegistryV3.sol";

contract UnpauseRegistry is Script {
    function run() external {
        EvidenceRegistryV3 registry = EvidenceRegistryV3(vm.envAddress("CONTRACT_ADDRESS"));
        uint256 pauserPrivateKey = vm.envUint("PAUSER_PRIVATE_KEY");
        uint256 expectedChainId = vm.envUint("CHAIN_ID");

        require(block.chainid == expectedChainId, "Invalid chain ID");
        require(address(registry).code.length > 0, "Contract not deployed");

        vm.startBroadcast(pauserPrivateKey);
        registry.unpause();
        vm.stopBroadcast();
    }
}
