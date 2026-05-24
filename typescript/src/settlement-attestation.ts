/**
 * Settlement attestation shape -- multi-chain categorical attestation
 * under the JCS RFC 8785 canonicalisation discipline.
 *
 * The categorical outcome (SETTLED / PENDING_FINALITY / REVERSED) is
 * load-bearing for downstream regulatory obligations:
 *
 * - SETTLED triggers settlement-finality records under MiCA Article 80
 *   and AMLR Article 56; PSD2 Article 89 refund-window clock starts.
 * - PENDING_FINALITY records inclusion-without-finality state.
 * - REVERSED records chain-reorganisation / fraud-reversal events.
 *
 * Specified in IETF Internet-Draft draft-hopley-x402-settlement-attestation-00
 * (Independent Submission, Informational; AlgoVoi-authored).
 */

import { CANON_VERSION } from '@algovoi/substrate';

export const SETTLEMENT_RESULTS = [
  'SETTLED',
  'PENDING_FINALITY',
  'REVERSED',
] as const;
export type SettlementResult = (typeof SETTLEMENT_RESULTS)[number];

export class SettlementAttestationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'SettlementAttestationError';
  }
}

export interface SettlementAmount {
  amount_minor: string;
  asset_id: string;
}

export interface SettlementAttestation {
  canon_version: string;
  jurisdiction_flags: string[];
  settled_payment_ref: string;
  settlement_amount: SettlementAmount;
  settlement_chain: string;
  settlement_provider_did: string;
  settlement_result: SettlementResult;
  settlement_timestamp_ms: number;
}

export interface BuildSettlementAttestationInput {
  settled_payment_ref: string;
  settlement_result: string;
  settlement_timestamp_ms: number;
  settlement_provider_did: string;
  settlement_amount: SettlementAmount;
  settlement_chain: string;
  jurisdiction_flags: string[];
  canon_version?: string;
}

function requireNonEmptyString(field: string, value: unknown): string {
  if (typeof value !== 'string' || value.length === 0) {
    throw new SettlementAttestationError(`${field} must be a non-empty string`);
  }
  return value;
}

function requireIntTimestampMs(value: unknown): number {
  if (typeof value !== 'number') {
    throw new SettlementAttestationError(
      `settlement_timestamp_ms must be epoch-millisecond integer (Substrate Rule 2), got ${typeof value}`,
    );
  }
  if (!Number.isFinite(value) || !Number.isInteger(value)) {
    throw new SettlementAttestationError(
      `settlement_timestamp_ms must be epoch-millisecond integer (Substrate Rule 2), got ${value}`,
    );
  }
  if (value < 0) {
    throw new SettlementAttestationError(
      `settlement_timestamp_ms must be non-negative, got ${value}`,
    );
  }
  return value;
}

function requireJurisdictionFlags(value: unknown): string[] {
  if (!Array.isArray(value)) {
    throw new SettlementAttestationError(
      `jurisdiction_flags must be array, got ${typeof value}`,
    );
  }
  for (let i = 0; i < value.length; i++) {
    const code = value[i];
    if (typeof code !== 'string' || code.length === 0) {
      throw new SettlementAttestationError(
        `jurisdiction_flags[${i}] must be a non-empty string`,
      );
    }
  }
  return [...value] as string[];
}

function requireSettlementAmount(value: unknown): SettlementAmount {
  if (value === null || typeof value !== 'object' || Array.isArray(value)) {
    throw new SettlementAttestationError(
      `settlement_amount must be object, got ${Array.isArray(value) ? 'array' : typeof value}`,
    );
  }
  const obj = value as Record<string, unknown>;
  const keys = Object.keys(obj).sort();
  const expected = ['amount_minor', 'asset_id'];
  if (
    keys.length !== expected.length ||
    keys[0] !== expected[0] ||
    keys[1] !== expected[1]
  ) {
    throw new SettlementAttestationError(
      `settlement_amount must have exactly the keys ${JSON.stringify(expected)}, got ${JSON.stringify(keys)}`,
    );
  }
  const amount_minor = obj.amount_minor;
  const asset_id = obj.asset_id;
  if (typeof amount_minor !== 'string' || amount_minor.length === 0) {
    throw new SettlementAttestationError(
      "settlement_amount.amount_minor must be a non-empty string (decimal digits in the asset's minor unit)",
    );
  }
  if (!/^[0-9]+$/.test(amount_minor)) {
    throw new SettlementAttestationError(
      `settlement_amount.amount_minor must be decimal digits only, got ${JSON.stringify(amount_minor)}`,
    );
  }
  if (typeof asset_id !== 'string' || asset_id.length === 0) {
    throw new SettlementAttestationError(
      'settlement_amount.asset_id must be a non-empty string',
    );
  }
  return { amount_minor, asset_id };
}

/**
 * Build a validated settlement attestation object.
 *
 * settlement_result MUST be one of SETTLED, PENDING_FINALITY, REVERSED.
 *
 * settlement_chain identifies the chain on which settlement occurred.
 * Convention: <chain_family> for default mainnet (e.g. "algo", "solana",
 * "stellar", "hedera", "base"); or <chain_family>:<network> for
 * non-default (e.g. "ethereum:8453" for Base by chainId).
 *
 * settlement_amount.amount_minor is a decimal-digit string in the
 * asset's minor unit; may differ from original payment amount under
 * cross-asset substitution.
 *
 * jurisdiction_flags is treated as ordered.
 * settlement_timestamp_ms MUST be integer (Substrate Rule 2).
 */
export function buildSettlementAttestation(
  input: BuildSettlementAttestationInput,
): SettlementAttestation {
  if (
    !SETTLEMENT_RESULTS.includes(input.settlement_result as SettlementResult)
  ) {
    throw new SettlementAttestationError(
      `settlement_result must be one of ${JSON.stringify([...SETTLEMENT_RESULTS])}, got ${JSON.stringify(input.settlement_result)}`,
    );
  }

  return {
    canon_version: requireNonEmptyString(
      'canon_version',
      input.canon_version ?? CANON_VERSION,
    ),
    jurisdiction_flags: requireJurisdictionFlags(input.jurisdiction_flags),
    settled_payment_ref: requireNonEmptyString(
      'settled_payment_ref',
      input.settled_payment_ref,
    ),
    settlement_amount: requireSettlementAmount(input.settlement_amount),
    settlement_chain: requireNonEmptyString(
      'settlement_chain',
      input.settlement_chain,
    ),
    settlement_provider_did: requireNonEmptyString(
      'settlement_provider_did',
      input.settlement_provider_did,
    ),
    settlement_result: input.settlement_result as SettlementResult,
    settlement_timestamp_ms: requireIntTimestampMs(input.settlement_timestamp_ms),
  };
}
