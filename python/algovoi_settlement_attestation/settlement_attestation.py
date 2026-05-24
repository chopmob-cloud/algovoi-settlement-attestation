"""
Settlement attestation shape -- multi-chain categorical attestation
under the JCS RFC 8785 canonicalisation discipline.

Specified in IETF Internet-Draft
`draft-hopley-x402-settlement-attestation-00` (Independent Submission,
Informational; AlgoVoi-authored).

The categorical outcome (SETTLED / PENDING_FINALITY / REVERSED) is
load-bearing for downstream regulatory obligations:

- SETTLED triggers settlement-finality records under MiCA Article 80
  and AMLR Article 56; PSD2 Article 89 refund-window clock starts.
- PENDING_FINALITY records inclusion-without-finality state; refund
  obligations differ from SETTLED.
- REVERSED records chain-reorganisation / fraud-reversal /
  operator-initiated reversal events for chain-of-custody audit.

Composes with compliance_receipt_v1 (via settled_payment_ref) and
refund_receipt_v1 (a refund receipt's original_payment_ref MAY equal
a settlement attestation content_hash).

Shape (8 fields, sorted lexicographically by JCS during
canonicalisation):
- canon_version: "jcs-rfc8785-v1"
- jurisdiction_flags: ordered list of jurisdiction codes
- settled_payment_ref: "sha256:<hex>"
- settlement_amount: {"amount_minor": str, "asset_id": str}
- settlement_chain: chain identifier string (e.g. "ethereum:8453")
- settlement_provider_did: DID URI of the attesting party
- settlement_result: SETTLED | PENDING_FINALITY | REVERSED
- settlement_timestamp_ms: integer (Substrate Rule 2)
"""

from __future__ import annotations

from typing import TypedDict

from algovoi_substrate.canonicalize import CANON_VERSION

SETTLEMENT_RESULTS = frozenset({"SETTLED", "PENDING_FINALITY", "REVERSED"})


class SettlementAttestationError(ValueError):
    """Raised when settlement attestation inputs violate the substrate discipline."""


class SettlementAmount(TypedDict):
    amount_minor: str
    asset_id: str


class SettlementAttestation(TypedDict):
    canon_version: str
    jurisdiction_flags: list[str]
    settled_payment_ref: str
    settlement_amount: SettlementAmount
    settlement_chain: str
    settlement_provider_did: str
    settlement_result: str
    settlement_timestamp_ms: int


def _require_str(field: str, value: object) -> str:
    if not isinstance(value, str) or not value:
        raise SettlementAttestationError(f"{field} must be a non-empty string")
    return value


def _require_int_timestamp_ms(value: object) -> int:
    if isinstance(value, bool):
        raise SettlementAttestationError(
            "settlement_timestamp_ms must be int, got bool"
        )
    if not isinstance(value, int):
        raise SettlementAttestationError(
            f"settlement_timestamp_ms must be epoch-millisecond integer "
            f"(Substrate Rule 2), got {type(value).__name__}"
        )
    if value < 0:
        raise SettlementAttestationError(
            f"settlement_timestamp_ms must be non-negative, got {value}"
        )
    return value


def _require_jurisdiction_flags(value: object) -> list[str]:
    if not isinstance(value, list):
        raise SettlementAttestationError(
            f"jurisdiction_flags must be list, got {type(value).__name__}"
        )
    for i, code in enumerate(value):
        if not isinstance(code, str) or not code:
            raise SettlementAttestationError(
                f"jurisdiction_flags[{i}] must be a non-empty string"
            )
    return list(value)


def _require_settlement_amount(value: object) -> SettlementAmount:
    if not isinstance(value, dict):
        raise SettlementAttestationError(
            f"settlement_amount must be dict, got {type(value).__name__}"
        )
    expected_keys = {"amount_minor", "asset_id"}
    if set(value.keys()) != expected_keys:
        raise SettlementAttestationError(
            f"settlement_amount must have exactly the keys {sorted(expected_keys)}, "
            f"got {sorted(value.keys())}"
        )
    amount_minor = value["amount_minor"]
    asset_id = value["asset_id"]
    if not isinstance(amount_minor, str) or not amount_minor:
        raise SettlementAttestationError(
            "settlement_amount.amount_minor must be a non-empty string "
            "(decimal digits in the asset's minor unit)"
        )
    if not amount_minor.isdigit():
        raise SettlementAttestationError(
            f"settlement_amount.amount_minor must be decimal digits only, "
            f"got {amount_minor!r}"
        )
    if not isinstance(asset_id, str) or not asset_id:
        raise SettlementAttestationError(
            "settlement_amount.asset_id must be a non-empty string"
        )
    return SettlementAmount(amount_minor=amount_minor, asset_id=asset_id)


def build_settlement_attestation(
    *,
    settled_payment_ref: str,
    settlement_result: str,
    settlement_timestamp_ms: int,
    settlement_provider_did: str,
    settlement_amount: SettlementAmount,
    settlement_chain: str,
    jurisdiction_flags: list[str],
    canon_version: str = CANON_VERSION,
) -> SettlementAttestation:
    """Build a validated settlement attestation object.

    settlement_result MUST be one of SETTLED, PENDING_FINALITY, REVERSED.

    settled_payment_ref is a content-addressed reference to the
    original payment record (e.g. compliance receipt content_hash).

    settlement_chain identifies the chain on which settlement occurred.
    Convention: <chain_family> for default mainnet
    (e.g. "algo", "solana", "stellar", "hedera", "base"); or
    <chain_family>:<network> for non-default (e.g. "ethereum:8453"
    for Base by chainId, "algorand:testnet").

    settlement_amount.amount_minor is a decimal-digit string in the
    asset's minor unit. May differ from the original payment amount in
    cross-asset substitution cases.

    jurisdiction_flags is treated as ordered; ["UK","EU"] and ["EU","UK"]
    produce distinct canonical bytes per RFC 8785 §3.2.3.

    settlement_timestamp_ms MUST be integer (Substrate Rule 2).
    """
    if settlement_result not in SETTLEMENT_RESULTS:
        raise SettlementAttestationError(
            f"settlement_result must be one of {sorted(SETTLEMENT_RESULTS)}, "
            f"got {settlement_result!r}"
        )

    return SettlementAttestation(
        canon_version=_require_str("canon_version", canon_version),
        jurisdiction_flags=_require_jurisdiction_flags(jurisdiction_flags),
        settled_payment_ref=_require_str("settled_payment_ref", settled_payment_ref),
        settlement_amount=_require_settlement_amount(settlement_amount),
        settlement_chain=_require_str("settlement_chain", settlement_chain),
        settlement_provider_did=_require_str(
            "settlement_provider_did", settlement_provider_did
        ),
        settlement_result=settlement_result,
        settlement_timestamp_ms=_require_int_timestamp_ms(settlement_timestamp_ms),
    )
