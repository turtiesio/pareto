//! Exact recursive typed-value (`TV`) codec from R0.1B section 3.

use core::fmt;

pub const TAG_U64: u8 = 0x01;
pub const TAG_I64: u8 = 0x02;
pub const TAG_BYTES: u8 = 0x03;
pub const TAG_TEXT: u8 = 0x04;
pub const TAG_FALSE: u8 = 0x05;
pub const TAG_TRUE: u8 = 0x06;
pub const TAG_LIST: u8 = 0x07;
pub const TAG_MAP: u8 = 0x08;
pub const TAG_UNKNOWN: u8 = 0x09;
pub const TAG_UNSUPPORTED: u8 = 0x0a;
pub const TAG_ENUM: u8 = 0x0b;

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum Value {
    U64(u64),
    I64(i64),
    Bytes(Vec<u8>),
    Text(String),
    Bool(bool),
    List(Vec<Value>),
    Map(Vec<(String, Value)>),
    Unknown {
        reason: String,
        needed_evidence: String,
    },
    Unsupported {
        reason: String,
    },
    Enum {
        namespace: u16,
        code: u16,
    },
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct Limits {
    pub max_depth: usize,
    pub max_container_items: usize,
    pub max_blob_bytes: usize,
    pub max_total_bytes: usize,
}

impl Default for Limits {
    fn default() -> Self {
        Self {
            max_depth: 128,
            max_container_items: 1_100_000,
            max_blob_bytes: 64 * 1024 * 1024,
            max_total_bytes: 128 * 1024 * 1024,
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum ErrorKind {
    Empty,
    UnknownTag(u8),
    Truncated { needed: usize, remaining: usize },
    TrailingBytes(usize),
    LengthOverflow(u64),
    LimitExceeded(&'static str),
    InvalidUtf8,
    InvalidMapKey(u8),
    MapKeyNotStrictlyOrdered,
    EmptyUnknownMember(&'static str),
    WrongEmbeddedType { expected: &'static str },
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct Error {
    pub offset: usize,
    pub kind: ErrorKind,
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "TV error at byte {}: ", self.offset)?;
        match &self.kind {
            ErrorKind::Empty => f.write_str("empty input"),
            ErrorKind::UnknownTag(tag) => write!(f, "unknown tag 0x{tag:02x}"),
            ErrorKind::Truncated { needed, remaining } => {
                write!(f, "truncated value (need {needed}, have {remaining})")
            }
            ErrorKind::TrailingBytes(count) => write!(f, "{count} trailing bytes"),
            ErrorKind::LengthOverflow(value) => write!(f, "length {value} cannot fit usize"),
            ErrorKind::LimitExceeded(name) => write!(f, "{name} limit exceeded"),
            ErrorKind::InvalidUtf8 => f.write_str("text is not valid UTF-8"),
            ErrorKind::InvalidMapKey(byte) => {
                write!(f, "map key contains non-printable ASCII byte 0x{byte:02x}")
            }
            ErrorKind::MapKeyNotStrictlyOrdered => {
                f.write_str("map keys are duplicated or not unsigned-byte ordered")
            }
            ErrorKind::EmptyUnknownMember(name) => write!(f, "{name} must be nonempty"),
            ErrorKind::WrongEmbeddedType { expected } => {
                write!(f, "embedded value must be {expected}")
            }
        }
    }
}

impl std::error::Error for Error {}

impl Value {
    pub fn encode(&self) -> Result<Vec<u8>, Error> {
        let mut output = Vec::new();
        encode_into(self, &mut output, 0, Limits::default())?;
        Ok(output)
    }

    pub fn map_get(&self, key: &str) -> Option<&Value> {
        match self {
            Self::Map(entries) => entries
                .binary_search_by(|(candidate, _)| candidate.as_bytes().cmp(key.as_bytes()))
                .ok()
                .map(|index| &entries[index].1),
            _ => None,
        }
    }

    pub fn as_text(&self) -> Option<&str> {
        match self {
            Self::Text(value) => Some(value),
            _ => None,
        }
    }

    pub fn as_bytes(&self) -> Option<&[u8]> {
        match self {
            Self::Bytes(value) => Some(value),
            _ => None,
        }
    }

    pub fn as_u64(&self) -> Option<u64> {
        match self {
            Self::U64(value) => Some(*value),
            _ => None,
        }
    }
}

pub fn decode_exact(input: &[u8]) -> Result<Value, Error> {
    decode_exact_with_limits(input, Limits::default())
}

pub fn decode_exact_with_limits(input: &[u8], limits: Limits) -> Result<Value, Error> {
    if input.is_empty() {
        return Err(Error {
            offset: 0,
            kind: ErrorKind::Empty,
        });
    }
    if input.len() > limits.max_total_bytes {
        return Err(Error {
            offset: 0,
            kind: ErrorKind::LimitExceeded("total bytes"),
        });
    }
    let mut decoder = Decoder {
        input,
        offset: 0,
        limits,
    };
    let value = decoder.value(0)?;
    if decoder.offset != input.len() {
        return Err(Error {
            offset: decoder.offset,
            kind: ErrorKind::TrailingBytes(input.len() - decoder.offset),
        });
    }
    Ok(value)
}

struct Decoder<'a> {
    input: &'a [u8],
    offset: usize,
    limits: Limits,
}

impl Decoder<'_> {
    fn error(&self, kind: ErrorKind) -> Error {
        Error {
            offset: self.offset,
            kind,
        }
    }

    fn take(&mut self, count: usize) -> Result<&[u8], Error> {
        let remaining = self.input.len().saturating_sub(self.offset);
        if count > remaining {
            return Err(self.error(ErrorKind::Truncated {
                needed: count,
                remaining,
            }));
        }
        let start = self.offset;
        self.offset += count;
        Ok(&self.input[start..self.offset])
    }

    fn byte(&mut self) -> Result<u8, Error> {
        Ok(self.take(1)?[0])
    }

    fn u16(&mut self) -> Result<u16, Error> {
        Ok(u16::from_be_bytes(
            self.take(2)?.try_into().expect("two bytes"),
        ))
    }

    fn u64(&mut self) -> Result<u64, Error> {
        Ok(u64::from_be_bytes(
            self.take(8)?.try_into().expect("eight bytes"),
        ))
    }

    fn usize_len(&self, length: u64, kind: &'static str) -> Result<usize, Error> {
        let result =
            usize::try_from(length).map_err(|_| self.error(ErrorKind::LengthOverflow(length)))?;
        if result > self.limits.max_blob_bytes {
            return Err(self.error(ErrorKind::LimitExceeded(kind)));
        }
        Ok(result)
    }

    fn count(&self, count: u64) -> Result<usize, Error> {
        let result =
            usize::try_from(count).map_err(|_| self.error(ErrorKind::LengthOverflow(count)))?;
        if result > self.limits.max_container_items {
            return Err(self.error(ErrorKind::LimitExceeded("container items")));
        }
        Ok(result)
    }

    fn text_payload(&mut self) -> Result<String, Error> {
        let length = self.u64()?;
        let length = self.usize_len(length, "text bytes")?;
        let bytes = self.take(length)?;
        String::from_utf8(bytes.to_vec()).map_err(|_| self.error(ErrorKind::InvalidUtf8))
    }

    fn embedded_text(&mut self, member: &'static str) -> Result<String, Error> {
        let tag_offset = self.offset;
        if self.byte()? != TAG_TEXT {
            return Err(Error {
                offset: tag_offset,
                kind: ErrorKind::WrongEmbeddedType { expected: "text" },
            });
        }
        let value = self.text_payload()?;
        if value.is_empty() {
            return Err(self.error(ErrorKind::EmptyUnknownMember(member)));
        }
        Ok(value)
    }

    fn value(&mut self, depth: usize) -> Result<Value, Error> {
        if depth > self.limits.max_depth {
            return Err(self.error(ErrorKind::LimitExceeded("nesting depth")));
        }
        let tag_offset = self.offset;
        let tag = self.byte()?;
        match tag {
            TAG_U64 => Ok(Value::U64(self.u64()?)),
            TAG_I64 => Ok(Value::I64(i64::from_be_bytes(
                self.take(8)?.try_into().expect("eight bytes"),
            ))),
            TAG_BYTES => {
                let length = self.u64()?;
                let length = self.usize_len(length, "byte-string bytes")?;
                Ok(Value::Bytes(self.take(length)?.to_vec()))
            }
            TAG_TEXT => Ok(Value::Text(self.text_payload()?)),
            TAG_FALSE => Ok(Value::Bool(false)),
            TAG_TRUE => Ok(Value::Bool(true)),
            TAG_LIST => {
                let encoded_count = self.u64()?;
                let count = self.count(encoded_count)?;
                let mut items = Vec::with_capacity(count);
                for _ in 0..count {
                    items.push(self.value(depth + 1)?);
                }
                Ok(Value::List(items))
            }
            TAG_MAP => {
                let encoded_count = self.u64()?;
                let count = self.count(encoded_count)?;
                let mut entries = Vec::with_capacity(count);
                let mut previous: Option<Vec<u8>> = None;
                for _ in 0..count {
                    let key_len = usize::from(self.u16()?);
                    let key_bytes = self.take(key_len)?;
                    if let Some(byte) = key_bytes
                        .iter()
                        .copied()
                        .find(|byte| !(0x20..=0x7e).contains(byte))
                    {
                        return Err(self.error(ErrorKind::InvalidMapKey(byte)));
                    }
                    if previous.as_deref().is_some_and(|old| old >= key_bytes) {
                        return Err(self.error(ErrorKind::MapKeyNotStrictlyOrdered));
                    }
                    let key = String::from_utf8(key_bytes.to_vec())
                        .expect("printable ASCII map key is UTF-8");
                    previous = Some(key_bytes.to_vec());
                    let value = self.value(depth + 1)?;
                    entries.push((key, value));
                }
                Ok(Value::Map(entries))
            }
            TAG_UNKNOWN => {
                let reason = self.embedded_text("reason")?;
                let needed_evidence = self.embedded_text("needed_evidence")?;
                Ok(Value::Unknown {
                    reason,
                    needed_evidence,
                })
            }
            TAG_UNSUPPORTED => Ok(Value::Unsupported {
                reason: self.embedded_text("reason")?,
            }),
            TAG_ENUM => Ok(Value::Enum {
                namespace: self.u16()?,
                code: self.u16()?,
            }),
            other => Err(Error {
                offset: tag_offset,
                kind: ErrorKind::UnknownTag(other),
            }),
        }
    }
}

fn encode_into(
    value: &Value,
    output: &mut Vec<u8>,
    depth: usize,
    limits: Limits,
) -> Result<(), Error> {
    if depth > limits.max_depth {
        return Err(Error {
            offset: output.len(),
            kind: ErrorKind::LimitExceeded("nesting depth"),
        });
    }
    match value {
        Value::U64(value) => {
            output.push(TAG_U64);
            output.extend_from_slice(&value.to_be_bytes());
        }
        Value::I64(value) => {
            output.push(TAG_I64);
            output.extend_from_slice(&value.to_be_bytes());
        }
        Value::Bytes(bytes) => {
            output.push(TAG_BYTES);
            encode_blob(bytes, output, limits, "byte-string bytes")?;
        }
        Value::Text(text) => {
            output.push(TAG_TEXT);
            encode_blob(text.as_bytes(), output, limits, "text bytes")?;
        }
        Value::Bool(false) => output.push(TAG_FALSE),
        Value::Bool(true) => output.push(TAG_TRUE),
        Value::List(items) => {
            if items.len() > limits.max_container_items {
                return Err(Error {
                    offset: output.len(),
                    kind: ErrorKind::LimitExceeded("container items"),
                });
            }
            output.push(TAG_LIST);
            output.extend_from_slice(&(items.len() as u64).to_be_bytes());
            for item in items {
                encode_into(item, output, depth + 1, limits)?;
            }
        }
        Value::Map(entries) => {
            if entries.len() > limits.max_container_items {
                return Err(Error {
                    offset: output.len(),
                    kind: ErrorKind::LimitExceeded("container items"),
                });
            }
            output.push(TAG_MAP);
            output.extend_from_slice(&(entries.len() as u64).to_be_bytes());
            let mut previous: Option<&[u8]> = None;
            for (key, item) in entries {
                let bytes = key.as_bytes();
                if bytes.len() > usize::from(u16::MAX) {
                    return Err(Error {
                        offset: output.len(),
                        kind: ErrorKind::LimitExceeded("map-key bytes"),
                    });
                }
                if let Some(byte) = bytes
                    .iter()
                    .copied()
                    .find(|byte| !(0x20..=0x7e).contains(byte))
                {
                    return Err(Error {
                        offset: output.len(),
                        kind: ErrorKind::InvalidMapKey(byte),
                    });
                }
                if previous.is_some_and(|old| old >= bytes) {
                    return Err(Error {
                        offset: output.len(),
                        kind: ErrorKind::MapKeyNotStrictlyOrdered,
                    });
                }
                previous = Some(bytes);
                output.extend_from_slice(&(bytes.len() as u16).to_be_bytes());
                output.extend_from_slice(bytes);
                encode_into(item, output, depth + 1, limits)?;
            }
        }
        Value::Unknown {
            reason,
            needed_evidence,
        } => {
            if reason.is_empty() {
                return Err(Error {
                    offset: output.len(),
                    kind: ErrorKind::EmptyUnknownMember("reason"),
                });
            }
            if needed_evidence.is_empty() {
                return Err(Error {
                    offset: output.len(),
                    kind: ErrorKind::EmptyUnknownMember("needed_evidence"),
                });
            }
            output.push(TAG_UNKNOWN);
            encode_into(&Value::Text(reason.clone()), output, depth + 1, limits)?;
            encode_into(
                &Value::Text(needed_evidence.clone()),
                output,
                depth + 1,
                limits,
            )?;
        }
        Value::Unsupported { reason } => {
            if reason.is_empty() {
                return Err(Error {
                    offset: output.len(),
                    kind: ErrorKind::EmptyUnknownMember("reason"),
                });
            }
            output.push(TAG_UNSUPPORTED);
            encode_into(&Value::Text(reason.clone()), output, depth + 1, limits)?;
        }
        Value::Enum { namespace, code } => {
            output.push(TAG_ENUM);
            output.extend_from_slice(&namespace.to_be_bytes());
            output.extend_from_slice(&code.to_be_bytes());
        }
    }
    if output.len() > limits.max_total_bytes {
        return Err(Error {
            offset: output.len(),
            kind: ErrorKind::LimitExceeded("total bytes"),
        });
    }
    Ok(())
}

fn encode_blob(
    bytes: &[u8],
    output: &mut Vec<u8>,
    limits: Limits,
    limit_name: &'static str,
) -> Result<(), Error> {
    if bytes.len() > limits.max_blob_bytes {
        return Err(Error {
            offset: output.len(),
            kind: ErrorKind::LimitExceeded(limit_name),
        });
    }
    output.extend_from_slice(&(bytes.len() as u64).to_be_bytes());
    output.extend_from_slice(bytes);
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::hex;

    #[test]
    fn every_tag_round_trips_without_type_merging() {
        let value = Value::Map(vec![
            ("a".into(), Value::U64(0)),
            ("b".into(), Value::I64(0)),
            ("c".into(), Value::Bytes(vec![0xff])),
            ("d".into(), Value::Text("x".into())),
            ("e".into(), Value::Bool(false)),
            ("f".into(), Value::Bool(true)),
            ("g".into(), Value::List(vec![])),
            (
                "h".into(),
                Value::Unknown {
                    reason: "unknown".into(),
                    needed_evidence: "trace".into(),
                },
            ),
            (
                "i".into(),
                Value::Unsupported {
                    reason: "physical behavior unavailable".into(),
                },
            ),
            (
                "j".into(),
                Value::Enum {
                    namespace: 6,
                    code: 4,
                },
            ),
        ]);
        let encoded = value.encode().unwrap();
        assert_eq!(decode_exact(&encoded).unwrap(), value);
    }

    #[test]
    fn rejects_noncanonical_maps_trailing_bytes_and_wrong_unknown_shape() {
        let duplicate = hex::decode("0800000000000000020001610500016106").unwrap();
        assert!(matches!(
            decode_exact(&duplicate).unwrap_err().kind,
            ErrorKind::MapKeyNotStrictlyOrdered
        ));
        assert!(matches!(
            decode_exact(&[TAG_FALSE, TAG_TRUE]).unwrap_err().kind,
            ErrorKind::TrailingBytes(1)
        ));
        assert!(decode_exact(&[TAG_UNKNOWN, TAG_FALSE]).is_err());
    }
}
