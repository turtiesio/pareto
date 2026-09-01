//! R0.1B `D_sem || P || H` record construction and recovery parsing.

use core::fmt;

use crate::{SEMANTIC_SUITE_DIGEST, sha256};

pub const DIGEST_BYTES: usize = 32;
pub const OVERHEAD_BYTES: usize = 64;
pub const MAX_PAYLOAD_BYTES: usize = 4096;
pub const MAX_RECORD_BYTES: usize = OVERHEAD_BYTES + MAX_PAYLOAD_BYTES;
pub const RECORD_DOMAIN: &[u8] = b"ZERO-GROUND-R01B-RECORD\0";

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum Error {
    TooShort {
        actual: usize,
    },
    TooLong {
        actual: usize,
    },
    SuiteMismatch {
        actual: [u8; 32],
    },
    HashMismatch {
        expected: [u8; 32],
        actual: [u8; 32],
    },
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::TooShort { actual } => write!(f, "record is shorter than 64 bytes: {actual}"),
            Self::TooLong { actual } => write!(f, "record is longer than 4160 bytes: {actual}"),
            Self::SuiteMismatch { .. } => f.write_str("record semantic-suite digest differs"),
            Self::HashMismatch { .. } => f.write_str("record payload hash differs"),
        }
    }
}

impl std::error::Error for Error {}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct ParsedRecord<'a> {
    pub semantic_suite_digest: [u8; 32],
    pub payload: &'a [u8],
    pub payload_hash: [u8; 32],
}

pub fn payload_hash_with_suite(suite: &[u8; 32], payload: &[u8]) -> [u8; 32] {
    sha256::digest_parts(&[
        RECORD_DOMAIN,
        suite,
        &(payload.len() as u64).to_be_bytes(),
        payload,
    ])
}

pub fn payload_hash(payload: &[u8]) -> [u8; 32] {
    payload_hash_with_suite(&SEMANTIC_SUITE_DIGEST, payload)
}

pub fn encode_with_suite(suite: &[u8; 32], payload: &[u8]) -> Result<Vec<u8>, Error> {
    if payload.len() > MAX_PAYLOAD_BYTES {
        return Err(Error::TooLong {
            actual: OVERHEAD_BYTES + payload.len(),
        });
    }
    let hash = payload_hash_with_suite(suite, payload);
    let mut output = Vec::with_capacity(OVERHEAD_BYTES + payload.len());
    output.extend_from_slice(suite);
    output.extend_from_slice(payload);
    output.extend_from_slice(&hash);
    Ok(output)
}

pub fn encode(payload: &[u8]) -> Result<Vec<u8>, Error> {
    encode_with_suite(&SEMANTIC_SUITE_DIGEST, payload)
}

pub fn wrong_suite_record(payload: &[u8]) -> Result<Vec<u8>, Error> {
    let mut wrong = SEMANTIC_SUITE_DIGEST;
    wrong[0] ^= 0x80;
    encode_with_suite(&wrong, payload)
}

pub fn parse<'a>(bytes: &'a [u8]) -> Result<ParsedRecord<'a>, Error> {
    parse_with_expected_suite(bytes, &SEMANTIC_SUITE_DIGEST)
}

pub fn parse_with_expected_suite<'a>(
    bytes: &'a [u8],
    expected_suite: &[u8; 32],
) -> Result<ParsedRecord<'a>, Error> {
    if bytes.len() < OVERHEAD_BYTES {
        return Err(Error::TooShort {
            actual: bytes.len(),
        });
    }
    if bytes.len() > MAX_RECORD_BYTES {
        return Err(Error::TooLong {
            actual: bytes.len(),
        });
    }
    let suite: [u8; 32] = bytes[..32].try_into().expect("32-byte prefix");
    if &suite != expected_suite {
        return Err(Error::SuiteMismatch { actual: suite });
    }
    let payload = &bytes[32..bytes.len() - 32];
    let actual_hash: [u8; 32] = bytes[bytes.len() - 32..]
        .try_into()
        .expect("32-byte suffix");
    let expected_hash = payload_hash_with_suite(&suite, payload);
    if !equal_32(&expected_hash, &actual_hash) {
        return Err(Error::HashMismatch {
            expected: expected_hash,
            actual: actual_hash,
        });
    }
    Ok(ParsedRecord {
        semantic_suite_digest: suite,
        payload,
        payload_hash: actual_hash,
    })
}

fn equal_32(left: &[u8; 32], right: &[u8; 32]) -> bool {
    let mut difference = 0_u8;
    for index in 0..32 {
        difference |= left[index] ^ right[index];
    }
    difference == 0
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::hex;

    const EMPTY_RECORD: &str = "996ff2afb799721da2a09ac1ae9dea2b6f7f7369c287b049c83fd1e641a482a64853649d24acf49ef566702f884ed0d4c8e6d74c9cfeb64e1ba76dfe3a3c0196";
    const ZERO_RECORD: &str = "996ff2afb799721da2a09ac1ae9dea2b6f7f7369c287b049c83fd1e641a482a600fa75a2cd3940cbf598707da3d715930c7c71121fc2858fdef84aef0dd5ff318b";

    #[test]
    fn matches_both_frozen_record_vectors() {
        assert_eq!(hex::encode(&encode(b"").unwrap()), EMPTY_RECORD);
        assert_eq!(hex::encode(&encode(&[0]).unwrap()), ZERO_RECORD);
        assert_eq!(
            parse(&hex::decode(EMPTY_RECORD).unwrap()).unwrap().payload,
            b""
        );
        assert_eq!(
            parse(&hex::decode(ZERO_RECORD).unwrap()).unwrap().payload,
            [0]
        );
    }

    #[test]
    fn rejects_all_proper_prefixes_and_bit_changes() {
        let record = encode(&[0]).unwrap();
        for end in 0..record.len() {
            assert!(parse(&record[..end]).is_err(), "accepted prefix {end}");
        }
        for index in 0..record.len() {
            for bit in 0..8 {
                let mut changed = record.clone();
                changed[index] ^= 1 << bit;
                assert!(parse(&changed).is_err(), "accepted flip ({index},{bit})");
            }
        }
    }

    #[test]
    fn coherent_wrong_suite_is_still_rejected() {
        let wrong = wrong_suite_record(b"").unwrap();
        assert!(matches!(parse(&wrong), Err(Error::SuiteMismatch { .. })));
    }
}
