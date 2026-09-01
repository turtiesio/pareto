//! Exact-byte inventory primitives for the later realization gate.
//!
//! This module intentionally does not define a private realization digest or
//! gate-R identifier.  It retains exact path, length, and SHA-256 observations
//! and explicitly reports bytes that cannot be obtained.

use core::fmt;
use std::{
    collections::BTreeSet,
    fs, io,
    path::{Path, PathBuf},
};

use crate::{hex, sha256};

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct FileObservation {
    pub path: PathBuf,
    pub byte_length: u64,
    pub sha256: [u8; 32],
}

impl FileObservation {
    pub fn sha256_hex(&self) -> String {
        hex::encode(&self.sha256)
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct UnknownBytes {
    pub component: String,
    pub reason: String,
    pub needed_evidence: String,
}

#[derive(Clone, Debug, Default, Eq, PartialEq)]
pub struct LoadedByteInventory {
    pub files: Vec<FileObservation>,
    pub unknown: Vec<UnknownBytes>,
}

#[derive(Debug)]
pub enum Error {
    Io { path: PathBuf, source: io::Error },
    NonRegularFile(PathBuf),
    LengthOverflow(PathBuf),
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Io { path, source } => write!(f, "{}: {source}", path.display()),
            Self::NonRegularFile(path) => write!(f, "{} is not a regular file", path.display()),
            Self::LengthOverflow(path) => write!(f, "{} length does not fit u64", path.display()),
        }
    }
}

impl std::error::Error for Error {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        match self {
            Self::Io { source, .. } => Some(source),
            _ => None,
        }
    }
}

pub fn observe_file(path: impl AsRef<Path>) -> Result<FileObservation, Error> {
    let path = path.as_ref();
    let metadata = fs::metadata(path).map_err(|source| Error::Io {
        path: path.to_owned(),
        source,
    })?;
    if !metadata.is_file() {
        return Err(Error::NonRegularFile(path.to_owned()));
    }
    let bytes = fs::read(path).map_err(|source| Error::Io {
        path: path.to_owned(),
        source,
    })?;
    let byte_length =
        u64::try_from(bytes.len()).map_err(|_| Error::LengthOverflow(path.to_owned()))?;
    Ok(FileObservation {
        path: path.to_owned(),
        byte_length,
        sha256: sha256::digest(&bytes),
    })
}

pub fn observe_files<I, P>(paths: I) -> Result<Vec<FileObservation>, Error>
where
    I: IntoIterator<Item = P>,
    P: AsRef<Path>,
{
    let mut observations = paths
        .into_iter()
        .map(observe_file)
        .collect::<Result<Vec<_>, _>>()?;
    observations.sort_by_key(|item| path_bytes(&item.path));
    observations.dedup_by(|left, right| left.path == right.path);
    Ok(observations)
}

/// Inventory the current executable and every absolute regular pathname found
/// in Linux `/proc/self/maps`.  Anonymous mappings, kernel state, firmware,
/// hypervisor, host, controller, and physical-media bytes remain explicitly
/// unknown rather than being assigned zero cost.
pub fn current_process_inventory() -> LoadedByteInventory {
    let mut paths = BTreeSet::new();
    let mut unknown = Vec::new();
    match std::env::current_exe() {
        Ok(path) => {
            paths.insert(path);
        }
        Err(error) => unknown.push(UnknownBytes {
            component: "current executable".into(),
            reason: format!("current_exe failed: {error}"),
            needed_evidence: "readable executable pathname and bytes".into(),
        }),
    }

    match fs::read_to_string("/proc/self/maps") {
        Ok(maps) => {
            for line in maps.lines() {
                let Some(path_offset) = line.find('/') else {
                    continue;
                };
                let path = &line[path_offset..];
                if let Some(deleted) = path.strip_suffix(" (deleted)") {
                    unknown.push(UnknownBytes {
                        component: format!("deleted mapped object {deleted}"),
                        reason: "mapped file was deleted and its loaded bytes are not recoverable by pathname"
                            .into(),
                        needed_evidence: "exact object bytes captured before deletion".into(),
                    });
                } else {
                    paths.insert(PathBuf::from(path));
                }
            }
        }
        Err(error) => unknown.push(UnknownBytes {
            component: "process file-backed mappings".into(),
            reason: format!("/proc/self/maps unavailable: {error}"),
            needed_evidence: "complete loss-detecting loaded-object inventory".into(),
        }),
    }

    let mut files = Vec::new();
    for path in paths {
        match observe_file(&path) {
            Ok(observation) => files.push(observation),
            Err(error) => unknown.push(UnknownBytes {
                component: format!("mapped object {}", path.display()),
                reason: error.to_string(),
                needed_evidence: "exact loaded object bytes".into(),
            }),
        }
    }
    files.sort_by_key(|item| path_bytes(&item.path));

    for component in [
        "kernel and kernel configuration bytes",
        "OS files not surfaced as file-backed process mappings",
        "hypervisor and host bytes",
        "storage controller and firmware bytes",
        "physical-media state and behavior",
    ] {
        unknown.push(UnknownBytes {
            component: component.into(),
            reason: "not observable through this guest-process inventory".into(),
            needed_evidence: "independently retained platform and physical provenance".into(),
        });
    }
    unknown.sort_by(|left, right| left.component.as_bytes().cmp(right.component.as_bytes()));
    LoadedByteInventory { files, unknown }
}

#[cfg(unix)]
fn path_bytes(path: &Path) -> Vec<u8> {
    use std::os::unix::ffi::OsStrExt;
    path.as_os_str().as_bytes().to_vec()
}

#[cfg(not(unix))]
fn path_bytes(path: &Path) -> Vec<u8> {
    path.to_string_lossy().as_bytes().to_vec()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn observes_own_manifest_without_hash_only_substitution() {
        let path = Path::new(env!("CARGO_MANIFEST_DIR")).join("Cargo.toml");
        let observation = observe_file(path).unwrap();
        assert!(observation.byte_length > 0);
        assert_eq!(observation.sha256_hex().len(), 64);
    }
}
