//! Typed access to the authoritative frozen `R01B-S1.json` artifact.

use core::fmt;
use std::collections::BTreeMap;

use crate::{
    FROZEN_S1_LENGTH, FROZEN_S1_SHA256, SEMANTIC_SUITE_DIGEST_HEX,
    descriptor::{self, DescriptorTemplate},
    fixture::{PublicationFixture, RecoveryFixture},
    hex, json,
    service::BResponseComponents,
    sha256,
};

pub const SCHEMA_ID: &str = "R01B-S1-1";
pub const DESCRIPTOR_ROW_COUNT: usize = 6318;
pub const RECOVERY_RECIPE_COUNT: usize = 1172;
pub const COMPARISON_EDGE_COUNT: usize = 2010;
pub const MEASUREMENT_PATH_COUNT: u64 = 1040;
pub const MEASUREMENT_FIXTURE_SHA256: &str =
    "61f7ae84cb1e39eeca445dcbb0794b1933287c6ab78591718bb2e91192d3e06d";

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum Error {
    Json(json::Error),
    Hex(hex::HexError),
    Tv(crate::tv::Error),
    Descriptor(descriptor::Error),
    Fixture(crate::fixture::Error),
    WrongFileLength {
        expected: usize,
        actual: usize,
    },
    WrongFileHash,
    WrongLiteral {
        field: &'static str,
        expected: String,
        actual: String,
    },
    WrongCount {
        field: &'static str,
        expected: usize,
        actual: usize,
    },
    WrongOrdinal {
        expected: usize,
        actual: u64,
    },
    WrongTrialId,
    WrongHistoryProduction,
    DuplicateCaseId,
    DuplicateTrialId,
    WrongExpectedShape,
    MissingLiteralOracle(String),
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Json(error) => write!(f, "{error}"),
            Self::Hex(error) => write!(f, "{error}"),
            Self::Tv(error) => write!(f, "{error}"),
            Self::Descriptor(error) => write!(f, "{error}"),
            Self::Fixture(error) => write!(f, "{error}"),
            Self::WrongFileLength { expected, actual } => {
                write!(f, "S1 length differs: expected {expected}, got {actual}")
            }
            Self::WrongFileHash => f.write_str("S1 SHA-256 differs from the frozen closure"),
            Self::WrongLiteral {
                field,
                expected,
                actual,
            } => {
                write!(f, "{field} differs: expected {expected:?}, got {actual:?}")
            }
            Self::WrongCount {
                field,
                expected,
                actual,
            } => {
                write!(
                    f,
                    "{field} count differs: expected {expected}, got {actual}"
                )
            }
            Self::WrongOrdinal { expected, actual } => {
                write!(
                    f,
                    "descriptor ordinal differs: expected {expected}, got {actual}"
                )
            }
            Self::WrongTrialId => f.write_str("recorded trial ID differs from descriptor TV hash"),
            Self::WrongHistoryProduction => {
                f.write_str("row history production differs from decoded descriptor")
            }
            Self::DuplicateCaseId => f.write_str("duplicate case ID"),
            Self::DuplicateTrialId => f.write_str("duplicate or unsorted trial ID"),
            Self::WrongExpectedShape => {
                f.write_str("literal B expectation has the wrong closed shape")
            }
            Self::MissingLiteralOracle(case_id) => {
                write!(f, "no literal oracle row for {case_id}")
            }
        }
    }
}

impl std::error::Error for Error {}

macro_rules! from_error {
    ($source:ty, $variant:ident) => {
        impl From<$source> for Error {
            fn from(value: $source) -> Self {
                Self::$variant(value)
            }
        }
    };
}

from_error!(json::Error, Json);
from_error!(hex::HexError, Hex);
from_error!(crate::tv::Error, Tv);
from_error!(descriptor::Error, Descriptor);
from_error!(crate::fixture::Error, Fixture);

#[derive(Clone, Copy, Debug)]
pub struct S1Document<'a> {
    bytes: &'a [u8],
    descriptor_registry: json::Span,
    fixture_registry: json::Span,
    literal_oracle_registry: json::Span,
    measurement_base_fixture: json::Span,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct RecordVector {
    pub payload: Vec<u8>,
    pub record: Vec<u8>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct PublicationSetupVector {
    pub setup: String,
    pub fixture: PublicationFixture,
    pub fixture_tv: Vec<u8>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct RecoveryRecipeVector {
    pub fixture: RecoveryFixture,
    pub fixture_tv: Vec<u8>,
    pub recipe_tv: Vec<u8>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct FixtureVectors {
    pub publication_setups: Vec<PublicationSetupVector>,
    pub record_by_payload: Vec<RecordVector>,
    pub recovery_recipes: Vec<RecoveryRecipeVector>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct DescriptorRow {
    pub case_id: String,
    pub comparison_edge_ids: Vec<String>,
    pub comparison_partner_case_ids: Vec<String>,
    pub descriptor_template_tv: Vec<u8>,
    pub expected_reachability: Option<String>,
    pub history_production: String,
    pub ordinal: u64,
    pub trial_id: String,
    pub descriptor: DescriptorTemplate,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct ComparisonEdge {
    pub edge_id: String,
    pub expected_result: EdgeResult,
    pub left_case_id: String,
    pub relation: String,
    pub right_case_id: String,
    pub scope: String,
    pub smallest_witness_order: Vec<String>,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum EdgeResult {
    Match,
    Differ,
    Unknown,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum LiteralBExpectation {
    Exact(BResponseComponents),
    NoBHistory { reason: String },
    LabOnly,
}

impl<'a> S1Document<'a> {
    /// Validate the exact frozen file hash, canonical JSON grammar, top-level
    /// closed shape, suite ID, schema ID, and fixed registry counts.
    pub fn parse_frozen(bytes: &'a [u8]) -> Result<Self, Error> {
        if bytes.len() != FROZEN_S1_LENGTH {
            return Err(Error::WrongFileLength {
                expected: FROZEN_S1_LENGTH,
                actual: bytes.len(),
            });
        }
        if sha256::digest(bytes) != FROZEN_S1_SHA256 {
            return Err(Error::WrongFileHash);
        }
        let root = json::validate(bytes)?;
        let fields = json::object_fields(bytes, root)?;
        json::require_fields(
            &fields,
            &[
                "descriptor_registry",
                "fixture_and_mutation_registry",
                "literal_oracle_registry",
                "measurement_base_fixture",
                "schema_id",
                "semantic_suite_digest",
            ],
        )?;
        check_string(
            bytes,
            json::field(&fields, "schema_id")?,
            "schema_id",
            SCHEMA_ID,
        )?;
        check_string(
            bytes,
            json::field(&fields, "semantic_suite_digest")?,
            "semantic_suite_digest",
            SEMANTIC_SUITE_DIGEST_HEX,
        )?;
        let document = Self {
            bytes,
            descriptor_registry: json::field(&fields, "descriptor_registry")?,
            fixture_registry: json::field(&fields, "fixture_and_mutation_registry")?,
            literal_oracle_registry: json::field(&fields, "literal_oracle_registry")?,
            measurement_base_fixture: json::field(&fields, "measurement_base_fixture")?,
        };
        document.validate_counts_and_measurement()?;
        Ok(document)
    }

    pub fn bytes(&self) -> &'a [u8] {
        self.bytes
    }

    pub fn fixture_vectors(&self) -> Result<FixtureVectors, Error> {
        let fields = json::object_fields(self.bytes, self.fixture_registry)?;
        json::require_fields(
            &fields,
            &[
                "publication_setups",
                "record_by_payload",
                "recovery_recipes",
            ],
        )?;

        let mut publication_setups = Vec::new();
        for span in json::array_items(self.bytes, json::field(&fields, "publication_setups")?)? {
            let row = json::object_fields(self.bytes, span)?;
            json::require_fields(&row, &["fixture_tv_hex", "setup"])?;
            let fixture_tv = hex_string(self.bytes, json::field(&row, "fixture_tv_hex")?)?;
            publication_setups.push(PublicationSetupVector {
                setup: json::string_value(self.bytes, json::field(&row, "setup")?)?,
                fixture: PublicationFixture::decode_tv(&fixture_tv)?,
                fixture_tv,
            });
        }

        let mut record_by_payload = Vec::new();
        for span in json::array_items(self.bytes, json::field(&fields, "record_by_payload")?)? {
            let row = json::object_fields(self.bytes, span)?;
            json::require_fields(&row, &["payload_hex", "record_hex"])?;
            record_by_payload.push(RecordVector {
                payload: hex_string(self.bytes, json::field(&row, "payload_hex")?)?,
                record: hex_string(self.bytes, json::field(&row, "record_hex")?)?,
            });
        }

        let mut recovery_recipes = Vec::new();
        for span in json::array_items(self.bytes, json::field(&fields, "recovery_recipes")?)? {
            let row = json::object_fields(self.bytes, span)?;
            json::require_fields(&row, &["fixture_tv_hex", "recipe_tv_hex"])?;
            let fixture_tv = hex_string(self.bytes, json::field(&row, "fixture_tv_hex")?)?;
            recovery_recipes.push(RecoveryRecipeVector {
                fixture: RecoveryFixture::decode_tv(&fixture_tv)?,
                fixture_tv,
                recipe_tv: hex_string(self.bytes, json::field(&row, "recipe_tv_hex")?)?,
            });
        }
        Ok(FixtureVectors {
            publication_setups,
            record_by_payload,
            recovery_recipes,
        })
    }

    pub fn descriptor_rows(&self) -> Result<Vec<DescriptorRow>, Error> {
        let registry = json::object_fields(self.bytes, self.descriptor_registry)?;
        json::require_fields(&registry, &["row_count", "rows"])?;
        let spans = json::array_items(self.bytes, json::field(&registry, "rows")?)?;
        let mut rows = Vec::with_capacity(spans.len());
        let mut previous_trial_id: Option<String> = None;
        let mut case_ids = std::collections::BTreeSet::new();
        for (ordinal, span) in spans.into_iter().enumerate() {
            let fields = json::object_fields(self.bytes, span)?;
            let expected_reachability = match fields.len() {
                7 => {
                    json::require_fields(
                        &fields,
                        &[
                            "case_id",
                            "comparison_edge_ids",
                            "comparison_partner_case_ids",
                            "descriptor_template_tv_hex",
                            "history_production",
                            "ordinal",
                            "trial_id",
                        ],
                    )?;
                    None
                }
                8 => {
                    json::require_fields(
                        &fields,
                        &[
                            "case_id",
                            "comparison_edge_ids",
                            "comparison_partner_case_ids",
                            "descriptor_template_tv_hex",
                            "expected_reachability",
                            "history_production",
                            "ordinal",
                            "trial_id",
                        ],
                    )?;
                    Some(json::string_value(
                        self.bytes,
                        json::field(&fields, "expected_reachability")?,
                    )?)
                }
                _ => {
                    return Err(Error::Json(json::Error {
                        offset: span.start,
                        kind: json::ErrorKind::WrongFields,
                    }));
                }
            };
            let case_id = json::string_value(self.bytes, json::field(&fields, "case_id")?)?;
            if !case_ids.insert(case_id.clone()) {
                return Err(Error::DuplicateCaseId);
            }
            let trial_id = json::string_value(self.bytes, json::field(&fields, "trial_id")?)?;
            if previous_trial_id
                .as_deref()
                .is_some_and(|previous| previous.as_bytes() >= trial_id.as_bytes())
            {
                return Err(Error::DuplicateTrialId);
            }
            previous_trial_id = Some(trial_id.clone());
            let recorded_ordinal = json::u64_value(self.bytes, json::field(&fields, "ordinal")?)?;
            if recorded_ordinal != ordinal as u64 {
                return Err(Error::WrongOrdinal {
                    expected: ordinal,
                    actual: recorded_ordinal,
                });
            }
            let descriptor_template_tv = hex_string(
                self.bytes,
                json::field(&fields, "descriptor_template_tv_hex")?,
            )?;
            if descriptor::trial_id(&descriptor_template_tv) != trial_id {
                return Err(Error::WrongTrialId);
            }
            let descriptor = DescriptorTemplate::decode_exact(&descriptor_template_tv)?;
            if descriptor.case_id() != case_id {
                return Err(Error::WrongHistoryProduction);
            }
            let history_production =
                json::string_value(self.bytes, json::field(&fields, "history_production")?)?;
            let decoded_production = match &descriptor {
                DescriptorTemplate::Publication(_) => "PUBLICATION",
                DescriptorTemplate::RecoveryOnly(_) => "RECOVERY_ONLY",
                DescriptorTemplate::LabOnly { .. } => "LAB_ONLY",
            };
            if decoded_production != history_production {
                return Err(Error::WrongHistoryProduction);
            }
            rows.push(DescriptorRow {
                case_id,
                comparison_edge_ids: string_array(
                    self.bytes,
                    json::field(&fields, "comparison_edge_ids")?,
                )?,
                comparison_partner_case_ids: string_array(
                    self.bytes,
                    json::field(&fields, "comparison_partner_case_ids")?,
                )?,
                descriptor_template_tv,
                expected_reachability,
                history_production,
                ordinal: recorded_ordinal,
                trial_id,
                descriptor,
            });
        }
        Ok(rows)
    }

    pub fn literal_b_expectations(&self) -> Result<BTreeMap<String, LiteralBExpectation>, Error> {
        let registry = json::object_fields(self.bytes, self.literal_oracle_registry)?;
        json::require_fields(&registry, &["comparison_edges", "rows"])?;
        let spans = json::array_items(self.bytes, json::field(&registry, "rows")?)?;
        let mut output = BTreeMap::new();
        for span in spans {
            let row = json::object_fields(self.bytes, span)?;
            json::require_fields(&row, &["case_id", "expected"])?;
            let case_id = json::string_value(self.bytes, json::field(&row, "case_id")?)?;
            let expected = json::object_fields(self.bytes, json::field(&row, "expected")?)?;
            let expectation = match expected
                .binary_search_by(|(candidate, _)| candidate.as_bytes().cmp(b"b_expectation"))
            {
                Err(_) => LiteralBExpectation::LabOnly,
                Ok(index) => parse_b_expectation(self.bytes, expected[index].1)?,
            };
            if output.insert(case_id, expectation).is_some() {
                return Err(Error::DuplicateCaseId);
            }
        }
        Ok(output)
    }

    pub fn comparison_edges(&self) -> Result<Vec<ComparisonEdge>, Error> {
        let registry = json::object_fields(self.bytes, self.literal_oracle_registry)?;
        json::require_fields(&registry, &["comparison_edges", "rows"])?;
        let spans = json::array_items(self.bytes, json::field(&registry, "comparison_edges")?)?;
        let mut edges = Vec::with_capacity(spans.len());
        let mut previous: Option<String> = None;
        for span in spans {
            let fields = json::object_fields(self.bytes, span)?;
            json::require_fields(
                &fields,
                &[
                    "edge_id",
                    "expected_result",
                    "identity",
                    "smallest_witness_order",
                ],
            )?;
            let edge_id = json::string_value(self.bytes, json::field(&fields, "edge_id")?)?;
            if previous
                .as_deref()
                .is_some_and(|old| old.as_bytes() >= edge_id.as_bytes())
            {
                return Err(Error::DuplicateTrialId);
            }
            previous = Some(edge_id.clone());
            let expected_text =
                json::string_value(self.bytes, json::field(&fields, "expected_result")?)?;
            let expected_result = match expected_text.as_str() {
                "MATCH" => EdgeResult::Match,
                "DIFFER" => EdgeResult::Differ,
                "UNKNOWN" => EdgeResult::Unknown,
                _ => return Err(Error::WrongExpectedShape),
            };
            let identity = json::object_fields(self.bytes, json::field(&fields, "identity")?)?;
            json::require_fields(
                &identity,
                &["left_case_id", "relation", "right_case_id", "scope"],
            )?;
            edges.push(ComparisonEdge {
                edge_id,
                expected_result,
                left_case_id: json::string_value(
                    self.bytes,
                    json::field(&identity, "left_case_id")?,
                )?,
                relation: json::string_value(self.bytes, json::field(&identity, "relation")?)?,
                right_case_id: json::string_value(
                    self.bytes,
                    json::field(&identity, "right_case_id")?,
                )?,
                scope: json::string_value(self.bytes, json::field(&identity, "scope")?)?,
                smallest_witness_order: string_array(
                    self.bytes,
                    json::field(&fields, "smallest_witness_order")?,
                )?,
            });
        }
        Ok(edges)
    }

    fn validate_counts_and_measurement(&self) -> Result<(), Error> {
        let descriptors = json::object_fields(self.bytes, self.descriptor_registry)?;
        json::require_fields(&descriptors, &["row_count", "rows"])?;
        let declared =
            json::u64_value(self.bytes, json::field(&descriptors, "row_count")?)? as usize;
        if declared != DESCRIPTOR_ROW_COUNT {
            return Err(Error::WrongCount {
                field: "descriptor_registry.row_count",
                expected: DESCRIPTOR_ROW_COUNT,
                actual: declared,
            });
        }
        let actual = json::array_items(self.bytes, json::field(&descriptors, "rows")?)?.len();
        if actual != DESCRIPTOR_ROW_COUNT {
            return Err(Error::WrongCount {
                field: "descriptor_registry.rows",
                expected: DESCRIPTOR_ROW_COUNT,
                actual,
            });
        }

        let fixtures = json::object_fields(self.bytes, self.fixture_registry)?;
        json::require_fields(
            &fixtures,
            &[
                "publication_setups",
                "record_by_payload",
                "recovery_recipes",
            ],
        )?;
        for (field_name, expected) in [
            ("publication_setups", 4),
            ("record_by_payload", 2),
            ("recovery_recipes", RECOVERY_RECIPE_COUNT),
        ] {
            let actual = json::array_items(self.bytes, json::field(&fixtures, field_name)?)?.len();
            if actual != expected {
                return Err(Error::WrongCount {
                    field: field_name,
                    expected,
                    actual,
                });
            }
        }

        let literal = json::object_fields(self.bytes, self.literal_oracle_registry)?;
        json::require_fields(&literal, &["comparison_edges", "rows"])?;
        for (field_name, expected) in [
            ("comparison_edges", COMPARISON_EDGE_COUNT),
            ("rows", DESCRIPTOR_ROW_COUNT),
        ] {
            let actual = json::array_items(self.bytes, json::field(&literal, field_name)?)?.len();
            if actual != expected {
                return Err(Error::WrongCount {
                    field: field_name,
                    expected,
                    actual,
                });
            }
        }

        let measurement = json::object_fields(self.bytes, self.measurement_base_fixture)?;
        json::require_fields(
            &measurement,
            &["fixture_tv_hex", "fixture_tv_sha256", "path_count"],
        )?;
        check_string(
            self.bytes,
            json::field(&measurement, "fixture_tv_sha256")?,
            "measurement.fixture_tv_sha256",
            MEASUREMENT_FIXTURE_SHA256,
        )?;
        let path_count = json::u64_value(self.bytes, json::field(&measurement, "path_count")?)?;
        if path_count != MEASUREMENT_PATH_COUNT {
            return Err(Error::WrongCount {
                field: "measurement.path_count",
                expected: MEASUREMENT_PATH_COUNT as usize,
                actual: path_count as usize,
            });
        }
        let fixture = hex_string(self.bytes, json::field(&measurement, "fixture_tv_hex")?)?;
        if hex::encode(&sha256::digest(&fixture)) != MEASUREMENT_FIXTURE_SHA256 {
            return Err(Error::WrongFileHash);
        }
        // Decode the exact base to ensure its TV framing is independently accepted.
        crate::tv::decode_exact(&fixture)?;
        Ok(())
    }
}

fn parse_b_expectation(bytes: &[u8], span: json::Span) -> Result<LiteralBExpectation, Error> {
    let fields = json::object_fields(bytes, span)?;
    let kind = json::string_value(bytes, json::field(&fields, "kind")?)?;
    match kind.as_str() {
        "EXACT" => {
            json::require_fields(
                &fields,
                &[
                    "history_production",
                    "kind",
                    "publish_result_hex_list",
                    "recovery_observation_hex",
                ],
            )?;
            let publish_result_hex_list =
                json::array_items(bytes, json::field(&fields, "publish_result_hex_list")?)?
                    .into_iter()
                    .map(|span| hex_string(bytes, span))
                    .collect::<Result<Vec<_>, _>>()?;
            if publish_result_hex_list.len() > 1 {
                return Err(Error::WrongExpectedShape);
            }
            Ok(LiteralBExpectation::Exact(BResponseComponents {
                publish_result_list: publish_result_hex_list,
                recovery_observation: hex_string(
                    bytes,
                    json::field(&fields, "recovery_observation_hex")?,
                )?,
            }))
        }
        "NO_B_HISTORY" => {
            json::require_fields(&fields, &["kind", "reason"])?;
            Ok(LiteralBExpectation::NoBHistory {
                reason: json::string_value(bytes, json::field(&fields, "reason")?)?,
            })
        }
        _ => Err(Error::WrongExpectedShape),
    }
}

fn check_string(
    bytes: &[u8],
    span: json::Span,
    field: &'static str,
    expected: &str,
) -> Result<(), Error> {
    let actual = json::string_value(bytes, span)?;
    if actual != expected {
        return Err(Error::WrongLiteral {
            field,
            expected: expected.to_owned(),
            actual,
        });
    }
    Ok(())
}

fn hex_string(bytes: &[u8], span: json::Span) -> Result<Vec<u8>, Error> {
    Ok(hex::decode(&json::string_value(bytes, span)?)?)
}

fn string_array(bytes: &[u8], span: json::Span) -> Result<Vec<String>, Error> {
    json::array_items(bytes, span)?
        .into_iter()
        .map(|item| json::string_value(bytes, item).map_err(Error::from))
        .collect()
}
