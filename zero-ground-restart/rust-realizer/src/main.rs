use std::env;
use std::fs::File;
use std::io::{self, BufReader, BufWriter, Write};
use std::process::ExitCode;

use b1_realizer::{Candidate, Machine};

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(error) => {
            eprintln!("error: {error}");
            ExitCode::FAILURE
        }
    }
}

fn run() -> Result<(), Box<dyn std::error::Error>> {
    let arguments: Vec<String> = env::args().skip(1).collect();
    let Some(command) = arguments.first().map(String::as_str) else {
        return usage();
    };
    let machine = Machine::build()?;
    match (command, arguments.as_slice()) {
        ("inspect", [_]) => {
            let (minimum, maximum, total) = machine.representative_payload_stats();
            println!(
                "states={} quiescent={} classes={} refinement_rounds={} representative_min={} representative_max={} representative_total={}",
                machine.state_count(),
                machine.quiescent_count(),
                machine.class_count(),
                machine.refinement_rounds(),
                minimum,
                maximum,
                total
            );
        }
        ("produce", [_, candidate, path]) => {
            let candidate = Candidate::parse(candidate)?;
            let summary = if path == "-" {
                let stdout = io::stdout();
                let mut output = stdout.lock();
                machine.write_state_stream(candidate, &mut output)?
            } else {
                let file = File::create(path)?;
                let mut output = BufWriter::new(file);
                let summary = machine.write_state_stream(candidate, &mut output)?;
                output.flush()?;
                summary
            };
            eprintln!(
                "candidate={} records={} bytes={} state_stream_sha256={}",
                summary.candidate.name(),
                summary.records,
                summary.bytes,
                summary.sha256
            );
        }
        ("consume", [_, candidate, path]) => {
            let candidate = Candidate::parse(candidate)?;
            let (ranks, summary) = if path == "-" {
                let stdin = io::stdin();
                machine.read_state_stream(candidate, stdin.lock())?
            } else {
                machine.read_state_stream(candidate, BufReader::new(File::open(path)?))?
            };
            let transition = machine.write_transition_transcript(candidate, &ranks, io::sink())?;
            let unique_recovered_classes = {
                let mut unique = ranks;
                unique.sort_unstable();
                unique.dedup();
                unique.len()
            };
            println!(
                "candidate={} records={} bytes={} state_stream_sha256={} unique_recovered_classes={} transition_records={} transition_bytes={} transition_sha256={}",
                summary.candidate.name(),
                summary.records,
                summary.bytes,
                summary.sha256,
                unique_recovered_classes,
                transition.records,
                transition.bytes,
                transition.sha256
            );
        }
        ("transcript", [_, candidate, input_path, output_path]) => {
            let candidate = Candidate::parse(candidate)?;
            let (ranks, _) = if input_path == "-" {
                let stdin = io::stdin();
                machine.read_state_stream(candidate, stdin.lock())?
            } else {
                machine.read_state_stream(candidate, BufReader::new(File::open(input_path)?))?
            };
            let transition = if output_path == "-" {
                let stdout = io::stdout();
                machine.write_transition_transcript(candidate, &ranks, stdout.lock())?
            } else {
                let mut output = BufWriter::new(File::create(output_path)?);
                let transition =
                    machine.write_transition_transcript(candidate, &ranks, &mut output)?;
                output.flush()?;
                transition
            };
            eprintln!(
                "candidate={} transition_records={} transition_bytes={} transition_sha256={}",
                transition.candidate.name(),
                transition.records,
                transition.bytes,
                transition.sha256
            );
        }
        _ => return usage(),
    }
    Ok(())
}

fn usage<T>() -> Result<T, Box<dyn std::error::Error>> {
    Err("usage: b1-realizer inspect | produce <ordinal|representative> <path|-> | consume <ordinal|representative> <path|-> | transcript <ordinal|representative> <stream-path|-> <output-path|->".into())
}
