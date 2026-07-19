// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import { Script } from "forge-std/Script.sol";
import { EvidenceRegistry } from "../contracts/EvidenceRegistry.sol";

contract DeployEvidenceRegistry is Script {
    function run() external returns (EvidenceRegistry registry) {
        address admin = vm.envAddress("REGISTRY_ADMIN_ADDRESS");
        uint256 deployerPrivateKey = vm.envUint("DEPLOYER_PRIVATE_KEY");

        vm.startBroadcast(deployerPrivateKey);
        registry = new EvidenceRegistry(admin);
        vm.stopBroadcast();
    }
}
