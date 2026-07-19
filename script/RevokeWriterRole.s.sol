// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import { Script } from "forge-std/Script.sol";
import { EvidenceRegistry } from "../contracts/EvidenceRegistry.sol";

contract RevokeWriterRole is Script {
    function run() external {
        EvidenceRegistry registry = EvidenceRegistry(vm.envAddress("CONTRACT_ADDRESS"));
        address writer = vm.envAddress("WRITER_ADDRESS");
        uint256 adminPrivateKey = vm.envUint("ADMIN_PRIVATE_KEY");

        vm.startBroadcast(adminPrivateKey);
        registry.revokeRole(registry.WRITER_ROLE(), writer);
        vm.stopBroadcast();
    }
}
