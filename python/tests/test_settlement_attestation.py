"""Tests for algovoi-settlement-attestation."""

from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path

import pytest

from algovoi_substrate.canonicalize import CANON_VERSION, canonicalize, sha256_jcs
from algovoi_settlement_attestation import (
    SETTLEMENT_RESULTS,
    SettlementAttestationError,
    build_settlement_attestation,
)


class TestSettlementResults:
    def test_only_settled_pending_reversed(self) -> None:
        assert SETTLEMENT_RESULTS == frozenset(
            {"SETTLED", "PENDING_FINALITY", "REVERSED"}
        )


class TestBuildSettlementAttestation:
    def test_builds_canonical_attestation(self) -> None:
        a = build_settlement_attestation(
            settled_payment_ref="sha256:abc123",
            settlement_result="SETTLED",
            settlement_timestamp_ms=1716460800000,
            settlement_provider_did="did:web:api.algovoi.co.uk",
            settlement_amount={"amount_minor": "100000", "asset_id": "USDC.6"},
            settlement_chain="ethereum:8453",
            jurisdiction_flags=["UK", "EU"],
        )
        assert a["settled_payment_ref"] == "sha256:abc123"
        assert a["settlement_result"] == "SETTLED"
        assert a["settlement_timestamp_ms"] == 1716460800000
        assert a["settlement_chain"] == "ethereum:8453"
        assert a["canon_version"] == CANON_VERSION

    def test_distinct_result_distinct_hashes(self) -> None:
        common = dict(
            settled_payment_ref="sha256:x",
            settlement_timestamp_ms=1716460800000,
            settlement_provider_did="did:web:x",
            settlement_amount={"amount_minor": "100000", "asset_id": "USDC.6"},
            settlement_chain="ethereum:8453",
            jurisdiction_flags=["UK"],
        )
        settled = build_settlement_attestation(settlement_result="SETTLED", **common)
        pending = build_settlement_attestation(
            settlement_result="PENDING_FINALITY", **common
        )
        reversed_a = build_settlement_attestation(
            settlement_result="REVERSED", **common
        )
        h_s = sha256_jcs(dict(settled))
        h_p = sha256_jcs(dict(pending))
        h_r = sha256_jcs(dict(reversed_a))
        assert h_s != h_p
        assert h_s != h_r
        assert h_p != h_r

    def test_distinct_chain_distinct_hashes(self) -> None:
        common = dict(
            settled_payment_ref="sha256:x",
            settlement_result="SETTLED",
            settlement_timestamp_ms=1716460800000,
            settlement_provider_did="did:web:x",
            settlement_amount={"amount_minor": "100000", "asset_id": "USDC.6"},
            jurisdiction_flags=["UK"],
        )
        base = build_settlement_attestation(settlement_chain="ethereum:8453", **common)
        solana = build_settlement_attestation(settlement_chain="solana", **common)
        assert sha256_jcs(dict(base)) != sha256_jcs(dict(solana))

    def test_rejects_invalid_result(self) -> None:
        with pytest.raises(
            SettlementAttestationError, match="settlement_result must be one of"
        ):
            build_settlement_attestation(
                settled_payment_ref="sha256:x",
                settlement_result="FINALIZED",
                settlement_timestamp_ms=0,
                settlement_provider_did="did:web:x",
                settlement_amount={"amount_minor": "1", "asset_id": "USDC.6"},
                settlement_chain="ethereum:8453",
                jurisdiction_flags=["UK"],
            )

    def test_rejects_float_timestamp(self) -> None:
        with pytest.raises(SettlementAttestationError, match="Substrate Rule 2"):
            build_settlement_attestation(
                settled_payment_ref="sha256:x",
                settlement_result="SETTLED",
                settlement_timestamp_ms=1716460800000.5,  # type: ignore[arg-type]
                settlement_provider_did="did:web:x",
                settlement_amount={"amount_minor": "1", "asset_id": "USDC.6"},
                settlement_chain="ethereum:8453",
                jurisdiction_flags=["UK"],
            )

    def test_rejects_string_timestamp(self) -> None:
        with pytest.raises(SettlementAttestationError, match="Substrate Rule 2"):
            build_settlement_attestation(
                settled_payment_ref="sha256:x",
                settlement_result="SETTLED",
                settlement_timestamp_ms="2024-05-23T12:00:00Z",  # type: ignore[arg-type]
                settlement_provider_did="did:web:x",
                settlement_amount={"amount_minor": "1", "asset_id": "USDC.6"},
                settlement_chain="ethereum:8453",
                jurisdiction_flags=["UK"],
            )

    def test_rejects_empty_chain(self) -> None:
        with pytest.raises(SettlementAttestationError, match="settlement_chain"):
            build_settlement_attestation(
                settled_payment_ref="sha256:x",
                settlement_result="SETTLED",
                settlement_timestamp_ms=0,
                settlement_provider_did="did:web:x",
                settlement_amount={"amount_minor": "1", "asset_id": "USDC.6"},
                settlement_chain="",
                jurisdiction_flags=["UK"],
            )

    def test_canon_version_default(self) -> None:
        a = build_settlement_attestation(
            settled_payment_ref="sha256:x",
            settlement_result="REVERSED",
            settlement_timestamp_ms=0,
            settlement_provider_did="did:web:x",
            settlement_amount={"amount_minor": "1", "asset_id": "USDC.6"},
            settlement_chain="solana",
            jurisdiction_flags=["UK"],
        )
        assert a["canon_version"] == "jcs-rfc8785-v1"


class TestConformanceVectorReproduction:
    VECTOR_PATH = Path(
        "C:/algo/algovoi-jcs-conformance-vectors/vectors/settlement_attestation_v1/settlement_attestation_v1.json"
    )

    def test_vectors_001_to_005_reproduce(self) -> None:
        if not self.VECTOR_PATH.exists():
            pytest.skip("conformance vectors not co-located")
        data = json.loads(self.VECTOR_PATH.read_text(encoding="utf-8"))
        for v in data["vectors"]:
            if "receipt" not in v:
                continue
            canon = canonicalize(v["receipt"])
            canon_bytes = canon.encode("utf-8") if isinstance(canon, str) else canon
            assert (
                base64.b64encode(canon_bytes).decode("ascii")
                == v["expected_jcs_bytes_b64"]
            ), f"{v['vector_id']}: JCS bytes mismatch"
            assert (
                hashlib.sha256(canon_bytes).hexdigest() == v["expected_content_hash"]
            ), f"{v['vector_id']}: content_hash mismatch"
