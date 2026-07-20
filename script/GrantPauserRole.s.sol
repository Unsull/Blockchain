// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import { Script } from "forge-std/Script.sol";
import { EvidenceRegistry } from "../contracts/EvidenceRegistry.sol";

contract GrantPauserRole is Script {
    function run() external {
        EvidenceRegistry registry = EvidenceRegistry(vm.envAddress("CONTRACT_ADDRESS"));
        address pauser = vm.envAddress("PAUSER_ADDRESS");
        uint256 adminPrivateKey = vm.envUint("ADMIN_PRIVATE_KEY");
        uint256 expectedChainId = vm.envUint("CHAIN_ID");

        require(block.chainid == expectedChainId, "Invalid chain ID");
        require(address(registry).code.length > 0, "Contract not deployed");
        require(pauser != address(0), "Pauser cannot be zero address");

        vm.startBroadcast(adminPrivateKey);
        registry.grantRole(registry.PAUSER_ROLE(), pauser);
        vm.stopBroadcast();
    }
}
