//! Strict lowercase hexadecimal codec used by the frozen registries.

use core::fmt;

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum HexError {
    OddLength,
    InvalidDigit { offset: usize, byte: u8 },
    WrongLength { expected: usize, actual: usize },
}

impl fmt::Display for HexError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::OddLength => f.write_str("hex input has odd length"),
            Self::InvalidDigit { offset, byte } => {
                write!(
                    f,
                    "invalid lowercase hex byte 0x{byte:02x} at offset {offset}"
                )
            }
            Self::WrongLength { expected, actual } => {
                write!(f, "wrong decoded length: expected {expected}, got {actual}")
            }
        }
    }
}

impl std::error::Error for HexError {}

fn nibble(byte: u8, offset: usize) -> Result<u8, HexError> {
    match byte {
        b'0'..=b'9' => Ok(byte - b'0'),
        b'a'..=b'f' => Ok(byte - b'a' + 10),
        _ => Err(HexError::InvalidDigit { offset, byte }),
    }
}

pub fn decode(input: &str) -> Result<Vec<u8>, HexError> {
    let bytes = input.as_bytes();
    if !bytes.len().is_multiple_of(2) {
        return Err(HexError::OddLength);
    }
    let mut output = Vec::with_capacity(bytes.len() / 2);
    for offset in (0..bytes.len()).step_by(2) {
        output.push((nibble(bytes[offset], offset)? << 4) | nibble(bytes[offset + 1], offset + 1)?);
    }
    Ok(output)
}

pub fn decode_array<const N: usize>(input: &str) -> Result<[u8; N], HexError> {
    let decoded = decode(input)?;
    if decoded.len() != N {
        return Err(HexError::WrongLength {
            expected: N,
            actual: decoded.len(),
        });
    }
    let mut output = [0_u8; N];
    output.copy_from_slice(&decoded);
    Ok(output)
}

pub fn encode(bytes: &[u8]) -> String {
    const DIGITS: &[u8; 16] = b"0123456789abcdef";
    let mut output = String::with_capacity(bytes.len() * 2);
    for byte in bytes {
        output.push(char::from(DIGITS[usize::from(byte >> 4)]));
        output.push(char::from(DIGITS[usize::from(byte & 0x0f)]));
    }
    output
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn strict_lowercase_round_trip() {
        assert_eq!(decode("00017fff").unwrap(), [0, 1, 0x7f, 0xff]);
        assert_eq!(encode(&[0, 1, 0x7f, 0xff]), "00017fff");
        assert!(decode("AA").is_err());
        assert!(decode("0").is_err());
    }
}
