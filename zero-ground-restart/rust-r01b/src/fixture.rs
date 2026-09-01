//! Closed publication and recovery fixture schemas from R0.1B section 1.3.

use core::fmt;

use crate::{record, tv};

pub const AUTHORITATIVE_NAME: &[u8] = b"state.bin";
pub const STAGING_NAME: &[u8] = b".state.tmp";
pub const NONREGULAR_TARGET: &[u8] = b".r01b-valid-target";

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum Entry {
    Absent,
    Regular(Vec<u8>),
    Symlink(Vec<u8>),
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct AuxiliaryRegularEntry {
    pub name_bytes: Vec<u8>,
    pub regular_bytes: Vec<u8>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct RecoveryFixture {
    pub authoritative_entry: Entry,
    pub auxiliary_regular_entries: Vec<AuxiliaryRegularEntry>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct PublicationFixture {
    pub authoritative_entry: Entry,
    pub staging_entry: Entry,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Ord, PartialOrd)]
pub enum PublicationSetup {
    AbsentClean,
    AbsentTmp,
    ValidP0Clean,
    ValidP0Tmp,
}

impl PublicationSetup {
    pub fn parse(text: &str) -> Result<Self, Error> {
        match text {
            "ABSENT_CLEAN" => Ok(Self::AbsentClean),
            "ABSENT_TMP" => Ok(Self::AbsentTmp),
            "VALID_P0_CLEAN" => Ok(Self::ValidP0Clean),
            "VALID_P0_TMP" => Ok(Self::ValidP0Tmp),
            _ => Err(Error::UnknownSetup(text.to_owned())),
        }
    }

    pub const fn label(self) -> &'static str {
        match self {
            Self::AbsentClean => "ABSENT_CLEAN",
            Self::AbsentTmp => "ABSENT_TMP",
            Self::ValidP0Clean => "VALID_P0_CLEAN",
            Self::ValidP0Tmp => "VALID_P0_TMP",
        }
    }

    pub fn fixture(self) -> PublicationFixture {
        let authoritative_entry = match self {
            Self::AbsentClean | Self::AbsentTmp => Entry::Absent,
            Self::ValidP0Clean | Self::ValidP0Tmp => {
                Entry::Regular(record::encode(b"").expect("P0 is in bounds"))
            }
        };
        let staging_entry = match self {
            Self::AbsentClean | Self::ValidP0Clean => Entry::Absent,
            Self::AbsentTmp | Self::ValidP0Tmp => Entry::Regular(Vec::new()),
        };
        PublicationFixture {
            authoritative_entry,
            staging_entry,
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum Error {
    Tv(tv::Error),
    ExpectedMap(&'static str),
    WrongKeys(&'static str),
    ExpectedText(&'static str),
    ExpectedBytes(&'static str),
    ExpectedList(&'static str),
    UnknownEntryKind(String),
    EntryShapeMismatch(String),
    InvalidAuxiliaryName,
    AuxiliaryNamesNotStrictlyOrdered,
    AuxiliaryForbiddenForEntryKind,
    UnknownSetup(String),
    NonregularFixtureMismatch,
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Tv(error) => write!(f, "{error}"),
            Self::ExpectedMap(name) => write!(f, "{name} must be a TV map"),
            Self::WrongKeys(name) => write!(f, "{name} has a non-closed map shape"),
            Self::ExpectedText(name) => write!(f, "{name} must be TV text"),
            Self::ExpectedBytes(name) => write!(f, "{name} must be TV bytes"),
            Self::ExpectedList(name) => write!(f, "{name} must be a TV list"),
            Self::UnknownEntryKind(kind) => write!(f, "unknown entry kind {kind:?}"),
            Self::EntryShapeMismatch(kind) => write!(f, "wrong closed shape for {kind} entry"),
            Self::InvalidAuxiliaryName => f.write_str("invalid auxiliary name component"),
            Self::AuxiliaryNamesNotStrictlyOrdered => {
                f.write_str("auxiliary names are duplicated or not unsigned-byte ordered")
            }
            Self::AuxiliaryForbiddenForEntryKind => {
                f.write_str("ABSENT and REGULAR fixtures require an empty auxiliary list")
            }
            Self::UnknownSetup(setup) => write!(f, "unknown publication setup {setup:?}"),
            Self::NonregularFixtureMismatch => {
                f.write_str("NONREGULAR fixture differs from the frozen target and auxiliary entry")
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

impl Entry {
    pub fn to_tv(&self) -> tv::Value {
        match self {
            Self::Absent => tv::Value::Map(vec![("kind".into(), tv::Value::Text("ABSENT".into()))]),
            Self::Regular(bytes) => tv::Value::Map(vec![
                ("kind".into(), tv::Value::Text("REGULAR".into())),
                ("regular_bytes".into(), tv::Value::Bytes(bytes.clone())),
            ]),
            Self::Symlink(target) => tv::Value::Map(vec![
                ("kind".into(), tv::Value::Text("SYMLINK".into())),
                (
                    "symlink_target_bytes".into(),
                    tv::Value::Bytes(target.clone()),
                ),
            ]),
        }
    }

    pub fn from_tv(value: &tv::Value) -> Result<Self, Error> {
        let entries = expect_map(value, "entry")?;
        let kind = entries
            .first()
            .filter(|(key, _)| key == "kind")
            .ok_or(Error::WrongKeys("entry"))?
            .1
            .as_text()
            .ok_or(Error::ExpectedText("entry.kind"))?;
        match kind {
            "ABSENT" if keys(entries) == ["kind"] => Ok(Self::Absent),
            "REGULAR" if keys(entries) == ["kind", "regular_bytes"] => Ok(Self::Regular(
                entries[1]
                    .1
                    .as_bytes()
                    .ok_or(Error::ExpectedBytes("entry.regular_bytes"))?
                    .to_vec(),
            )),
            "SYMLINK" if keys(entries) == ["kind", "symlink_target_bytes"] => Ok(Self::Symlink(
                entries[1]
                    .1
                    .as_bytes()
                    .ok_or(Error::ExpectedBytes("entry.symlink_target_bytes"))?
                    .to_vec(),
            )),
            "ABSENT" | "REGULAR" | "SYMLINK" => Err(Error::EntryShapeMismatch(kind.to_owned())),
            other => Err(Error::UnknownEntryKind(other.to_owned())),
        }
    }
}

impl PublicationFixture {
    pub fn to_tv(&self) -> tv::Value {
        tv::Value::Map(vec![
            (
                "authoritative_entry".into(),
                self.authoritative_entry.to_tv(),
            ),
            ("staging_entry".into(), self.staging_entry.to_tv()),
        ])
    }

    pub fn encode_tv(&self) -> Result<Vec<u8>, Error> {
        Ok(self.to_tv().encode()?)
    }

    pub fn decode_tv(bytes: &[u8]) -> Result<Self, Error> {
        let value = tv::decode_exact(bytes)?;
        Self::from_tv(&value)
    }

    pub fn from_tv(value: &tv::Value) -> Result<Self, Error> {
        let entries = expect_map(value, "publication fixture")?;
        if keys(entries) != ["authoritative_entry", "staging_entry"] {
            return Err(Error::WrongKeys("publication fixture"));
        }
        Ok(Self {
            authoritative_entry: Entry::from_tv(&entries[0].1)?,
            staging_entry: Entry::from_tv(&entries[1].1)?,
        })
    }
}

impl RecoveryFixture {
    pub fn to_tv(&self) -> tv::Value {
        let auxiliaries = self
            .auxiliary_regular_entries
            .iter()
            .map(|entry| {
                tv::Value::Map(vec![
                    (
                        "name_bytes".into(),
                        tv::Value::Bytes(entry.name_bytes.clone()),
                    ),
                    (
                        "regular_bytes".into(),
                        tv::Value::Bytes(entry.regular_bytes.clone()),
                    ),
                ])
            })
            .collect();
        tv::Value::Map(vec![
            (
                "authoritative_entry".into(),
                self.authoritative_entry.to_tv(),
            ),
            (
                "auxiliary_regular_entries".into(),
                tv::Value::List(auxiliaries),
            ),
        ])
    }

    pub fn validate(&self) -> Result<(), Error> {
        if !matches!(self.authoritative_entry, Entry::Symlink(_))
            && !self.auxiliary_regular_entries.is_empty()
        {
            return Err(Error::AuxiliaryForbiddenForEntryKind);
        }
        let mut previous: Option<&[u8]> = None;
        for entry in &self.auxiliary_regular_entries {
            let name = entry.name_bytes.as_slice();
            if name.is_empty()
                || name.contains(&0)
                || name.contains(&b'/')
                || name == AUTHORITATIVE_NAME
                || name == STAGING_NAME
            {
                return Err(Error::InvalidAuxiliaryName);
            }
            if previous.is_some_and(|old| old >= name) {
                return Err(Error::AuxiliaryNamesNotStrictlyOrdered);
            }
            previous = Some(name);
        }
        Ok(())
    }

    pub fn validate_current_nonregular(&self) -> Result<(), Error> {
        self.validate()?;
        let expected_record = record::encode(b"").expect("P0 is in bounds");
        match (
            &self.authoritative_entry,
            self.auxiliary_regular_entries.as_slice(),
        ) {
            (Entry::Symlink(target), [auxiliary])
                if target == NONREGULAR_TARGET
                    && auxiliary.name_bytes == NONREGULAR_TARGET
                    && auxiliary.regular_bytes == expected_record =>
            {
                Ok(())
            }
            _ => Err(Error::NonregularFixtureMismatch),
        }
    }

    pub fn encode_tv(&self) -> Result<Vec<u8>, Error> {
        self.validate()?;
        Ok(self.to_tv().encode()?)
    }

    pub fn decode_tv(bytes: &[u8]) -> Result<Self, Error> {
        let value = tv::decode_exact(bytes)?;
        Self::from_tv(&value)
    }

    pub fn from_tv(value: &tv::Value) -> Result<Self, Error> {
        let entries = expect_map(value, "recovery fixture")?;
        if keys(entries) != ["authoritative_entry", "auxiliary_regular_entries"] {
            return Err(Error::WrongKeys("recovery fixture"));
        }
        let authoritative_entry = Entry::from_tv(&entries[0].1)?;
        let list = match &entries[1].1 {
            tv::Value::List(value) => value,
            _ => return Err(Error::ExpectedList("auxiliary_regular_entries")),
        };
        let mut auxiliary_regular_entries = Vec::with_capacity(list.len());
        for value in list {
            let fields = expect_map(value, "auxiliary entry")?;
            if keys(fields) != ["name_bytes", "regular_bytes"] {
                return Err(Error::WrongKeys("auxiliary entry"));
            }
            auxiliary_regular_entries.push(AuxiliaryRegularEntry {
                name_bytes: fields[0]
                    .1
                    .as_bytes()
                    .ok_or(Error::ExpectedBytes("auxiliary.name_bytes"))?
                    .to_vec(),
                regular_bytes: fields[1]
                    .1
                    .as_bytes()
                    .ok_or(Error::ExpectedBytes("auxiliary.regular_bytes"))?
                    .to_vec(),
            });
        }
        let fixture = Self {
            authoritative_entry,
            auxiliary_regular_entries,
        };
        fixture.validate()?;
        Ok(fixture)
    }
}

fn expect_map<'a>(
    value: &'a tv::Value,
    name: &'static str,
) -> Result<&'a [(String, tv::Value)], Error> {
    match value {
        tv::Value::Map(entries) => Ok(entries),
        _ => Err(Error::ExpectedMap(name)),
    }
}

fn keys(entries: &[(String, tv::Value)]) -> Vec<&str> {
    entries.iter().map(|(key, _)| key.as_str()).collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn publication_labels_have_exact_closed_fixtures() {
        for label in [
            "ABSENT_CLEAN",
            "ABSENT_TMP",
            "VALID_P0_CLEAN",
            "VALID_P0_TMP",
        ] {
            let setup = PublicationSetup::parse(label).unwrap();
            let fixture = setup.fixture();
            assert_eq!(
                PublicationFixture::decode_tv(&fixture.encode_tv().unwrap()).unwrap(),
                fixture
            );
        }
    }

    #[test]
    fn current_nonregular_shape_is_exact() {
        let fixture = RecoveryFixture {
            authoritative_entry: Entry::Symlink(NONREGULAR_TARGET.to_vec()),
            auxiliary_regular_entries: vec![AuxiliaryRegularEntry {
                name_bytes: NONREGULAR_TARGET.to_vec(),
                regular_bytes: record::encode(b"").unwrap(),
            }],
        };
        fixture.validate_current_nonregular().unwrap();
        assert_eq!(
            RecoveryFixture::decode_tv(&fixture.encode_tv().unwrap()).unwrap(),
            fixture
        );
    }
}
