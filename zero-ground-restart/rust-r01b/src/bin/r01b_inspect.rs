use std::{env, fs, path::PathBuf, process::ExitCode};

use rust_r01b::{
    descriptor::DescriptorTemplate,
    inventory,
    s1::{LiteralBExpectation, S1Document},
};

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(error) => {
            eprintln!("r01b-inspect: {error}");
            ExitCode::FAILURE
        }
    }
}

fn run() -> Result<(), Box<dyn std::error::Error>> {
    let mut arguments = env::args_os();
    let _program = arguments.next();
    let Some(command) = arguments.next() else {
        return Err("usage: r01b-inspect validate-s1 PATH | inventory [PATH ...]".into());
    };
    match command.to_str() {
        Some("validate-s1") => {
            let path = arguments
                .next()
                .ok_or("validate-s1 requires the exact R01B-S1.json path")?;
            if arguments.next().is_some() {
                return Err("validate-s1 accepts exactly one path".into());
            }
            let bytes = fs::read(&path)?;
            let document = S1Document::parse_frozen(&bytes)?;
            let fixtures = document.fixture_vectors()?;
            let rows = document.descriptor_rows()?;
            let literal = document.literal_b_expectations()?;
            let publication = rows
                .iter()
                .filter(|row| matches!(row.descriptor, DescriptorTemplate::Publication(_)))
                .count();
            let recovery = rows
                .iter()
                .filter(|row| matches!(row.descriptor, DescriptorTemplate::RecoveryOnly(_)))
                .count();
            let lab = rows.len() - publication - recovery;
            let exact = literal
                .values()
                .filter(|value| matches!(value, LiteralBExpectation::Exact(_)))
                .count();
            let no_b = literal
                .values()
                .filter(|value| matches!(value, LiteralBExpectation::NoBHistory { .. }))
                .count();
            println!("S1 exact bytes validated");
            println!(
                "descriptors={} publication={} recovery_only={} lab_only={}",
                rows.len(),
                publication,
                recovery,
                lab
            );
            println!(
                "literal_exact={} literal_no_b={} literal_lab={}",
                exact,
                no_b,
                literal.len() - exact - no_b
            );
            println!(
                "record_vectors={} publication_setups={} recovery_recipes={}",
                fixtures.record_by_payload.len(),
                fixtures.publication_setups.len(),
                fixtures.recovery_recipes.len()
            );
        }
        Some("inventory") => {
            let explicit: Vec<PathBuf> = arguments.map(PathBuf::from).collect();
            for observation in inventory::observe_files(&explicit)? {
                println!(
                    "FILE\t{}\t{}\t{}",
                    observation.byte_length,
                    observation.sha256_hex(),
                    observation.path.display()
                );
            }
            let process = inventory::current_process_inventory();
            for observation in process.files {
                println!(
                    "LOADED\t{}\t{}\t{}",
                    observation.byte_length,
                    observation.sha256_hex(),
                    observation.path.display()
                );
            }
            for unknown in process.unknown {
                println!(
                    "UNKNOWN\t{}\t{}\t{}",
                    unknown.component, unknown.reason, unknown.needed_evidence
                );
            }
        }
        _ => {
            return Err("usage: r01b-inspect validate-s1 PATH | inventory [PATH ...]".into());
        }
    }
    Ok(())
}
