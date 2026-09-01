//! Exact declared service-component bytes and a pure in-memory subject model.
//!
//! The contract does not freeze an enclosing byte schema for `BH`,
//! `B_input_key`, or `B_response`; this module therefore does not invent one.
//! It retains and compares the exact declared publish-result and recovery-
//! observation byte strings as separately typed components.

use core::fmt;

use crate::{
    descriptor::PublicationDescriptor,
    fixture::{Entry, PublicationFixture, PublicationSetup, RecoveryFixture},
    record,
};

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum RecoveryObservation {
    Absent,
    Reject,
    Ok(Vec<u8>),
}

impl RecoveryObservation {
    pub fn encode(&self) -> Vec<u8> {
        match self {
            Self::Absent => vec![0x00],
            Self::Reject => vec![0x01],
            Self::Ok(value) => {
                let mut bytes = Vec::with_capacity(5 + value.len());
                bytes.push(0x02);
                bytes.extend_from_slice(&(value.len() as u32).to_be_bytes());
                bytes.extend_from_slice(value);
                bytes
            }
        }
    }

    pub fn decode_exact(bytes: &[u8]) -> Result<Self, WireError> {
        match bytes {
            [0x00] => Ok(Self::Absent),
            [0x01] => Ok(Self::Reject),
            [0x02, length @ ..] if length.len() >= 4 => {
                let size = u32::from_be_bytes(length[..4].try_into().expect("four bytes")) as usize;
                if length.len() != 4 + size {
                    return Err(WireError::WrongLength);
                }
                Ok(Self::Ok(length[4..].to_vec()))
            }
            [tag, ..] => Err(WireError::UnknownTag(*tag)),
            [] => Err(WireError::WrongLength),
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum PublishResult {
    Complete,
    Error { slot: u8, source: u8, errno: i32 },
}

impl PublishResult {
    pub fn encode(&self) -> Vec<u8> {
        match self {
            Self::Complete => vec![0x10],
            Self::Error {
                slot,
                source,
                errno,
            } => {
                let mut bytes = vec![0x11, *slot, *source];
                bytes.extend_from_slice(&errno.to_be_bytes());
                bytes
            }
        }
    }

    pub fn decode_exact(bytes: &[u8]) -> Result<Self, WireError> {
        match bytes {
            [0x10] => Ok(Self::Complete),
            [0x11, slot, source, errno @ ..] if errno.len() == 4 => Ok(Self::Error {
                slot: *slot,
                source: *source,
                errno: i32::from_be_bytes(errno.try_into().expect("four bytes")),
            }),
            [tag, ..] => Err(WireError::UnknownTag(*tag)),
            [] => Err(WireError::WrongLength),
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum WireError {
    WrongLength,
    UnknownTag(u8),
}

impl fmt::Display for WireError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::WrongLength => f.write_str("wire value has the wrong exact length"),
            Self::UnknownTag(tag) => write!(f, "unknown service wire tag 0x{tag:02x}"),
        }
    }
}

impl std::error::Error for WireError {}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct BResponseComponents {
    /// Length zero when no publish-result crossing exists, otherwise length one.
    pub publish_result_list: Vec<Vec<u8>>,
    pub recovery_observation: Vec<u8>,
}

impl BResponseComponents {
    pub fn from_values(
        publish_result: Option<PublishResult>,
        recovery: RecoveryObservation,
    ) -> Self {
        Self {
            publish_result_list: publish_result
                .into_iter()
                .map(|value| value.encode())
                .collect(),
            recovery_observation: recovery.encode(),
        }
    }

    pub fn exact_match(&self, other: &Self) -> bool {
        self == other
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum ServiceResult {
    Complete(BResponseComponents),
    ControlUnavailable,
    Unsupported {
        reason: String,
        needed_evidence: String,
    },
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum ComparisonResult {
    Match,
    Differ,
    Unknown,
    NotCompared,
}

pub fn compare_complete_responses(
    left: Option<&BResponseComponents>,
    right: Option<&BResponseComponents>,
) -> ComparisonResult {
    match (left, right) {
        (Some(left), Some(right)) if left.exact_match(right) => ComparisonResult::Match,
        (Some(_), Some(_)) => ComparisonResult::Differ,
        _ => ComparisonResult::Unknown,
    }
}

/// Section-5 aggregate over the executed edges incident to one descriptor.
pub fn aggregate_comparisons(
    results: impl IntoIterator<Item = ComparisonResult>,
) -> ComparisonResult {
    let mut saw_match = false;
    let mut saw_unknown = false;
    for result in results {
        match result {
            ComparisonResult::Differ => return ComparisonResult::Differ,
            ComparisonResult::Unknown => saw_unknown = true,
            ComparisonResult::Match => saw_match = true,
            ComparisonResult::NotCompared => {}
        }
    }
    if saw_unknown {
        ComparisonResult::Unknown
    } else if saw_match {
        ComparisonResult::Match
    } else {
        ComparisonResult::NotCompared
    }
}

#[derive(Debug)]
pub enum RecoveryError {
    Fixture(crate::fixture::Error),
    UnsupportedContinuation,
}

impl fmt::Display for RecoveryError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Fixture(error) => write!(f, "{error}"),
            Self::UnsupportedContinuation => f.write_str(
                "continuation is outside the frozen C=empty adapter position; new authority is required",
            ),
        }
    }
}

impl std::error::Error for RecoveryError {}

impl From<crate::fixture::Error> for RecoveryError {
    fn from(value: crate::fixture::Error) -> Self {
        Self::Fixture(value)
    }
}

pub fn recover(
    fixture: &RecoveryFixture,
    continuation: &[u8],
) -> Result<RecoveryObservation, RecoveryError> {
    fixture.validate()?;
    if !continuation.is_empty() {
        // The frozen adapter position declares only C=empty.  This is not
        // silently widened into another continuation grammar.
        return Err(RecoveryError::UnsupportedContinuation);
    }
    let bytes = match &fixture.authoritative_entry {
        Entry::Absent => return Ok(RecoveryObservation::Absent),
        Entry::Symlink(_) => return Ok(RecoveryObservation::Reject),
        Entry::Regular(bytes) => bytes,
    };
    let parsed = match record::parse(bytes) {
        Ok(value) => value,
        Err(_) => return Ok(RecoveryObservation::Reject),
    };
    match parsed.payload {
        [] => Ok(RecoveryObservation::Ok(Vec::new())),
        [0] => Ok(RecoveryObservation::Ok(vec![0])),
        _ => Ok(RecoveryObservation::Reject),
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum Cut {
    J0,
    J1,
    J2,
    J3,
    J4,
    J5,
    Normal,
}

impl Cut {
    fn parse(value: &str) -> Option<Self> {
        match value {
            "J0" => Some(Self::J0),
            "J1" => Some(Self::J1),
            "J2" => Some(Self::J2),
            "J3" => Some(Self::J3),
            "J4" => Some(Self::J4),
            "J5" => Some(Self::J5),
            "NORMAL" => Some(Self::Normal),
            _ => None,
        }
    }

    const fn ordinal(self) -> u8 {
        match self {
            Self::J0 => 0,
            Self::J1 => 1,
            Self::J2 => 2,
            Self::J3 => 3,
            Self::J4 => 4,
            Self::J5 => 5,
            Self::Normal => 6,
        }
    }
}

/// Evaluate the process-kill publication semantics without claiming OS,
/// filesystem, trace, reaping, power-loss, or physical behavior.
///
/// Only contract-declared branches are evaluated.  Unknown registry labels
/// return `Unsupported` rather than being guessed.
pub fn publish_model(descriptor: &PublicationDescriptor) -> ServiceResult {
    let Some(cut) = Cut::parse(&descriptor.cut) else {
        return unsupported("unregistered cut", "a frozen descriptor row");
    };
    let Ok(setup) = PublicationSetup::parse(&descriptor.setup) else {
        return unsupported("unregistered setup", "a frozen descriptor row");
    };
    if !descriptor.continuation.is_empty() {
        return unsupported(
            "continuation is outside the frozen C=empty position",
            "a newly frozen adapter position",
        );
    }
    if !descriptor.requested_payload.is_empty() && descriptor.requested_payload != [0] {
        return unsupported(
            "payload is outside the frozen P0/P1 positions",
            "a newly frozen adapter position",
        );
    }

    if descriptor.mechanism_manifest == "DROP_STAGE_CONTROLLER" && cut != Cut::Normal {
        return ServiceResult::ControlUnavailable;
    }

    let PublicationFixture {
        authoritative_entry: old,
        staging_entry,
    } = setup.fixture();
    let mut selected = old;
    let occupied = !matches!(staging_entry, Entry::Absent);

    let fault = descriptor.injected_fault.as_str();
    let injected_error = match fault {
        "NONE" | "SHORT_WRITE_1" | "SHORT_WRITE_2" | "SHORT_WRITE_7" | "SHORT_WRITE_31" => None,
        // The fourth member is the first checkpoint made unreachable by the
        // failed operation. Earlier armed checkpoints still kill first.
        "FILE_FSYNC_EIO" | "FILE_FSYNC_ERROR" => Some((0x03, 0x01, 5, 3)),
        "REPLACE_EIO" | "REPLACE_ERROR" => Some((0x04, 0x01, 5, 4)),
        "DIRECTORY_FSYNC_EIO" | "DIRECTORY_FSYNC_ERROR" => Some((0x05, 0x01, 5, 5)),
        _ => {
            return unsupported(
                "injected-fault label is not implemented by the pure model",
                "the frozen row's literal exact B expectation",
            );
        }
    };

    let acquire_exclusive = descriptor.mechanism_manifest != "NO_EXCLUSIVE_CREATE";
    let error = if occupied && acquire_exclusive {
        Some((0x01, 0x00, 17, 1))
    } else {
        injected_error
    };
    let failure_preempts_cut =
        error.is_some_and(|(_, _, _, first_unreachable)| cut.ordinal() >= first_unreachable);

    let no_replace = descriptor.mechanism_manifest == "NO_REPLACE";
    let killed = cut != Cut::Normal && !failure_preempts_cut;
    let replacement_reached =
        cut.ordinal() >= 4 && !matches!(error, Some((0x01 | 0x03 | 0x04, _, _, _)));
    if replacement_reached && !no_replace {
        selected = Entry::Regular(
            record::encode(&descriptor.requested_payload).expect("payload bounds checked"),
        );
    }

    let publish_result = if killed {
        None
    } else if let Some((slot, source, errno, _)) = error {
        Some(PublishResult::Error {
            slot,
            source,
            errno,
        })
    } else {
        Some(PublishResult::Complete)
    };
    let recovery = recover_authoritative(&selected, &descriptor.continuation);
    ServiceResult::Complete(BResponseComponents::from_values(publish_result, recovery))
}

fn recover_authoritative(entry: &Entry, continuation: &[u8]) -> RecoveryObservation {
    let fixture = RecoveryFixture {
        authoritative_entry: entry.clone(),
        auxiliary_regular_entries: Vec::new(),
    };
    recover(&fixture, continuation).expect("model creates a valid fixture")
}

fn unsupported(reason: &str, needed_evidence: &str) -> ServiceResult {
    ServiceResult::Unsupported {
        reason: reason.to_owned(),
        needed_evidence: needed_evidence.to_owned(),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn exact_service_wire_values() {
        for value in [
            RecoveryObservation::Absent,
            RecoveryObservation::Reject,
            RecoveryObservation::Ok(vec![]),
            RecoveryObservation::Ok(vec![0]),
        ] {
            assert_eq!(
                RecoveryObservation::decode_exact(&value.encode()).unwrap(),
                value
            );
        }
        assert_eq!(PublishResult::Complete.encode(), [0x10]);
        assert_eq!(
            PublishResult::Error {
                slot: 3,
                source: 1,
                errno: 5
            }
            .encode(),
            [0x11, 3, 1, 0, 0, 0, 5]
        );
        assert_eq!(
            aggregate_comparisons([
                ComparisonResult::Match,
                ComparisonResult::Unknown,
                ComparisonResult::NotCompared,
            ]),
            ComparisonResult::Unknown
        );
        assert_eq!(
            aggregate_comparisons([ComparisonResult::Unknown, ComparisonResult::Differ,]),
            ComparisonResult::Differ
        );
    }

    #[test]
    fn recovery_handles_exact_fixture_kinds_and_records() {
        let absent = RecoveryFixture {
            authoritative_entry: Entry::Absent,
            auxiliary_regular_entries: vec![],
        };
        assert_eq!(recover(&absent, b"").unwrap(), RecoveryObservation::Absent);

        let valid = RecoveryFixture {
            authoritative_entry: Entry::Regular(record::encode(&[0]).unwrap()),
            auxiliary_regular_entries: vec![],
        };
        assert_eq!(
            recover(&valid, b"").unwrap(),
            RecoveryObservation::Ok(vec![0])
        );

        let mut corrupt = record::encode(b"").unwrap();
        corrupt[63] ^= 1;
        assert_eq!(
            recover(
                &RecoveryFixture {
                    authoritative_entry: Entry::Regular(corrupt),
                    auxiliary_regular_entries: vec![],
                },
                b""
            )
            .unwrap(),
            RecoveryObservation::Reject
        );
    }
}
