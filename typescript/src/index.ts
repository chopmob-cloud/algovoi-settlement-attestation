/**
 * @algovoi/settlement-attestation
 *
 * AlgoVoi settlement attestation reference implementation.
 * Multi-chain categorical attestation under JCS RFC 8785.
 *
 * Specified in IETF Internet-Draft draft-hopley-x402-settlement-attestation-00.
 * Apache 2.0.
 */

export {
  SETTLEMENT_RESULTS,
  type SettlementResult,
  SettlementAttestationError,
  type SettlementAttestation,
  type SettlementAmount,
  type BuildSettlementAttestationInput,
  buildSettlementAttestation,
} from './settlement-attestation.js';
