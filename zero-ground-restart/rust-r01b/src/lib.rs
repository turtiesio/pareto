//! Independent R0.1B semantic machinery.
//!
//! This crate deliberately has no third-party dependencies.  It implements the
//! frozen typed-value codec, record validation, fixture schemas, pure subject
//! service model, registry reader, and retained-byte inventory directly from
//! the normative R0.1B contract and `R01B-S1.json`.

#![forbid(unsafe_code)]

pub mod descriptor;
pub mod fixture;
pub mod hex;
pub mod inventory;
pub mod json;
pub mod record;
pub mod s1;
pub mod service;
pub mod sha256;
pub mod tv;

/// Frozen semantic suite digest (`D_sem`).
pub const SEMANTIC_SUITE_DIGEST: [u8; 32] = [
    0x99, 0x6f, 0xf2, 0xaf, 0xb7, 0x99, 0x72, 0x1d, 0xa2, 0xa0, 0x9a, 0xc1, 0xae, 0x9d, 0xea, 0x2b,
    0x6f, 0x7f, 0x73, 0x69, 0xc2, 0x87, 0xb0, 0x49, 0xc8, 0x3f, 0xd1, 0xe6, 0x41, 0xa4, 0x82, 0xa6,
];

pub const SEMANTIC_SUITE_DIGEST_HEX: &str =
    "996ff2afb799721da2a09ac1ae9dea2b6f7f7369c287b049c83fd1e641a482a6";

pub const SEMANTIC_FREEZE_ID: &str =
    "r01b-semantic-954e2b16b258ceb8869795dbb823a0284a8369ca1cb20481168d7f652d89fcfd";

pub const FROZEN_S1_SHA256: [u8; 32] = [
    0xfb, 0x72, 0xf6, 0xb3, 0x6c, 0xa3, 0xea, 0xe2, 0x84, 0x00, 0x3e, 0xe1, 0x98, 0x3e, 0x99, 0x5a,
    0xfb, 0x13, 0xd3, 0xe8, 0xec, 0x9d, 0x51, 0x8f, 0x0c, 0x1a, 0xfe, 0xac, 0xa6, 0x7a, 0x90, 0x43,
];

pub const FROZEN_S1_LENGTH: usize = 28_549_230;
