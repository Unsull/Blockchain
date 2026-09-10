// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import { Script } from "forge-std/Script.sol";
import { EvidenceRegistryV3 } from "../contracts/EvidenceRegistryV3.sol";

contract DeployEvidenceRegistryV3 is Script {
    function run() external returns (EvidenceRegistryV3 registry) {
        address admin = vm.envAddress("REGISTRY_ADMIN_ADDRESS");
        uint256 deployerPrivateKey = vm.envUint("DEPLOYER_PRIVATE_KEY");
        uint256 expectedChainId = vm.envUint("CHAIN_ID");

        require(block.chainid == expectedChainId, "Invalid chain ID");
        require(admin != address(0), "Admin cannot be zero address");

        vm.startBroadcast(deployerPrivateKey);
        registry = new EvidenceRegistryV3(admin);
        vm.stopBroadcast();
    }
}
