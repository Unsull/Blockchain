import json
import time
from typing import Any

from web3 import Web3

from config import CONTRACT_ADDRESS, WEB3_PROVIDER_URI


ABI_JSON = """
[
  {
    "anonymous": false,
    "inputs": [
      {"indexed": false, "internalType": "string", "name": "evidenceId", "type": "string"},
      {"indexed": false, "internalType": "string", "name": "accessHash", "type": "string"},
      {"indexed": false, "internalType": "string", "name": "accessSessionId", "type": "string"},
      {"indexed": false, "internalType": "uint256", "name": "timestamp", "type": "uint256"}
    ],
    "name": "AccessRecorded",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {"indexed": false, "internalType": "string", "name": "evidenceId", "type": "string"},
      {"indexed": false, "internalType": "string", "name": "watermarkHash", "type": "string"},
      {"indexed": false, "internalType": "uint256", "name": "timestamp", "type": "uint256"}
    ],
    "name": "EvidenceStored",
    "type": "event"
  },
  {
    "inputs": [
      {"internalType": "string", "name": "_evidenceId", "type": "string"}
    ],
    "name": "getAccessLogs",
    "outputs": [
      {
        "components": [
          {"internalType": "string", "name": "accessHash", "type": "string"},
          {"internalType": "string", "name": "accessSessionId", "type": "string"},
          {"internalType": "uint256", "name": "timestamp", "type": "uint256"}
        ],
        "internalType": "struct EvidenceWatermarkRegistry.AccessLog[]",
        "name": "",
        "type": "tuple[]"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {"internalType": "string", "name": "_evidenceId", "type": "string"}
    ],
    "name": "getEvidenceData",
    "outputs": [
      {"internalType": "string", "name": "", "type": "string"},
      {"internalType": "uint256", "name": "", "type": "uint256"},
      {"internalType": "bool", "name": "", "type": "bool"}
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {"internalType": "string", "name": "_evidenceId", "type": "string"},
      {"internalType": "string", "name": "_accessHash", "type": "string"},
      {"internalType": "string", "name": "_accessSessionId", "type": "string"}
    ],
    "name": "recordAccess",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {"internalType": "string", "name": "_evidenceId", "type": "string"},
      {"internalType": "string", "name": "_watermarkHash", "type": "string"}
    ],
    "name": "recordEvidence",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  }
]
"""

w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URI))
contract_abi = json.loads(ABI_JSON)


def _get_contract():
    if not w3.is_connected():
        raise ConnectionError("Web3 provider is not connected.")
    if not CONTRACT_ADDRESS:
        raise ValueError("CONTRACT_ADDRESS is not configured.")
    return w3.eth.contract(
        address=w3.to_checksum_address(CONTRACT_ADDRESS),
        abi=contract_abi,
    )


def _get_main_account() -> str:
    accounts = w3.eth.accounts
    if not accounts:
        raise ConnectionError("No unlocked Web3 account is available.")
    return accounts[0]


def _wait_for_success(tx_hash: Any):
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status != 1:
        raise RuntimeError("Blockchain transaction failed.")
    return receipt


def store_watermark_evidence(evidence_id: str, watermark_hash: str) -> str | None:
    try:
        contract = _get_contract()
        account = _get_main_account()
        tx_hash = contract.functions.recordEvidence(
            evidence_id,
            watermark_hash,
        ).transact({"from": account})
        receipt = _wait_for_success(tx_hash)
        return receipt.transactionHash.hex()
    except Exception as e:
        print(f"Error storing evidence on blockchain: {e}")
        return None


def get_evidence_details(evidence_id: str) -> dict | None:
    try:
        result = _get_contract().functions.getEvidenceData(evidence_id).call()
        record_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(result[1]))
        return {
            "watermark_hash": result[0],
            "timestamp": record_time,
            "is_recorded": result[2],
        }
    except Exception as e:
        print(f"Error fetching evidence details: {e}")
        return None


def log_access_to_blockchain(
    evidence_id: str,
    access_hash: str,
    access_session_id: str,
) -> str | None:
    try:
        contract = _get_contract()
        account = _get_main_account()
        tx_hash = contract.functions.recordAccess(
            evidence_id,
            access_hash,
            access_session_id,
        ).transact({"from": account})
        receipt = _wait_for_success(tx_hash)
        return receipt.transactionHash.hex()
    except Exception as e:
        print(f"Error logging access on blockchain: {e}")
        return None


def fetch_access_logs(evidence_id: str) -> list:
    try:
        return _get_contract().functions.getAccessLogs(evidence_id).call()
    except Exception as e:
        print(f"Error fetching logs: {e}")
        return []


if __name__ == "__main__":
    test_evidence_id = "EVD-2026-256"
    test_watermark_hash = "sha256_dummy_hash_abcdef1234567890"
    print(store_watermark_evidence(test_evidence_id, test_watermark_hash))
    print(get_evidence_details(test_evidence_id))
