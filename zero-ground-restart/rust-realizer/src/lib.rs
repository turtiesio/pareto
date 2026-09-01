//! Independent, standard-library-only realization of the frozen finite B1 machine.

use std::cmp::Ordering;
use std::collections::{HashMap, VecDeque};
use std::fmt;
use std::io::{self, Read, Write};

pub const ARTIFACT_DIGEST_HEX: &str =
    "b38fc5d3e57fd0117b9ee1fd4c0d0686833115db9ce22dd5950fe6fb41a09339";
pub const EXPECTED_STATE_COUNT: usize = 82_584;
pub const EXPECTED_QUIESCENT_COUNT: usize = 10_420;
pub const OPERATION_COUNT: usize = 17;
pub const EXPECTED_ORDINAL_STREAM_BYTES: usize = 3_716_290;
pub const EXPECTED_REPRESENTATIVE_STREAM_BYTES: usize = 18_053_209;
pub const EXPECTED_ORDINAL_STREAM_SHA256: &str =
    "253cb73a89dce87bee4ed1c5c4bc22eddffbd848e3a805037d00fd71c16740ec";
pub const EXPECTED_REPRESENTATIVE_STREAM_SHA256: &str =
    "5aa508e648df5a43fd6cea5ff0552daed5faa1e9903e6841e3fde657755ef2f5";
pub const EXPECTED_ORDINAL_TRANSITION_SHA256: &str =
    "293cca6b94d8dd0e727c6ecf9d55ac0aac0dae8707a365206bf762049056aaa3";
pub const EXPECTED_REPRESENTATIVE_TRANSITION_SHA256: &str =
    "4ff1ba87a2f2f30bc1c93678e9d00a61aa3ce37a4b3dd04e65052a976b62dec6";

const ENVELOPE_MAGIC: &[u8; 4] = b"ZGPE";
const STREAM_MAGIC: &[u8; 4] = b"ZGPS";
const FORMAT_VERSION: u8 = 1;

#[derive(Clone, Copy, Debug, Eq, Hash, Ord, PartialEq, PartialOrd)]
pub enum Candidate {
    Ordinal,
    Representative,
}

impl Candidate {
    pub fn parse(value: &str) -> Result<Self, Error> {
        match value {
            "ordinal" => Ok(Self::Ordinal),
            "representative" => Ok(Self::Representative),
            _ => Err(Error::new(format!(
                "unknown candidate {value:?}; expected ordinal or representative"
            ))),
        }
    }

    pub const fn tag(self) -> u8 {
        match self {
            Self::Ordinal => 1,
            Self::Representative => 2,
        }
    }

    pub const fn name(self) -> &'static str {
        match self {
            Self::Ordinal => "ordinal",
            Self::Representative => "representative",
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct Error(String);

impl Error {
    fn new(message: impl Into<String>) -> Self {
        Self(message.into())
    }
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(&self.0)
    }
}

impl std::error::Error for Error {}

impl From<io::Error> for Error {
    fn from(value: io::Error) -> Self {
        Self(value.to_string())
    }
}

#[derive(Clone, Copy, Debug, Eq, Hash, Ord, PartialEq, PartialOrd)]
enum Source {
    A,
    B,
}

impl Source {
    const fn atom(self) -> &'static str {
        match self {
            Self::A => "a",
            Self::B => "b",
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, Hash, Ord, PartialEq, PartialOrd)]
enum Bit {
    Zero,
    One,
}

impl Bit {
    const fn atom(self) -> &'static str {
        match self {
            Self::Zero => "0",
            Self::One => "1",
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, Hash, Ord, PartialEq, PartialOrd)]
enum Rule {
    Default,
    U00,
    U01,
    V01,
}

impl Rule {
    const fn label(self) -> RuleLabel {
        match self {
            Self::Default => RuleLabel::D,
            Self::U00 | Self::U01 => RuleLabel::U,
            Self::V01 => RuleLabel::V,
        }
    }

    const fn map(self, bit: Bit) -> Bit {
        match (self, bit) {
            (Self::U00, _) | (_, Bit::Zero) => Bit::Zero,
            (_, Bit::One) => Bit::One,
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, Hash, Ord, PartialEq, PartialOrd)]
enum RuleLabel {
    D,
    U,
    V,
}

impl RuleLabel {
    const fn atom(self) -> &'static str {
        match self {
            Self::D => "d",
            Self::U => "u",
            Self::V => "v",
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, Hash, Ord, PartialEq, PartialOrd)]
enum Key {
    K,
    L,
}

impl Key {
    const fn atom(self) -> &'static str {
        match self {
            Self::K => "k",
            Self::L => "l",
        }
    }

    const fn index(self) -> usize {
        match self {
            Self::K => 0,
            Self::L => 1,
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, Hash, Ord, PartialEq, PartialOrd)]
struct Descriptor {
    source: Source,
    authored: Bit,
    rule: RuleLabel,
    interpreted: Bit,
}

impl Descriptor {
    fn from_current(source: Source, authored: Bit, rule: Rule) -> Self {
        Self {
            source,
            authored,
            rule: rule.label(),
            interpreted: rule.map(authored),
        }
    }

    fn arguments(self) -> String {
        format!(
            "{},{},{},{}",
            self.source.atom(),
            self.authored.atom(),
            self.rule.atom(),
            self.interpreted.atom()
        )
    }
}

#[derive(Clone, Copy, Debug, Eq, Hash, Ord, PartialEq, PartialOrd)]
enum Action {
    Absent,
    Pending(Descriptor),
    Done(Descriptor),
}

#[derive(Clone, Debug, Eq, Hash, Ord, PartialEq, PartialOrd)]
enum Output {
    Empty,
    Raw(Source, Bit),
    Val(Bit),
    Why(Descriptor),
    Do(Key, Descriptor),
    Already(Key, Descriptor),
    NoData(Key),
    Absent(Key),
    Pending(Key, Descriptor),
    Done(Key, Descriptor),
}

impl Output {
    fn frame(&self) -> String {
        match self {
            Self::Empty => "out:client:EMPTY".to_owned(),
            Self::Raw(source, bit) => {
                format!("out:client:RAW({},{})", source.atom(), bit.atom())
            }
            Self::Val(bit) => format!("out:client:VAL({})", bit.atom()),
            Self::Why(descriptor) => {
                format!("out:client:WHY({})", descriptor.arguments())
            }
            Self::Do(key, descriptor) => {
                format!("out:action:DO({},{})", key.atom(), descriptor.arguments())
            }
            Self::Already(key, descriptor) => format!(
                "out:client:ALREADY({},{})",
                key.atom(),
                descriptor.arguments()
            ),
            Self::NoData(key) => format!("out:client:NO_DATA({})", key.atom()),
            Self::Absent(key) => format!("out:client:ABSENT({})", key.atom()),
            Self::Pending(key, descriptor) => format!(
                "out:client:PENDING({},{})",
                key.atom(),
                descriptor.arguments()
            ),
            Self::Done(key, descriptor) => {
                format!("out:client:DONE({},{})", key.atom(), descriptor.arguments())
            }
        }
    }

    const fn is_action_port(&self) -> bool {
        matches!(self, Self::Do(_, _))
    }
}

#[derive(Clone, Debug, Eq, Hash, Ord, PartialEq, PartialOrd)]
struct State {
    current: Option<(Source, Bit)>,
    rule: Rule,
    actions: [Action; 2],
    owed: Option<Output>,
}

impl State {
    const fn initial() -> Self {
        Self {
            current: None,
            rule: Rule::Default,
            actions: [Action::Absent, Action::Absent],
            owed: None,
        }
    }

    const fn is_quiescent(&self) -> bool {
        self.owed.is_none()
    }

    fn descriptor(&self) -> Option<Descriptor> {
        self.current
            .map(|(source, bit)| Descriptor::from_current(source, bit, self.rule))
    }

    fn apply(&self, operation: Operation) -> Step {
        match operation {
            Operation::Resume => self.resume(),
            Operation::Input(input) => self.input(input),
        }
    }

    fn resume(&self) -> Step {
        let Some(output) = self.owed.clone() else {
            return Step {
                membership: None,
                client: Vec::new(),
                action: Vec::new(),
                next: self.clone(),
            };
        };
        let mut next = self.clone();
        next.owed = None;
        if let Output::Do(key, descriptor) = output {
            next.actions[key.index()] = Action::Pending(descriptor);
        }
        let frame = output.frame();
        let (client, action) = if output.is_action_port() {
            (Vec::new(), vec![frame])
        } else {
            (vec![frame], Vec::new())
        };
        Step {
            membership: None,
            client,
            action,
            next,
        }
    }

    fn input(&self, input: Input) -> Step {
        if !self.is_quiescent() || !self.input_enabled(input) {
            return Step {
                membership: Some(false),
                client: Vec::new(),
                action: Vec::new(),
                next: self.clone(),
            };
        }

        let mut next = self.clone();
        match input {
            Input::Ack(key) => {
                let Action::Pending(descriptor) = next.actions[key.index()] else {
                    unreachable!("domain checked above")
                };
                next.actions[key.index()] = Action::Done(descriptor);
            }
            Input::A(key) => {
                next.owed = Some(match self.actions[key.index()] {
                    Action::Absent => match self.descriptor() {
                        Some(descriptor) => Output::Do(key, descriptor),
                        None => Output::NoData(key),
                    },
                    Action::Pending(descriptor) => Output::Do(key, descriptor),
                    Action::Done(descriptor) => Output::Already(key, descriptor),
                });
            }
            Input::O => {
                next.owed = Some(match self.current {
                    Some((source, bit)) => Output::Raw(source, bit),
                    None => Output::Empty,
                });
            }
            Input::P(source, bit) => next.current = Some((source, bit)),
            Input::Q => {
                next.owed = Some(match self.descriptor() {
                    Some(descriptor) => Output::Val(descriptor.interpreted),
                    None => Output::Empty,
                });
            }
            Input::R(rule) => next.rule = rule,
            Input::S(key) => {
                next.owed = Some(match self.actions[key.index()] {
                    Action::Absent => Output::Absent(key),
                    Action::Pending(descriptor) => Output::Pending(key, descriptor),
                    Action::Done(descriptor) => Output::Done(key, descriptor),
                });
            }
            Input::X => {
                next.owed = Some(match self.descriptor() {
                    Some(descriptor) => Output::Why(descriptor),
                    None => Output::Empty,
                });
            }
        }
        Step {
            membership: Some(true),
            client: Vec::new(),
            action: Vec::new(),
            next,
        }
    }

    const fn input_enabled(&self, input: Input) -> bool {
        if !self.is_quiescent() {
            return false;
        }
        match input {
            Input::Ack(key) => matches!(self.actions[key.index()], Action::Pending(_)),
            _ => true,
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, Hash, Ord, PartialEq, PartialOrd)]
enum Input {
    Ack(Key),
    A(Key),
    O,
    P(Source, Bit),
    Q,
    R(Rule),
    S(Key),
    X,
}

impl Input {
    fn frame(self) -> &'static str {
        match self {
            Self::Ack(Key::K) => "in:action:ACK(k)",
            Self::Ack(Key::L) => "in:action:ACK(l)",
            Self::A(Key::K) => "in:client:A(k)",
            Self::A(Key::L) => "in:client:A(l)",
            Self::O => "in:client:O",
            Self::P(Source::A, Bit::Zero) => "in:client:P(a,0)",
            Self::P(Source::A, Bit::One) => "in:client:P(a,1)",
            Self::P(Source::B, Bit::Zero) => "in:client:P(b,0)",
            Self::P(Source::B, Bit::One) => "in:client:P(b,1)",
            Self::Q => "in:client:Q",
            Self::R(Rule::U00) => "in:client:R(u,0,0)",
            Self::R(Rule::U01) => "in:client:R(u,0,1)",
            Self::R(Rule::V01) => "in:client:R(v,0,1)",
            Self::R(Rule::Default) => unreachable!("the default rule is not an input"),
            Self::S(Key::K) => "in:client:S(k)",
            Self::S(Key::L) => "in:client:S(l)",
            Self::X => "in:client:X",
        }
    }
}

const INPUTS: [Input; 16] = [
    Input::Ack(Key::K),
    Input::Ack(Key::L),
    Input::A(Key::K),
    Input::A(Key::L),
    Input::O,
    Input::P(Source::A, Bit::Zero),
    Input::P(Source::A, Bit::One),
    Input::P(Source::B, Bit::Zero),
    Input::P(Source::B, Bit::One),
    Input::Q,
    Input::R(Rule::U00),
    Input::R(Rule::U01),
    Input::R(Rule::V01),
    Input::S(Key::K),
    Input::S(Key::L),
    Input::X,
];

#[derive(Clone, Copy, Debug, Eq, Hash, Ord, PartialEq, PartialOrd)]
enum Operation {
    Resume,
    Input(Input),
}

impl Operation {
    fn spelling(self) -> &'static str {
        match self {
            Self::Resume => "resume",
            Self::Input(input) => input.frame(),
        }
    }
}

fn operations() -> impl Iterator<Item = Operation> {
    std::iter::once(Operation::Resume).chain(INPUTS.into_iter().map(Operation::Input))
}

#[derive(Clone, Debug, Eq, PartialEq)]
struct Step {
    membership: Option<bool>,
    client: Vec<String>,
    action: Vec<String>,
    next: State,
}

#[derive(Clone, Debug)]
struct Node {
    state: State,
    representative: Vec<String>,
}

#[derive(Clone, Debug)]
pub struct Machine {
    nodes: Vec<Node>,
    state_to_node: HashMap<State, usize>,
    class_of_node: Vec<usize>,
    class_nodes: Vec<usize>,
    representative_to_class: HashMap<Vec<u8>, usize>,
    refinement_rounds: usize,
}

impl Machine {
    pub fn build() -> Result<Self, Error> {
        let (nodes, state_to_node) = enumerate_states();
        let (_initial_class_of_node, mut classes, refinement_rounds) =
            refine(&nodes, &state_to_node);

        for class in &mut classes {
            class.sort_by(|left, right| compare_representatives(&nodes[*left], &nodes[*right]));
        }
        classes.sort_by(|left, right| compare_representatives(&nodes[left[0]], &nodes[right[0]]));

        let mut reordered_class_of_node = vec![usize::MAX; nodes.len()];
        let mut class_nodes = Vec::with_capacity(classes.len());
        let mut representative_to_class = HashMap::with_capacity(classes.len());
        for (rank, class) in classes.iter().enumerate() {
            let canonical = class[0];
            class_nodes.push(canonical);
            for node in class {
                reordered_class_of_node[*node] = rank;
            }
            let bytes = representative_bytes(&nodes[canonical].representative);
            if representative_to_class.insert(bytes, rank).is_some() {
                return Err(Error::new("duplicate canonical representative"));
            }
        }

        let machine = Self {
            nodes,
            state_to_node,
            class_of_node: reordered_class_of_node,
            class_nodes,
            representative_to_class,
            refinement_rounds,
        };
        machine.validate_counts()?;
        Ok(machine)
    }

    fn validate_counts(&self) -> Result<(), Error> {
        let quiescent = self
            .nodes
            .iter()
            .filter(|node| node.state.is_quiescent())
            .count();
        if quiescent != EXPECTED_QUIESCENT_COUNT {
            return Err(Error::new(format!(
                "quiescent-state mismatch: got {quiescent}, expected {EXPECTED_QUIESCENT_COUNT}"
            )));
        }
        if self.class_nodes.len() != EXPECTED_STATE_COUNT {
            return Err(Error::new(format!(
                "stable-class mismatch: got {}, expected {EXPECTED_STATE_COUNT}",
                self.class_nodes.len()
            )));
        }
        Ok(())
    }

    pub fn state_count(&self) -> usize {
        self.nodes.len()
    }

    pub fn quiescent_count(&self) -> usize {
        self.nodes
            .iter()
            .filter(|node| node.state.is_quiescent())
            .count()
    }

    pub fn class_count(&self) -> usize {
        self.class_nodes.len()
    }

    pub fn refinement_rounds(&self) -> usize {
        self.refinement_rounds
    }

    pub fn representative_payload_stats(&self) -> (usize, usize, usize) {
        let mut minimum = usize::MAX;
        let mut maximum = 0;
        let mut total = 0;
        for rank in 0..self.class_count() {
            let length = self.representative(rank).len();
            minimum = minimum.min(length);
            maximum = maximum.max(length);
            total += length;
        }
        (minimum, maximum, total)
    }

    pub fn representative(&self, rank: usize) -> Vec<u8> {
        representative_bytes(&self.nodes[self.class_nodes[rank]].representative)
    }

    fn state(&self, rank: usize) -> &State {
        &self.nodes[self.class_nodes[rank]].state
    }

    fn successor_rank(&self, state: &State) -> usize {
        let node = self.state_to_node[state];
        self.class_of_node[node]
    }

    pub fn envelope(&self, candidate: Candidate, rank: usize) -> Vec<u8> {
        let payload = match candidate {
            Candidate::Ordinal => vec![
                ((rank >> 16) & 0xff) as u8,
                ((rank >> 8) & 0xff) as u8,
                (rank & 0xff) as u8,
            ],
            Candidate::Representative => self.representative(rank),
        };
        encode_envelope(candidate, &payload)
    }

    pub fn recover_envelope(&self, expected: Candidate, bytes: &[u8]) -> Result<usize, Error> {
        let payload = decode_envelope(expected, bytes)?;
        match expected {
            Candidate::Ordinal => {
                if payload.len() != 3 {
                    return Err(Error::new(format!(
                        "ordinal payload length {}, expected 3",
                        payload.len()
                    )));
                }
                let rank = ((payload[0] as usize) << 16)
                    | ((payload[1] as usize) << 8)
                    | payload[2] as usize;
                if rank >= self.class_count() {
                    return Err(Error::new(format!(
                        "ordinal rank {rank} is outside 0..{}",
                        self.class_count()
                    )));
                }
                Ok(rank)
            }
            Candidate::Representative => self
                .representative_to_class
                .get(payload)
                .copied()
                .ok_or_else(|| Error::new("representative is malformed, illegal, or noncanonical")),
        }
    }

    pub fn write_state_stream<W: Write>(
        &self,
        candidate: Candidate,
        mut output: W,
    ) -> Result<StreamSummary, Error> {
        let mut digesting = DigestWriter::new(&mut output);
        digesting.write_all(STREAM_MAGIC)?;
        digesting.write_all(&[FORMAT_VERSION, candidate.tag()])?;
        digesting.write_all(&(self.class_count() as u32).to_be_bytes())?;
        for rank in 0..self.class_count() {
            digesting.write_all(&self.envelope(candidate, rank))?;
        }
        let bytes = digesting.bytes;
        let sha256 = digesting.sha.finalize_hex();
        Ok(StreamSummary {
            candidate,
            records: self.class_count(),
            bytes,
            sha256,
        })
    }

    pub fn read_state_stream<R: Read>(
        &self,
        expected: Candidate,
        mut input: R,
    ) -> Result<(Vec<usize>, StreamSummary), Error> {
        let mut bytes = Vec::new();
        input.read_to_end(&mut bytes)?;
        let sha256 = Sha256::digest_hex(&bytes);
        if bytes.len() < 10 {
            return Err(Error::new("truncated state-stream header"));
        }
        if &bytes[..4] != STREAM_MAGIC {
            return Err(Error::new("wrong state-stream magic"));
        }
        if bytes[4] != FORMAT_VERSION {
            return Err(Error::new(format!(
                "wrong state-stream version {}",
                bytes[4]
            )));
        }
        if bytes[5] != expected.tag() {
            return Err(Error::new(format!(
                "state-stream candidate tag {} does not match {}",
                bytes[5],
                expected.name()
            )));
        }
        let count = u32::from_be_bytes(bytes[6..10].try_into().unwrap()) as usize;
        if count != self.class_count() {
            return Err(Error::new(format!(
                "state-stream record count {count}, expected {}",
                self.class_count()
            )));
        }
        let mut cursor = 10;
        let mut ranks = Vec::with_capacity(count);
        for record in 0..count {
            if bytes.len().saturating_sub(cursor) < 42 {
                return Err(Error::new(format!(
                    "truncated envelope header at record {record}"
                )));
            }
            let length =
                u32::from_be_bytes(bytes[cursor + 38..cursor + 42].try_into().unwrap()) as usize;
            let end = cursor
                .checked_add(42)
                .and_then(|value| value.checked_add(length))
                .ok_or_else(|| Error::new("envelope length overflow"))?;
            if end > bytes.len() {
                return Err(Error::new(format!("truncated envelope at record {record}")));
            }
            ranks.push(self.recover_envelope(expected, &bytes[cursor..end])?);
            cursor = end;
        }
        if cursor != bytes.len() {
            return Err(Error::new(format!(
                "trailing bytes after state stream: {}",
                bytes.len() - cursor
            )));
        }
        Ok((
            ranks,
            StreamSummary {
                candidate: expected,
                records: count,
                bytes: bytes.len(),
                sha256,
            },
        ))
    }

    /// Write the canonical one-step transcript for the recovered stream order.
    ///
    /// Each record contains the current state envelope, operation spelling,
    /// optional proof-domain marker, ordered client and action output lists, and
    /// next state envelope. Variable byte strings use a big-endian u32 length;
    /// output lists begin with a big-endian u32 item count.
    pub fn write_transition_transcript<W: Write>(
        &self,
        candidate: Candidate,
        ranks: &[usize],
        mut output: W,
    ) -> Result<TransitionSummary, Error> {
        let envelopes: Vec<Vec<u8>> = (0..self.class_count())
            .map(|rank| self.envelope(candidate, rank))
            .collect();
        let mut digesting = DigestWriter::new(&mut output);
        digesting.write_all(b"ZGTR")?;
        digesting.write_all(&[FORMAT_VERSION, candidate.tag()])?;
        digesting.write_all(&artifact_digest())?;
        digesting.write_all(&(ranks.len() as u32).to_be_bytes())?;
        digesting.write_all(&(OPERATION_COUNT as u32).to_be_bytes())?;
        digesting.write_all(b"proof-domain-membership-v1\0")?;
        for operation in operations() {
            write_length_prefixed(&mut digesting, operation.spelling().as_bytes())?;
        }
        let mut records = 0usize;
        for &rank in ranks {
            if rank >= self.class_count() {
                return Err(Error::new(format!("invalid recovered rank {rank}")));
            }
            for operation in operations() {
                let step = self.state(rank).apply(operation);
                let next_rank = self.successor_rank(&step.next);
                digesting.write_all(b"S")?;
                write_length_prefixed(&mut digesting, &envelopes[rank])?;
                digesting.write_all(b"O")?;
                write_length_prefixed(&mut digesting, operation.spelling().as_bytes())?;
                digesting.write_all(b"M")?;
                let membership: &[u8] = match step.membership {
                    None => b"N",
                    Some(true) => b"enabled",
                    Some(false) => b"disabled",
                };
                write_length_prefixed(&mut digesting, membership)?;
                write_tagged_frame_list(&mut digesting, b'C', &step.client)?;
                write_tagged_frame_list(&mut digesting, b'A', &step.action)?;
                digesting.write_all(b"N")?;
                write_length_prefixed(&mut digesting, &envelopes[next_rank])?;
                records += 1;
            }
        }
        Ok(TransitionSummary {
            candidate,
            records,
            bytes: digesting.bytes,
            sha256: digesting.sha.finalize_hex(),
        })
    }
}

fn write_length_prefixed<W: Write>(output: &mut W, bytes: &[u8]) -> io::Result<()> {
    output.write_all(&(bytes.len() as u32).to_be_bytes())?;
    output.write_all(bytes)
}

fn write_tagged_frame_list<W: Write>(output: &mut W, tag: u8, frames: &[String]) -> io::Result<()> {
    output.write_all(&[tag])?;
    output.write_all(&(frames.len() as u32).to_be_bytes())?;
    for frame in frames {
        output.write_all(b"V")?;
        write_length_prefixed(output, frame.as_bytes())?;
    }
    Ok(())
}

fn enumerate_states() -> (Vec<Node>, HashMap<State, usize>) {
    let initial = State::initial();
    let mut nodes = vec![Node {
        state: initial.clone(),
        representative: Vec::new(),
    }];
    let mut state_to_node = HashMap::from([(initial, 0)]);
    let mut queue = VecDeque::from([0]);

    while let Some(node_index) = queue.pop_front() {
        let state = nodes[node_index].state.clone();
        let representative = nodes[node_index].representative.clone();
        let mut edges = Vec::<(String, State)>::new();
        if let Some(output) = &state.owed {
            edges.push((output.frame(), state.resume().next));
        } else {
            for input in INPUTS {
                if state.input_enabled(input) {
                    edges.push((input.frame().to_owned(), state.input(input).next));
                }
            }
        }
        edges.sort_by(|left, right| left.0.as_bytes().cmp(right.0.as_bytes()));
        for (frame, successor) in edges {
            if state_to_node.contains_key(&successor) {
                continue;
            }
            let mut next_representative = representative.clone();
            next_representative.push(frame);
            let next_index = nodes.len();
            nodes.push(Node {
                state: successor.clone(),
                representative: next_representative,
            });
            state_to_node.insert(successor, next_index);
            queue.push_back(next_index);
        }
    }
    (nodes, state_to_node)
}

#[derive(Clone, Debug, Eq, Hash, Ord, PartialEq, PartialOrd)]
struct ImmediateSignature {
    membership: Option<bool>,
    client: Vec<String>,
    action: Vec<String>,
}

fn refine(
    nodes: &[Node],
    state_to_node: &HashMap<State, usize>,
) -> (Vec<usize>, Vec<Vec<usize>>, usize) {
    let immediate: Vec<Vec<ImmediateSignature>> = nodes
        .iter()
        .map(|node| {
            operations()
                .map(|operation| {
                    let step = node.state.apply(operation);
                    ImmediateSignature {
                        membership: step.membership,
                        client: step.client,
                        action: step.action,
                    }
                })
                .collect()
        })
        .collect();
    let mut blocks = intern_signatures(immediate.iter().cloned());
    let mut rounds = 0;
    loop {
        let signatures = nodes.iter().enumerate().map(|(node_index, node)| {
            let successors: Vec<usize> = operations()
                .map(|operation| {
                    let step = node.state.apply(operation);
                    blocks[state_to_node[&step.next]]
                })
                .collect();
            (immediate[node_index].clone(), successors)
        });
        let next = intern_signatures(signatures);
        if same_partition(&blocks, &next) {
            let classes = collect_classes(&next);
            return (next, classes, rounds);
        }
        blocks = next;
        rounds += 1;
    }
}

fn intern_signatures<T: Eq + std::hash::Hash>(values: impl Iterator<Item = T>) -> Vec<usize> {
    let mut ids = HashMap::<T, usize>::new();
    values
        .map(|value| {
            let next = ids.len();
            *ids.entry(value).or_insert(next)
        })
        .collect()
}

fn same_partition(left: &[usize], right: &[usize]) -> bool {
    if left.len() != right.len() {
        return false;
    }
    let mut left_to_right = HashMap::new();
    let mut right_to_left = HashMap::new();
    left.iter().zip(right).all(|(&a, &b)| {
        left_to_right.get(&a).is_none_or(|value| *value == b)
            && right_to_left.get(&b).is_none_or(|value| *value == a)
            && {
                left_to_right.insert(a, b);
                right_to_left.insert(b, a);
                true
            }
    })
}

fn collect_classes(blocks: &[usize]) -> Vec<Vec<usize>> {
    let count = blocks.iter().copied().max().map_or(0, |value| value + 1);
    let mut classes = vec![Vec::new(); count];
    for (node, &block) in blocks.iter().enumerate() {
        classes[block].push(node);
    }
    classes
}

fn compare_representatives(left: &Node, right: &Node) -> Ordering {
    left.representative
        .len()
        .cmp(&right.representative.len())
        .then_with(|| {
            left.representative
                .iter()
                .zip(&right.representative)
                .find_map(|(left, right)| {
                    let comparison = left.as_bytes().cmp(right.as_bytes());
                    (comparison != Ordering::Equal).then_some(comparison)
                })
                .unwrap_or(Ordering::Equal)
        })
}

fn representative_bytes(frames: &[String]) -> Vec<u8> {
    frames.join(";").into_bytes()
}

fn encode_envelope(candidate: Candidate, payload: &[u8]) -> Vec<u8> {
    let mut encoded = Vec::with_capacity(42 + payload.len());
    encoded.extend_from_slice(ENVELOPE_MAGIC);
    encoded.push(FORMAT_VERSION);
    encoded.push(candidate.tag());
    encoded.extend_from_slice(&artifact_digest());
    encoded.extend_from_slice(&(payload.len() as u32).to_be_bytes());
    encoded.extend_from_slice(payload);
    encoded
}

fn decode_envelope(expected: Candidate, bytes: &[u8]) -> Result<&[u8], Error> {
    if bytes.len() < 42 {
        return Err(Error::new("truncated envelope header"));
    }
    if &bytes[..4] != ENVELOPE_MAGIC {
        return Err(Error::new("wrong envelope magic"));
    }
    if bytes[4] != FORMAT_VERSION {
        return Err(Error::new(format!("wrong envelope version {}", bytes[4])));
    }
    if bytes[5] != expected.tag() {
        return Err(Error::new(format!(
            "envelope candidate tag {} does not match {}",
            bytes[5],
            expected.name()
        )));
    }
    if bytes[6..38] != artifact_digest() {
        return Err(Error::new("artifact digest mismatch"));
    }
    let length = u32::from_be_bytes(bytes[38..42].try_into().unwrap()) as usize;
    let expected_length = 42usize
        .checked_add(length)
        .ok_or_else(|| Error::new("envelope length overflow"))?;
    if bytes.len() != expected_length {
        return Err(Error::new(format!(
            "envelope length says {expected_length} bytes, got {}",
            bytes.len()
        )));
    }
    Ok(&bytes[42..])
}

fn artifact_digest() -> [u8; 32] {
    let mut digest = [0u8; 32];
    let encoded = ARTIFACT_DIGEST_HEX.as_bytes();
    for index in 0..digest.len() {
        digest[index] = (hex_nibble(encoded[index * 2]) << 4) | hex_nibble(encoded[index * 2 + 1]);
    }
    digest
}

const fn hex_nibble(byte: u8) -> u8 {
    match byte {
        b'0'..=b'9' => byte - b'0',
        b'a'..=b'f' => byte - b'a' + 10,
        _ => panic!("invalid frozen artifact digest"),
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct StreamSummary {
    pub candidate: Candidate,
    pub records: usize,
    pub bytes: usize,
    pub sha256: String,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct TransitionSummary {
    pub candidate: Candidate,
    pub records: usize,
    pub bytes: usize,
    pub sha256: String,
}

struct DigestWriter<'a, W> {
    inner: &'a mut W,
    sha: Sha256,
    bytes: usize,
}

impl<'a, W> DigestWriter<'a, W> {
    fn new(inner: &'a mut W) -> Self {
        Self {
            inner,
            sha: Sha256::new(),
            bytes: 0,
        }
    }
}

impl<W: Write> Write for DigestWriter<'_, W> {
    fn write(&mut self, buffer: &[u8]) -> io::Result<usize> {
        let written = self.inner.write(buffer)?;
        self.sha.update(&buffer[..written]);
        self.bytes += written;
        Ok(written)
    }

    fn flush(&mut self) -> io::Result<()> {
        self.inner.flush()
    }
}

#[derive(Clone, Debug)]
pub struct Sha256 {
    state: [u32; 8],
    block: [u8; 64],
    block_len: usize,
    byte_len: u64,
}

impl Sha256 {
    pub const fn new() -> Self {
        Self {
            state: [
                0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab,
                0x5be0cd19,
            ],
            block: [0; 64],
            block_len: 0,
            byte_len: 0,
        }
    }

    pub fn update(&mut self, mut bytes: &[u8]) {
        self.byte_len = self
            .byte_len
            .checked_add(bytes.len() as u64)
            .expect("SHA-256 input length overflow");
        if self.block_len != 0 {
            let take = (64 - self.block_len).min(bytes.len());
            self.block[self.block_len..self.block_len + take].copy_from_slice(&bytes[..take]);
            self.block_len += take;
            bytes = &bytes[take..];
            if self.block_len == 64 {
                let block = self.block;
                self.compress(&block);
                self.block_len = 0;
            } else {
                return;
            }
        }
        while bytes.len() >= 64 {
            let block: &[u8; 64] = bytes[..64].try_into().unwrap();
            self.compress(block);
            bytes = &bytes[64..];
        }
        self.block[..bytes.len()].copy_from_slice(bytes);
        self.block_len = bytes.len();
    }

    pub fn finalize(mut self) -> [u8; 32] {
        let bit_len = self
            .byte_len
            .checked_mul(8)
            .expect("SHA-256 bit length overflow");
        self.block[self.block_len] = 0x80;
        self.block_len += 1;
        if self.block_len > 56 {
            self.block[self.block_len..].fill(0);
            let block = self.block;
            self.compress(&block);
            self.block = [0; 64];
        } else {
            self.block[self.block_len..56].fill(0);
        }
        self.block[56..64].copy_from_slice(&bit_len.to_be_bytes());
        let block = self.block;
        self.compress(&block);
        let mut digest = [0u8; 32];
        for (index, value) in self.state.into_iter().enumerate() {
            digest[index * 4..index * 4 + 4].copy_from_slice(&value.to_be_bytes());
        }
        digest
    }

    pub fn finalize_hex(self) -> String {
        encode_hex(&self.finalize())
    }

    pub fn digest_hex(bytes: &[u8]) -> String {
        let mut hash = Self::new();
        hash.update(bytes);
        hash.finalize_hex()
    }

    fn compress(&mut self, block: &[u8; 64]) {
        const K: [u32; 64] = [
            0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4,
            0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe,
            0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f,
            0x4a7484aa, 0x5cb0a9dc, 0x76f988da, 0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
            0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc,
            0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b,
            0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070, 0x19a4c116,
            0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
            0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7,
            0xc67178f2,
        ];
        let mut words = [0u32; 64];
        for index in 0..16 {
            words[index] = u32::from_be_bytes(block[index * 4..index * 4 + 4].try_into().unwrap());
        }
        for index in 16..64 {
            let s0 = words[index - 15].rotate_right(7)
                ^ words[index - 15].rotate_right(18)
                ^ (words[index - 15] >> 3);
            let s1 = words[index - 2].rotate_right(17)
                ^ words[index - 2].rotate_right(19)
                ^ (words[index - 2] >> 10);
            words[index] = words[index - 16]
                .wrapping_add(s0)
                .wrapping_add(words[index - 7])
                .wrapping_add(s1);
        }
        let mut a = self.state[0];
        let mut b = self.state[1];
        let mut c = self.state[2];
        let mut d = self.state[3];
        let mut e = self.state[4];
        let mut f = self.state[5];
        let mut g = self.state[6];
        let mut h = self.state[7];
        for index in 0..64 {
            let big_sigma1 = e.rotate_right(6) ^ e.rotate_right(11) ^ e.rotate_right(25);
            let choice = (e & f) ^ ((!e) & g);
            let temporary1 = h
                .wrapping_add(big_sigma1)
                .wrapping_add(choice)
                .wrapping_add(K[index])
                .wrapping_add(words[index]);
            let big_sigma0 = a.rotate_right(2) ^ a.rotate_right(13) ^ a.rotate_right(22);
            let majority = (a & b) ^ (a & c) ^ (b & c);
            let temporary2 = big_sigma0.wrapping_add(majority);
            h = g;
            g = f;
            f = e;
            e = d.wrapping_add(temporary1);
            d = c;
            c = b;
            b = a;
            a = temporary1.wrapping_add(temporary2);
        }
        self.state[0] = self.state[0].wrapping_add(a);
        self.state[1] = self.state[1].wrapping_add(b);
        self.state[2] = self.state[2].wrapping_add(c);
        self.state[3] = self.state[3].wrapping_add(d);
        self.state[4] = self.state[4].wrapping_add(e);
        self.state[5] = self.state[5].wrapping_add(f);
        self.state[6] = self.state[6].wrapping_add(g);
        self.state[7] = self.state[7].wrapping_add(h);
    }
}

impl Default for Sha256 {
    fn default() -> Self {
        Self::new()
    }
}

fn encode_hex(bytes: &[u8]) -> String {
    const HEX: &[u8; 16] = b"0123456789abcdef";
    let mut encoded = String::with_capacity(bytes.len() * 2);
    for &byte in bytes {
        encoded.push(HEX[(byte >> 4) as usize] as char);
        encoded.push(HEX[(byte & 0xf) as usize] as char);
    }
    encoded
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::OnceLock;

    fn frozen_machine() -> &'static Machine {
        static MACHINE: OnceLock<Machine> = OnceLock::new();
        MACHINE.get_or_init(|| Machine::build().unwrap())
    }

    #[test]
    fn sha256_known_vectors() {
        assert_eq!(
            Sha256::digest_hex(b""),
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        );
        assert_eq!(
            Sha256::digest_hex(b"abc"),
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
        );
        let mut incremental = Sha256::new();
        incremental.update(b"a");
        incremental.update(b"b");
        incremental.update(b"c");
        assert_eq!(
            incremental.finalize_hex(),
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
        );
    }

    #[test]
    fn frozen_machine_counts_and_representative_sizes() {
        let machine = frozen_machine();
        assert_eq!(machine.quiescent_count(), EXPECTED_QUIESCENT_COUNT);
        assert_eq!(machine.class_count(), EXPECTED_STATE_COUNT);
        assert_eq!(machine.state_count(), 83_352);
        assert_eq!(machine.representative_payload_stats(), (0, 236, 14_584_671));
    }

    #[test]
    fn refinement_is_a_stable_right_congruence() {
        let machine = frozen_machine();
        let mut reference: Vec<Option<Vec<(ImmediateSignature, usize)>>> =
            vec![None; machine.class_count()];
        for (node_index, node) in machine.nodes.iter().enumerate() {
            let signature: Vec<(ImmediateSignature, usize)> = operations()
                .map(|operation| {
                    let step = node.state.apply(operation);
                    (
                        ImmediateSignature {
                            membership: step.membership,
                            client: step.client,
                            action: step.action,
                        },
                        machine.successor_rank(&step.next),
                    )
                })
                .collect();
            let class = machine.class_of_node[node_index];
            match &reference[class] {
                Some(expected) => assert_eq!(expected, &signature),
                None => reference[class] = Some(signature),
            }
        }
        assert!(reference.into_iter().all(|entry| entry.is_some()));
    }

    #[test]
    fn emitted_state_streams_match_b3() {
        let machine = frozen_machine();
        let mut ordinal = Vec::new();
        let ordinal_summary = machine
            .write_state_stream(Candidate::Ordinal, &mut ordinal)
            .unwrap();
        assert_eq!(ordinal_summary.records, EXPECTED_STATE_COUNT);
        assert_eq!(ordinal_summary.bytes, EXPECTED_ORDINAL_STREAM_BYTES);
        assert_eq!(ordinal_summary.sha256, EXPECTED_ORDINAL_STREAM_SHA256);

        let mut representative = Vec::new();
        let representative_summary = machine
            .write_state_stream(Candidate::Representative, &mut representative)
            .unwrap();
        assert_eq!(representative_summary.records, EXPECTED_STATE_COUNT);
        assert_eq!(
            representative_summary.bytes,
            EXPECTED_REPRESENTATIVE_STREAM_BYTES
        );
        assert_eq!(
            representative_summary.sha256,
            EXPECTED_REPRESENTATIVE_STREAM_SHA256
        );
    }

    #[test]
    fn envelope_decoder_rejects_wrong_or_noncanonical_bytes() {
        let machine = frozen_machine();
        let ordinal = machine.envelope(Candidate::Ordinal, 0);
        for length in 0..ordinal.len() {
            assert!(machine
                .recover_envelope(Candidate::Ordinal, &ordinal[..length])
                .is_err());
        }

        let mut wrong_magic = ordinal.clone();
        wrong_magic[0] ^= 1;
        assert!(machine
            .recover_envelope(Candidate::Ordinal, &wrong_magic)
            .is_err());
        let mut wrong_version = ordinal.clone();
        wrong_version[4] = 2;
        assert!(machine
            .recover_envelope(Candidate::Ordinal, &wrong_version)
            .is_err());
        assert!(machine
            .recover_envelope(Candidate::Representative, &ordinal)
            .is_err());
        let mut wrong_digest = ordinal.clone();
        wrong_digest[6] ^= 1;
        assert!(machine
            .recover_envelope(Candidate::Ordinal, &wrong_digest)
            .is_err());
        let mut wrong_length = ordinal.clone();
        wrong_length[41] = 2;
        assert!(machine
            .recover_envelope(Candidate::Ordinal, &wrong_length)
            .is_err());
        let mut trailing = ordinal.clone();
        trailing.push(0);
        assert!(machine
            .recover_envelope(Candidate::Ordinal, &trailing)
            .is_err());
        assert!(machine
            .recover_envelope(
                Candidate::Ordinal,
                &encode_envelope(Candidate::Ordinal, &[0, 0])
            )
            .is_err());
        let invalid_rank = EXPECTED_STATE_COUNT;
        let invalid_rank_payload = [
            ((invalid_rank >> 16) & 0xff) as u8,
            ((invalid_rank >> 8) & 0xff) as u8,
            (invalid_rank & 0xff) as u8,
        ];
        assert!(machine
            .recover_envelope(
                Candidate::Ordinal,
                &encode_envelope(Candidate::Ordinal, &invalid_rank_payload),
            )
            .is_err());

        assert!(machine
            .recover_envelope(
                Candidate::Representative,
                &encode_envelope(Candidate::Representative, &[0xff]),
            )
            .is_err());
        let legal_but_noncanonical = b"in:client:O;out:client:EMPTY";
        assert!(machine
            .recover_envelope(
                Candidate::Representative,
                &encode_envelope(Candidate::Representative, legal_but_noncanonical),
            )
            .is_err());
    }

    #[test]
    fn stream_decoder_requires_exact_header_count_and_eof() {
        let machine = frozen_machine();
        let mut stream = Vec::new();
        machine
            .write_state_stream(Candidate::Ordinal, &mut stream)
            .unwrap();

        let mut wrong_magic = stream.clone();
        wrong_magic[0] ^= 1;
        assert!(machine
            .read_state_stream(Candidate::Ordinal, wrong_magic.as_slice())
            .is_err());
        assert!(machine
            .read_state_stream(Candidate::Representative, stream.as_slice())
            .is_err());
        let mut wrong_count = stream.clone();
        wrong_count[9] ^= 1;
        assert!(machine
            .read_state_stream(Candidate::Ordinal, wrong_count.as_slice())
            .is_err());
        let mut trailing = stream;
        trailing.push(0);
        assert!(machine
            .read_state_stream(Candidate::Ordinal, trailing.as_slice())
            .is_err());
    }

    #[test]
    #[ignore = "exhaustive 1,403,928-record digest check; run explicitly in release mode"]
    fn exhaustive_transition_digests_match_b3() {
        let machine = frozen_machine();
        let ranks: Vec<usize> = (0..machine.class_count()).collect();
        let ordinal = machine
            .write_transition_transcript(Candidate::Ordinal, &ranks, io::sink())
            .unwrap();
        assert_eq!(ordinal.records, EXPECTED_STATE_COUNT * OPERATION_COUNT);
        assert_eq!(ordinal.sha256, EXPECTED_ORDINAL_TRANSITION_SHA256);
        let representative = machine
            .write_transition_transcript(Candidate::Representative, &ranks, io::sink())
            .unwrap();
        assert_eq!(
            representative.records,
            EXPECTED_STATE_COUNT * OPERATION_COUNT
        );
        assert_eq!(
            representative.sha256,
            EXPECTED_REPRESENTATIVE_TRANSITION_SHA256
        );
    }
}
