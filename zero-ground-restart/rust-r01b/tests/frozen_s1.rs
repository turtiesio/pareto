use std::{fs, path::Path};

use rust_r01b::{
    descriptor::DescriptorTemplate,
    fixture::PublicationSetup,
    record,
    s1::{EdgeResult, LiteralBExpectation, S1Document},
    service::{self, ComparisonResult, ServiceResult},
};

fn frozen_s1() -> Vec<u8> {
    fs::read(Path::new(env!("CARGO_MANIFEST_DIR")).join("../R01B-S1.json"))
        .expect("frozen S1 artifact must be adjacent to the crate")
}

#[test]
fn independently_decodes_all_frozen_vectors_and_descriptor_templates() {
    let bytes = frozen_s1();
    let document = S1Document::parse_frozen(&bytes).unwrap();
    let fixtures = document.fixture_vectors().unwrap();
    assert_eq!(fixtures.record_by_payload.len(), 2);
    for vector in &fixtures.record_by_payload {
        assert_eq!(record::encode(&vector.payload).unwrap(), vector.record);
        assert_eq!(
            record::parse(&vector.record).unwrap().payload,
            vector.payload
        );
    }
    for vector in &fixtures.publication_setups {
        let expected = PublicationSetup::parse(&vector.setup).unwrap().fixture();
        assert_eq!(vector.fixture, expected);
        assert_eq!(expected.encode_tv().unwrap(), vector.fixture_tv);
    }
    assert_eq!(fixtures.recovery_recipes.len(), 1172);
    let unique_fixture_bytes = fixtures
        .recovery_recipes
        .iter()
        .map(|vector| vector.fixture_tv.as_slice())
        .collect::<std::collections::BTreeSet<_>>();
    assert_eq!(unique_fixture_bytes.len(), 1137);
    for vector in &fixtures.recovery_recipes {
        assert_eq!(vector.fixture.encode_tv().unwrap(), vector.fixture_tv);
        // Recipe bytes are authoritative typed values, not interpreted as an
        // ambient mutation grammar by this realization.
        rust_r01b::tv::decode_exact(&vector.recipe_tv).unwrap();
    }

    let rows = document.descriptor_rows().unwrap();
    assert_eq!(rows.len(), 6318);
    assert_eq!(
        rows.iter()
            .filter(|row| matches!(row.descriptor, DescriptorTemplate::Publication(_)))
            .count(),
        684
    );
    assert_eq!(
        rows.iter()
            .filter(|row| matches!(row.descriptor, DescriptorTemplate::RecoveryOnly(_)))
            .count(),
        2344
    );

    let edges = document.comparison_edges().unwrap();
    assert_eq!(edges.len(), 2010);
}

#[test]
fn pure_service_components_match_every_subject_literal_vector() {
    let bytes = frozen_s1();
    let document = S1Document::parse_frozen(&bytes).unwrap();
    let rows = document.descriptor_rows().unwrap();
    let literal = document.literal_b_expectations().unwrap();

    for row in rows {
        let expected = literal
            .get(&row.case_id)
            .expect("one literal row per descriptor");
        match (&row.descriptor, expected) {
            (DescriptorTemplate::Publication(descriptor), LiteralBExpectation::Exact(expected)) => {
                let actual = service::publish_model(descriptor);
                assert_eq!(
                    actual,
                    ServiceResult::Complete(expected.clone()),
                    "publication mismatch for {}",
                    row.case_id
                );
            }
            (
                DescriptorTemplate::Publication(descriptor),
                LiteralBExpectation::NoBHistory { .. },
            ) => {
                assert_eq!(
                    service::publish_model(descriptor),
                    ServiceResult::ControlUnavailable,
                    "control-unavailable mismatch for {}",
                    row.case_id
                );
            }
            (
                DescriptorTemplate::RecoveryOnly(descriptor),
                LiteralBExpectation::Exact(expected),
            ) => {
                let observation =
                    service::recover(&descriptor.recovery_fixture, &descriptor.continuation)
                        .unwrap();
                let actual = service::BResponseComponents::from_values(None, observation);
                assert_eq!(&actual, expected, "recovery mismatch for {}", row.case_id);
            }
            (DescriptorTemplate::LabOnly { .. }, LiteralBExpectation::LabOnly) => {}
            _ => panic!("descriptor/literal production mismatch for {}", row.case_id),
        }
    }

    for edge in document.comparison_edges().unwrap() {
        let left = match literal.get(&edge.left_case_id).unwrap() {
            LiteralBExpectation::Exact(value) => Some(value),
            _ => None,
        };
        let right = match literal.get(&edge.right_case_id).unwrap() {
            LiteralBExpectation::Exact(value) => Some(value),
            _ => None,
        };
        let structural = service::compare_complete_responses(left, right);
        match edge.expected_result {
            EdgeResult::Match => {
                assert_eq!(structural, ComparisonResult::Match, "{}", edge.edge_id)
            }
            EdgeResult::Differ => {
                assert_eq!(structural, ComparisonResult::Differ, "{}", edge.edge_id)
            }
            // UNKNOWN can retain equal component bytes while execution or
            // required evidence is unavailable; equality must not promote it.
            EdgeResult::Unknown => {}
        }
    }
}
