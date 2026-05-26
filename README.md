# algovoi-settlement-attestation

[![PyPI](https://img.shields.io/pypi/v/algovoi-settlement-attestation?label=PyPI)](https://pypi.org/project/algovoi-settlement-attestation/)
[![npm](https://img.shields.io/npm/v/@algovoi/settlement-attestation?label=npm)](https://www.npmjs.com/package/@algovoi/settlement-attestation)
[![Apache 2.0](https://img.shields.io/badge/license-Apache--2.0-green)](./LICENSE)
[![IETF I-D](https://img.shields.io/badge/companion%20IETF%20I--D-draft--hopley--x402--settlement--attestation--00-blue)](https://datatracker.ietf.org/doc/draft-hopley-x402-settlement-attestation/)

AlgoVoi-authored reference implementation for the settlement attestation
format specified in IETF Internet-Draft
[`draft-hopley-x402-settlement-attestation-00`](https://datatracker.ietf.org/doc/draft-hopley-x402-settlement-attestation/)
(Independent Submission, Informational).

Multi-chain categorical attestation under the JCS RFC 8785
canonicalisation discipline
([`urn:x402:canonicalisation:jcs-rfc8785-v1`](https://datatracker.ietf.org/doc/draft-hopley-x402-canonicalisation-jcs-v1/)).
Companion to the AlgoVoi compliance receipt and refund receipt I-Ds —
closes the lifecycle gap between admission and refund.

Python and TypeScript reference implementations, byte-for-byte parity,
Apache 2.0.

## Lifecycle position

```
admission         settlement        refund
compliance   -->  settlement   -->  refund
receipt           attestation       receipt
```

All three formats anchor to the same canonicalisation discipline. A
verifier walking the audit chain confirms admission → settlement →
refund under one byte-deterministic pin.

## Packages

| Language | Package | Install |
|---|---|---|
| Python | [`algovoi-settlement-attestation`](https://pypi.org/project/algovoi-settlement-attestation/) | `pip install algovoi-settlement-attestation` |
| TypeScript | [`@algovoi/settlement-attestation`](https://www.npmjs.com/package/@algovoi/settlement-attestation) | `npm install @algovoi/settlement-attestation` |

Both depend on `algovoi-substrate` / `@algovoi/substrate` for the JCS
canonicalisation primitive.

## Quick start

### Python

```python
from algovoi_settlement_attestation import build_settlement_attestation
from algovoi_substrate import sha256_jcs

a = build_settlement_attestation(
    settled_payment_ref="sha256:0dd5d0b76c9b9281fdeb2509ad38ab132b16a17385ca01d976ff9e6e12563a0f",
    settlement_result="SETTLED",
    settlement_timestamp_ms=1716494400000,
    settlement_provider_did="did:web:api.algovoi.co.uk",
    settlement_amount={"amount_minor": "100000", "asset_id": "USDC.6"},
    settlement_chain="ethereum:8453",
    jurisdiction_flags=["UK", "EU"],
)
print(sha256_jcs(dict(a)))
# 0ead75bfe7fc74cc0421124903e56cb5c5006d02c393231a1d5f260fa87e96d3
```

### TypeScript

```typescript
import { buildSettlementAttestation } from "@algovoi/settlement-attestation";
import { sha256Jcs } from "@algovoi/substrate";

const a = buildSettlementAttestation({
  settled_payment_ref:
    "sha256:0dd5d0b76c9b9281fdeb2509ad38ab132b16a17385ca01d976ff9e6e12563a0f",
  settlement_result: "SETTLED",
  settlement_timestamp_ms: 1716494400000,
  settlement_provider_did: "did:web:api.algovoi.co.uk",
  settlement_amount: { amount_minor: "100000", asset_id: "USDC.6" },
  settlement_chain: "ethereum:8453",
  jurisdiction_flags: ["UK", "EU"],
});
console.log(sha256Jcs(a));
// 0ead75bfe7fc74cc0421124903e56cb5c5006d02c393231a1d5f260fa87e96d3
```

## Receipt format

Eight-field JSON object canonicalised under RFC 8785 (JCS):

| Field | Type | Description |
|---|---|---|
| `canon_version` | string | `jcs-rfc8785-v1` |
| `jurisdiction_flags` | ordered array | ISO-3166-1 codes; primary jurisdiction first |
| `settled_payment_ref` | string | `sha256:<hex>` reference to original payment record |
| `settlement_amount` | object | `{amount_minor: string, asset_id: string}` |
| `settlement_chain` | string | `<chain_family>` (e.g. `algo`, `solana`) or `<chain_family>:<network>` (e.g. `ethereum:8453`) |
| `settlement_provider_did` | string | DID URI of attesting party |
| `settlement_result` | string (closed enum) | `SETTLED` / `PENDING_FINALITY` / `REVERSED` |
| `settlement_timestamp_ms` | integer | Epoch ms (Substrate Rule 2) |

## Closed enumeration: `settlement_result`

| Value | Semantic | Regulatory significance |
|---|---|---|
| `SETTLED` | Payment confirmed on-chain with sufficient finality. | Triggers settlement-finality record-keeping under MiCA Article 80 and AMLR Article 56. PSD2 Article 89 refund-window clock starts. |
| `PENDING_FINALITY` | Broadcast and included, awaiting confirmation depth. | Operator has visibility of inclusion but does not assert finality. PSD2 refund-window timing differs from SETTLED. |
| `REVERSED` | Previously SETTLED payment now considered reversed (chain reorg, fraud reversal, operator-initiated under regulatory directive). | Triggers reversal-evidence obligations under POCA s.330 and AML5/6. |

## Multi-chain settlement_chain identifier

AlgoVoi's production xChain runs on 8 chain families. Conventional identifiers:

| Chain | Identifier |
|---|---|
| Algorand mainnet | `algo` |
| VOI mainnet | `voi` |
| Solana mainnet | `solana` |
| Stellar Pubnet | `stellar` |
| Hedera mainnet | `hedera` |
| Base L2 | `base` or `ethereum:8453` |
| Tempo mainnet | `tempo:mainnet` |
| Ethereum mainnet | `ethereum:1` |

## Conformance vectors

8 byte-level reference vectors + 5 pair invariants + 3 chain invariants
at [`vectors/settlement_attestation_v1/`](https://github.com/chopmob-cloud/algovoi-jcs-conformance-vectors/tree/main/vectors/settlement_attestation_v1).

## Companion IETF Internet-Draft

[`draft-hopley-x402-settlement-attestation-00`](https://datatracker.ietf.org/doc/draft-hopley-x402-settlement-attestation/)
(Independent Submission, Informational). AlgoVoi-authored, sole
authorship.

## Related AlgoVoi packages

| Package | Purpose |
|---|---|
| [`algovoi-substrate`](https://pypi.org/project/algovoi-substrate/) / [`@algovoi/substrate`](https://www.npmjs.com/package/@algovoi/substrate) | JCS RFC 8785 canonicalisation, `action_ref`, compliance receipts |
| [`algovoi-refund-receipt`](https://pypi.org/project/algovoi-refund-receipt/) / [`@algovoi/refund-receipt`](https://www.npmjs.com/package/@algovoi/refund-receipt) | Refund receipt format |
| [`algovoi-rfc9421-verifier`](https://pypi.org/project/algovoi-rfc9421-verifier/) / [`@algovoi/rfc9421-verifier`](https://www.npmjs.com/package/@algovoi/rfc9421-verifier) | RFC 9421 HTTP message signature verifier |
| **`algovoi-settlement-attestation`** / `@algovoi/settlement-attestation` | **This package.** Settlement attestation format |

## Conformance to the canonicalisation discipline

This package emits settlement attestations pinned to `canon_version: jcs-rfc8785-v1` on every emitted attestation. The pin is in-band; downstream verifiers (including [`algovoi-audit-verifier`](https://pypi.org/project/algovoi-audit-verifier/) and any conformant third-party verifier) read the pin to select the canonicalisation rule applied at emission.

The pin is the load-bearing primitive for the [Substrate Adopters Registry](https://docs.algovoi.co.uk/adopters): adopters anchoring to this discipline pin the same `canon_version` value in their own publicly-citable artefacts. AlgoVoi maintains the registry as a neutral observer; this package itself is recorded there as the AlgoVoi reference implementation.

## Substrate adopters

AlgoVoi is recorded in the [Substrate Adopters Registry](https://docs.algovoi.co.uk/adopters) as the substrate author (v1 and v2). Parties anchoring their own services or specifications to `canon_version: jcs-rfc8785-v1` are recorded in the registry via the [submission process](https://docs.algovoi.co.uk/adopters#how-to-submit-an-adoption-entry). AlgoVoi validates submissions against the artefact's canonical bytes and adds qualifying entries.

## Licence

Apache 2.0.
