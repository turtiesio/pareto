//! Strict zero-dependency reader for the frozen canonical JSON profile.
//!
//! R0.1B S1 permits only printable ASCII strings, two exact escapes (`\"` and
//! `\\`), nonnegative shortest-decimal integers, booleans, arrays, and maps
//! whose keys are strictly ordered by unsigned UTF-8 bytes.  This reader does
//! not silently accept a broader JSON dialect.

use core::{fmt, ops::Range};

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct Span {
    pub start: usize,
    pub end: usize,
}

impl Span {
    pub fn range(self) -> Range<usize> {
        self.start..self.end
    }

    pub fn bytes(self, document: &[u8]) -> &[u8] {
        &document[self.range()]
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum ErrorKind {
    Empty,
    UnexpectedByte(u8),
    UnexpectedEnd,
    TrailingBytes,
    NonPrintableStringByte(u8),
    InvalidEscape(u8),
    NumberLeadingZero,
    NumberOverflow,
    ObjectKeyNotStrictlyOrdered,
    NestingLimit,
    Expected(&'static str),
    MissingField(String),
    WrongFields,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct Error {
    pub offset: usize,
    pub kind: ErrorKind,
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "canonical JSON error at byte {}: ", self.offset)?;
        match &self.kind {
            ErrorKind::Empty => f.write_str("empty document"),
            ErrorKind::UnexpectedByte(byte) => write!(f, "unexpected byte 0x{byte:02x}"),
            ErrorKind::UnexpectedEnd => f.write_str("unexpected end of input"),
            ErrorKind::TrailingBytes => f.write_str("trailing bytes"),
            ErrorKind::NonPrintableStringByte(byte) => {
                write!(f, "non-printable/non-ASCII string byte 0x{byte:02x}")
            }
            ErrorKind::InvalidEscape(byte) => {
                write!(f, "invalid/noncanonical escape \\{}", char::from(*byte))
            }
            ErrorKind::NumberLeadingZero => f.write_str("integer has a leading zero"),
            ErrorKind::NumberOverflow => f.write_str("integer exceeds u64"),
            ErrorKind::ObjectKeyNotStrictlyOrdered => {
                f.write_str("object keys are duplicated or not unsigned-byte ordered")
            }
            ErrorKind::NestingLimit => f.write_str("nesting limit exceeded"),
            ErrorKind::Expected(name) => write!(f, "expected {name}"),
            ErrorKind::MissingField(name) => write!(f, "missing field {name:?}"),
            ErrorKind::WrongFields => f.write_str("object has the wrong closed field set"),
        }
    }
}

impl std::error::Error for Error {}

const MAX_DEPTH: usize = 256;

pub fn validate(document: &[u8]) -> Result<Span, Error> {
    if document.is_empty() {
        return Err(Error {
            offset: 0,
            kind: ErrorKind::Empty,
        });
    }
    let mut parser = Parser {
        document,
        offset: 0,
    };
    let span = parser.value(0)?;
    if parser.offset != document.len() {
        return Err(parser.error(ErrorKind::TrailingBytes));
    }
    Ok(span)
}

pub fn object_fields(document: &[u8], span: Span) -> Result<Vec<(String, Span)>, Error> {
    let mut parser = Parser {
        document,
        offset: span.start,
    };
    parser.expect_byte(b'{', "object")?;
    let mut fields = Vec::new();
    if parser.peek() == Some(b'}') {
        parser.offset += 1;
    } else {
        loop {
            let key = parser.string()?;
            parser.expect_byte(b':', "colon")?;
            let value = parser.value(1)?;
            fields.push((key, value));
            match parser.byte()? {
                b',' => continue,
                b'}' => break,
                other => {
                    return Err(
                        parser.error_at(parser.offset - 1, ErrorKind::UnexpectedByte(other))
                    );
                }
            }
        }
    }
    if parser.offset != span.end {
        return Err(parser.error(ErrorKind::Expected("exact object span")));
    }
    Ok(fields)
}

pub fn array_items(document: &[u8], span: Span) -> Result<Vec<Span>, Error> {
    let mut parser = Parser {
        document,
        offset: span.start,
    };
    parser.expect_byte(b'[', "array")?;
    let mut items = Vec::new();
    if parser.peek() == Some(b']') {
        parser.offset += 1;
    } else {
        loop {
            items.push(parser.value(1)?);
            match parser.byte()? {
                b',' => continue,
                b']' => break,
                other => {
                    return Err(
                        parser.error_at(parser.offset - 1, ErrorKind::UnexpectedByte(other))
                    );
                }
            }
        }
    }
    if parser.offset != span.end {
        return Err(parser.error(ErrorKind::Expected("exact array span")));
    }
    Ok(items)
}

pub fn string_value(document: &[u8], span: Span) -> Result<String, Error> {
    let mut parser = Parser {
        document,
        offset: span.start,
    };
    let value = parser.string()?;
    if parser.offset != span.end {
        return Err(parser.error(ErrorKind::Expected("exact string span")));
    }
    Ok(value)
}

pub fn u64_value(document: &[u8], span: Span) -> Result<u64, Error> {
    let mut parser = Parser {
        document,
        offset: span.start,
    };
    let value = parser.number()?;
    if parser.offset != span.end {
        return Err(parser.error(ErrorKind::Expected("exact integer span")));
    }
    Ok(value)
}

pub fn bool_value(document: &[u8], span: Span) -> Result<bool, Error> {
    match span.bytes(document) {
        b"false" => Ok(false),
        b"true" => Ok(true),
        _ => Err(Error {
            offset: span.start,
            kind: ErrorKind::Expected("boolean"),
        }),
    }
}

pub fn field(fields: &[(String, Span)], name: &str) -> Result<Span, Error> {
    fields
        .binary_search_by(|(candidate, _)| candidate.as_bytes().cmp(name.as_bytes()))
        .ok()
        .map(|index| fields[index].1)
        .ok_or_else(|| Error {
            offset: 0,
            kind: ErrorKind::MissingField(name.to_owned()),
        })
}

pub fn require_fields(fields: &[(String, Span)], expected: &[&str]) -> Result<(), Error> {
    if fields.len() != expected.len()
        || fields
            .iter()
            .zip(expected)
            .any(|((actual, _), expected)| actual != expected)
    {
        return Err(Error {
            offset: fields.first().map_or(0, |(_, span)| span.start),
            kind: ErrorKind::WrongFields,
        });
    }
    Ok(())
}

struct Parser<'a> {
    document: &'a [u8],
    offset: usize,
}

impl Parser<'_> {
    fn error(&self, kind: ErrorKind) -> Error {
        Error {
            offset: self.offset,
            kind,
        }
    }

    fn error_at(&self, offset: usize, kind: ErrorKind) -> Error {
        Error { offset, kind }
    }

    fn peek(&self) -> Option<u8> {
        self.document.get(self.offset).copied()
    }

    fn byte(&mut self) -> Result<u8, Error> {
        let byte = self
            .peek()
            .ok_or_else(|| self.error(ErrorKind::UnexpectedEnd))?;
        self.offset += 1;
        Ok(byte)
    }

    fn expect_byte(&mut self, expected: u8, name: &'static str) -> Result<(), Error> {
        let offset = self.offset;
        let actual = self.byte()?;
        if actual != expected {
            return Err(self.error_at(offset, ErrorKind::Expected(name)));
        }
        Ok(())
    }

    fn literal(&mut self, literal: &[u8]) -> Result<(), Error> {
        let end = self
            .offset
            .checked_add(literal.len())
            .ok_or_else(|| self.error(ErrorKind::UnexpectedEnd))?;
        if self.document.get(self.offset..end) != Some(literal) {
            return Err(self.error(ErrorKind::Expected("literal")));
        }
        self.offset = end;
        Ok(())
    }

    fn value(&mut self, depth: usize) -> Result<Span, Error> {
        if depth > MAX_DEPTH {
            return Err(self.error(ErrorKind::NestingLimit));
        }
        let start = self.offset;
        match self
            .peek()
            .ok_or_else(|| self.error(ErrorKind::UnexpectedEnd))?
        {
            b'"' => {
                self.string()?;
            }
            b'0'..=b'9' => {
                self.number()?;
            }
            b'f' => self.literal(b"false")?,
            b't' => self.literal(b"true")?,
            b'[' => self.array(depth + 1)?,
            b'{' => self.object(depth + 1)?,
            other => return Err(self.error(ErrorKind::UnexpectedByte(other))),
        }
        Ok(Span {
            start,
            end: self.offset,
        })
    }

    fn string(&mut self) -> Result<String, Error> {
        self.expect_byte(b'"', "string")?;
        let mut output = Vec::new();
        loop {
            let offset = self.offset;
            let byte = self.byte()?;
            match byte {
                b'"' => break,
                b'\\' => {
                    let escaped = self.byte()?;
                    match escaped {
                        b'"' | b'\\' => output.push(escaped),
                        other => return Err(self.error_at(offset, ErrorKind::InvalidEscape(other))),
                    }
                }
                0x20..=0x7e => output.push(byte),
                other => {
                    return Err(self.error_at(offset, ErrorKind::NonPrintableStringByte(other)));
                }
            }
        }
        Ok(String::from_utf8(output).expect("printable ASCII is UTF-8"))
    }

    fn number(&mut self) -> Result<u64, Error> {
        let start = self.offset;
        let first = self.byte()?;
        if first == b'0' {
            if matches!(self.peek(), Some(b'0'..=b'9')) {
                return Err(self.error_at(start, ErrorKind::NumberLeadingZero));
            }
            return Ok(0);
        }
        if !(b'1'..=b'9').contains(&first) {
            return Err(self.error_at(start, ErrorKind::Expected("unsigned integer")));
        }
        let mut value = u64::from(first - b'0');
        while let Some(byte @ b'0'..=b'9') = self.peek() {
            self.offset += 1;
            value = value
                .checked_mul(10)
                .and_then(|value| value.checked_add(u64::from(byte - b'0')))
                .ok_or_else(|| self.error_at(start, ErrorKind::NumberOverflow))?;
        }
        Ok(value)
    }

    fn array(&mut self, depth: usize) -> Result<(), Error> {
        self.expect_byte(b'[', "array")?;
        if self.peek() == Some(b']') {
            self.offset += 1;
            return Ok(());
        }
        loop {
            self.value(depth)?;
            match self.byte()? {
                b',' => continue,
                b']' => return Ok(()),
                other => {
                    return Err(self.error_at(self.offset - 1, ErrorKind::UnexpectedByte(other)));
                }
            }
        }
    }

    fn object(&mut self, depth: usize) -> Result<(), Error> {
        self.expect_byte(b'{', "object")?;
        if self.peek() == Some(b'}') {
            self.offset += 1;
            return Ok(());
        }
        let mut previous: Option<Vec<u8>> = None;
        loop {
            let key_offset = self.offset;
            let key = self.string()?.into_bytes();
            if previous.as_deref().is_some_and(|old| old >= key.as_slice()) {
                return Err(self.error_at(key_offset, ErrorKind::ObjectKeyNotStrictlyOrdered));
            }
            previous = Some(key);
            self.expect_byte(b':', "colon")?;
            self.value(depth)?;
            match self.byte()? {
                b',' => continue,
                b'}' => return Ok(()),
                other => {
                    return Err(self.error_at(self.offset - 1, ErrorKind::UnexpectedByte(other)));
                }
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn validates_only_frozen_canonical_profile() {
        let bytes = br#"{"a":[0,true,false,"x\\\""]}"#;
        let root = validate(bytes).unwrap();
        let fields = object_fields(bytes, root).unwrap();
        require_fields(&fields, &["a"]).unwrap();
        assert_eq!(
            array_items(bytes, field(&fields, "a").unwrap())
                .unwrap()
                .len(),
            4
        );

        for rejected in [
            br#"{"b":0,"a":1}"#.as_slice(),
            br#"{"a":01}"#,
            br#"{"a":null}"#,
            br#"{ "a":0}"#,
            br#"{"a":"\n"}"#,
        ] {
            assert!(validate(rejected).is_err(), "accepted {:?}", rejected);
        }
    }
}
