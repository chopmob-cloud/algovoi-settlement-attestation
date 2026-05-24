"""
algovoi-settlement-attestation -- AlgoVoi settlement attestation reference implementation.

Multi-chain categorical settlement attestation under the JCS RFC 8785
canonicalisation discipline (urn:x402:canonicalisation:jcs-rfc8785-v1).
Companion to algovoi-substrate compliance receipts and the
algovoi-refund-receipt format.

Specified in IETF Internet-Draft draft-hopley-x402-settlement-attestation-00
(Independent Submission, Informational; AlgoVoi-authored).

The categorical outcome (SETTLED / PENDING_FINALITY / REVERSED) is
load-bearing under MiCA Art. 80, AMLR Art. 56 record-keeping
obligations and PSD2 Article 89 refund-window timing.

Composes with compliance_receipt_v1 via settled_payment_ref linkage
and with refund_receipt_v1 via the chain-of-custody pattern (a refund
receipt's original_payment_ref may equal a settlement attestation
content_hash).

Licensed under Apache 2.0.
"""

from algovoi_settlement_attestation.settlement_attestation import (
    SETTLEMENT_RESULTS,
    SettlementAmount,
    SettlementAttestation,
    SettlementAttestationError,
    build_settlement_attestation,
)

__all__ = [
    "SETTLEMENT_RESULTS",
    "SettlementAmount",
    "SettlementAttestation",
    "SettlementAttestationError",
    "build_settlement_attestation",
]

__version__ = "0.1.0"
