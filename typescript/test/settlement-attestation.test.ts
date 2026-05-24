import { describe, it, expect } from 'vitest';
import { existsSync, readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';

import { canonicalize, sha256Jcs } from '@algovoi/substrate';
import {
  SETTLEMENT_RESULTS,
  SettlementAttestationError,
  buildSettlementAttestation,
} from '../src/settlement-attestation.js';

describe('SETTLEMENT_RESULTS', () => {
  it('is exactly SETTLED, PENDING_FINALITY, REVERSED', () => {
    expect([...SETTLEMENT_RESULTS]).toEqual([
      'SETTLED',
      'PENDING_FINALITY',
      'REVERSED',
    ]);
  });
});

describe('buildSettlementAttestation', () => {
  const base = {
    settled_payment_ref: 'sha256:abc123',
    settlement_result: 'SETTLED',
    settlement_timestamp_ms: 1716460800000,
    settlement_provider_did: 'did:web:api.algovoi.co.uk',
    settlement_amount: { amount_minor: '100000', asset_id: 'USDC.6' },
    settlement_chain: 'ethereum:8453',
    jurisdiction_flags: ['UK', 'EU'],
  };

  it('builds canonical attestation', () => {
    const a = buildSettlementAttestation(base);
    expect(a).toEqual({ ...base, canon_version: 'jcs-rfc8785-v1' });
  });

  it('distinct settlement_result distinct hashes', () => {
    const s = buildSettlementAttestation({ ...base, settlement_result: 'SETTLED' });
    const p = buildSettlementAttestation({
      ...base,
      settlement_result: 'PENDING_FINALITY',
    });
    const r = buildSettlementAttestation({ ...base, settlement_result: 'REVERSED' });
    expect(sha256Jcs(s)).not.toBe(sha256Jcs(p));
    expect(sha256Jcs(s)).not.toBe(sha256Jcs(r));
    expect(sha256Jcs(p)).not.toBe(sha256Jcs(r));
  });

  it('distinct settlement_chain distinct hashes', () => {
    const baseChain = buildSettlementAttestation({
      ...base,
      settlement_chain: 'ethereum:8453',
    });
    const solChain = buildSettlementAttestation({
      ...base,
      settlement_chain: 'solana',
    });
    expect(sha256Jcs(baseChain)).not.toBe(sha256Jcs(solChain));
  });

  it('rejects invalid result', () => {
    expect(() =>
      buildSettlementAttestation({ ...base, settlement_result: 'FINALIZED' }),
    ).toThrow(/settlement_result must be one of/);
  });

  it('rejects float timestamp', () => {
    expect(() =>
      buildSettlementAttestation({ ...base, settlement_timestamp_ms: 1716460800000.5 }),
    ).toThrow(/Substrate Rule 2/);
  });

  it('rejects string timestamp', () => {
    expect(() =>
      buildSettlementAttestation({
        ...base,
        settlement_timestamp_ms: '2024-05-23T12:00:00Z' as unknown as number,
      }),
    ).toThrow(/Substrate Rule 2/);
  });

  it('rejects empty chain', () => {
    expect(() =>
      buildSettlementAttestation({ ...base, settlement_chain: '' }),
    ).toThrow(/settlement_chain/);
  });

  it('canon_version defaults to jcs-rfc8785-v1', () => {
    expect(buildSettlementAttestation(base).canon_version).toBe('jcs-rfc8785-v1');
  });
});

describe('Conformance vector reproduction', () => {
  const VECTOR_PATH =
    'C:/algo/algovoi-jcs-conformance-vectors/vectors/settlement_attestation_v1/settlement_attestation_v1.json';

  it('reproduces vectors 001 to 005 byte-identical', () => {
    if (!existsSync(VECTOR_PATH)) return;
    const data = JSON.parse(readFileSync(VECTOR_PATH, 'utf-8'));
    for (const v of data.vectors) {
      if (!v.receipt) continue;
      const canon = canonicalize(v.receipt);
      const canonBytes = Buffer.from(canon, 'utf-8');
      expect(canonBytes.toString('base64')).toBe(v.expected_jcs_bytes_b64);
      expect(createHash('sha256').update(canonBytes).digest('hex')).toBe(
        v.expected_content_hash,
      );
    }
  });
});
