//! Closed final descriptor-template (`d0`) decoder and trial identity.

use core::fmt;

use crate::{fixture::RecoveryFixture, hex, sha256, tv};

pub const TRIAL_DOMAIN: &[u8] = b"ZGR01B-TRIAL\0";

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct PublicationDescriptor {
    pub backend: String,
    pub case_id: String,
    pub continuation: Vec<u8>,
    pub cut: String,
    pub history_production: String,
    pub injected_fault: String,
    pub mechanism_manifest: String,
    pub observer_profile: String,
    pub repetition: u64,
    pub requested_payload: Vec<u8>,
    pub setup: String,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct RecoveryDescriptor {
    pub backend: String,
    pub case_id: String,
    pub continuation: Vec<u8>,
    pub history_production: String,
    pub mechanism_manifest: String,
    pub observer_profile: String,
    pub recovery_fixture: RecoveryFixture,
    pub repetition: u64,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum DescriptorTemplate {
    Publication(PublicationDescriptor),
    RecoveryOnly(RecoveryDescriptor),
    LabOnly {
        case_id: String,
        lab_input: tv::Value,
    },
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum Error {
    Tv(tv::Error),
    Fixture(crate::fixture::Error),
    ExpectedMap,
    WrongShape,
    WrongType(&'static str),
    WrongHistoryProduction(String),
    InvalidCaseId,
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Tv(error) => write!(f, "{error}"),
            Self::Fixture(error) => write!(f, "{error}"),
            Self::ExpectedMap => f.write_str("descriptor template must be a TV map"),
            Self::WrongShape => f.write_str("descriptor template has the wrong closed shape"),
            Self::WrongType(field) => write!(f, "descriptor field {field} has the wrong TV type"),
            Self::WrongHistoryProduction(value) => {
                write!(f, "unknown history production {value:?}")
            }
            Self::InvalidCaseId => {
                f.write_str("case_id is not r01b-case- plus 64 lowercase hex digits")
            }
        }
    }
}

impl std::error::Error for Error {}

impl From<tv::Error> for Error {
    fn from(value: tv::Error) -> Self {
        Self::Tv(value)
    }
}

impl From<crate::fixture::Error> for Error {
    fn from(value: crate::fixture::Error) -> Self {
        Self::Fixture(value)
    }
}

impl DescriptorTemplate {
    pub fn decode_exact(bytes: &[u8]) -> Result<Self, Error> {
        let value = tv::decode_exact(bytes)?;
        Self::from_tv(&value)
    }

    pub fn from_tv(value: &tv::Value) -> Result<Self, Error> {
        let fields = match value {
            tv::Value::Map(fields) => fields,
            _ => return Err(Error::ExpectedMap),
        };
        let case_id = text(field(fields, "case_id")?, "case_id")?.to_owned();
        validate_case_id(&case_id)?;

        if field(fields, "lab_input").is_ok() {
            if keys(fields) != ["case_id", "lab_input"] {
                return Err(Error::WrongShape);
            }
            return Ok(Self::LabOnly {
                case_id,
                lab_input: field(fields, "lab_input")?.clone(),
            });
        }

        let production = text(field(fields, "history_production")?, "history_production")?;
        match production {
            "PUBLICATION" => {
                if keys(fields)
                    != [
                        "backend",
                        "case_id",
                        "continuation",
                        "cut",
                        "history_production",
                        "injected_fault",
                        "mechanism_manifest",
                        "observer_profile",
                        "repetition",
                        "requested_payload",
                        "setup",
                    ]
                {
                    return Err(Error::WrongShape);
                }
                Ok(Self::Publication(PublicationDescriptor {
                    backend: text(field(fields, "backend")?, "backend")?.to_owned(),
                    case_id,
                    continuation: bytes(field(fields, "continuation")?, "continuation")?.to_vec(),
                    cut: text(field(fields, "cut")?, "cut")?.to_owned(),
                    history_production: production.to_owned(),
                    injected_fault: text(field(fields, "injected_fault")?, "injected_fault")?
                        .to_owned(),
                    mechanism_manifest: text(
                        field(fields, "mechanism_manifest")?,
                        "mechanism_manifest",
                    )?
                    .to_owned(),
                    observer_profile: text(field(fields, "observer_profile")?, "observer_profile")?
                        .to_owned(),
                    repetition: unsigned(field(fields, "repetition")?, "repetition")?,
                    requested_payload: bytes(
                        field(fields, "requested_payload")?,
                        "requested_payload",
                    )?
                    .to_vec(),
                    setup: text(field(fields, "setup")?, "setup")?.to_owned(),
                }))
            }
            "RECOVERY_ONLY" => {
                if keys(fields)
                    != [
                        "backend",
                        "case_id",
                        "continuation",
                        "history_production",
                        "mechanism_manifest",
                        "observer_profile",
                        "recovery_fixture",
                        "repetition",
                    ]
                {
                    return Err(Error::WrongShape);
                }
                Ok(Self::RecoveryOnly(RecoveryDescriptor {
                    backend: text(field(fields, "backend")?, "backend")?.to_owned(),
                    case_id,
                    continuation: bytes(field(fields, "continuation")?, "continuation")?.to_vec(),
                    history_production: production.to_owned(),
                    mechanism_manifest: text(
                        field(fields, "mechanism_manifest")?,
                        "mechanism_manifest",
                    )?
                    .to_owned(),
                    observer_profile: text(field(fields, "observer_profile")?, "observer_profile")?
                        .to_owned(),
                    recovery_fixture: RecoveryFixture::from_tv(field(fields, "recovery_fixture")?)?,
                    repetition: unsigned(field(fields, "repetition")?, "repetition")?,
                }))
            }
            other => Err(Error::WrongHistoryProduction(other.to_owned())),
        }
    }

    pub fn case_id(&self) -> &str {
        match self {
            Self::Publication(value) => &value.case_id,
            Self::RecoveryOnly(value) => &value.case_id,
            Self::LabOnly { case_id, .. } => case_id,
        }
    }
}

pub fn trial_digest(descriptor_template_tv: &[u8]) -> [u8; 32] {
    sha256::digest_parts(&[TRIAL_DOMAIN, descriptor_template_tv])
}

pub fn trial_id(descriptor_template_tv: &[u8]) -> String {
    format!(
        "r01b-{}",
        hex::encode(&trial_digest(descriptor_template_tv))
    )
}

fn validate_case_id(value: &str) -> Result<(), Error> {
    let Some(hex) = value.strip_prefix("r01b-case-") else {
        return Err(Error::InvalidCaseId);
    };
    if hex.len() != 64 || crate::hex::decode(hex).is_err() {
        return Err(Error::InvalidCaseId);
    }
    Ok(())
}

fn field<'a>(fields: &'a [(String, tv::Value)], key: &str) -> Result<&'a tv::Value, Error> {
    fields
        .binary_search_by(|(candidate, _)| candidate.as_bytes().cmp(key.as_bytes()))
        .ok()
        .map(|index| &fields[index].1)
        .ok_or(Error::WrongShape)
}

fn keys(fields: &[(String, tv::Value)]) -> Vec<&str> {
    fields.iter().map(|(key, _)| key.as_str()).collect()
}

fn text<'a>(value: &'a tv::Value, field: &'static str) -> Result<&'a str, Error> {
    value.as_text().ok_or(Error::WrongType(field))
}

fn bytes<'a>(value: &'a tv::Value, field: &'static str) -> Result<&'a [u8], Error> {
    value.as_bytes().ok_or(Error::WrongType(field))
}

fn unsigned(value: &tv::Value, field: &'static str) -> Result<u64, Error> {
    value.as_u64().ok_or(Error::WrongType(field))
}
