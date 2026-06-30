import time

from web3.exceptions import TransactionNotFound

from blockchain_service import _get_contract, w3


def _normalize_tx_hash(tx_hash: str) -> str:
    normalized = tx_hash.strip()
    if not normalized.startswith("0x"):
        normalized = f"0x{normalized}"
    if len(normalized) != 66:
        raise ValueError("tx_hash must be a 32-byte hex transaction hash.")
    int(normalized[2:], 16)
    return normalized


def trace_officer_from_watermark(tx_hash: str):
    """
    Trace a dynamic watermark transaction to blockchain audit references only.

    TODO: Resolve access_session_id to officer_id from the backend database/proxy
    table. Officer identity is intentionally not stored or decrypted from chain.
    """
    try:
        normalized_hash = _normalize_tx_hash(tx_hash)
        contract = _get_contract()
        tx = w3.eth.get_transaction(normalized_hash)
        receipt = w3.eth.get_transaction_receipt(normalized_hash)

        if receipt.status != 1:
            return {
                "status": "error",
                "message": "Transaction receipt indicates a failed transaction.",
            }

        func_obj, func_params = contract.decode_function_input(tx.input)
        if func_obj.fn_name != "recordAccess":
            return {
                "status": "error",
                "message": f"Transaction calls {func_obj.fn_name}, not recordAccess.",
            }

        block = w3.eth.get_block(tx.blockNumber)
        block_timestamp = time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime(block.timestamp),
        )

        return {
            "status": "verified",
            "evidence_id": func_params["_evidenceId"],
            "access_hash": func_params["_accessHash"],
            "access_session_id": func_params["_accessSessionId"],
            "tx_hash": normalized_hash,
            "block_number": tx.blockNumber,
            "block_timestamp": block_timestamp,
        }
    except TransactionNotFound:
        return {"status": "error", "message": "Transaction not found."}
    except ValueError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"Unable to trace transaction: {e}"}


if __name__ == "__main__":
    test_hash = "0x0000000000000000000000000000000000000000000000000000000000000000"
    print(trace_officer_from_watermark(test_hash))
