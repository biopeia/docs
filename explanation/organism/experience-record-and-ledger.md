# The experience record and its ledger

Reviewed against `organism` at commit `637bc21a7e2a1aa9e0870f55f134e839657687f4`
(main on 2026-10-16); first written against `ba001179`. Everything below describes that revision.
Statements are marked by what supports them: the code, the tests, an ad hoc run, or an accepted decision.

## What it is

The Organism package has a directory called `memory`. It holds an immutable
value describing one episode (`ExperienceRecord`), a bounded FIFO container
(`ExperienceLedger`), and a recording pipeline (`organism:src/organism/memory/recording.py`)
that creates records deterministically from sensory inputs, cognitive activations, and
action outcomes during organism transitions.

The records capture abstract native tokens and verified evidence references without
host entropy or ungrounded evaluator labels. Records can be constructed, shape-checked,
serialized to JSON, restored, and accumulated into the ledger with strict capacity bounds.

This ledger is not the [executive outcome ledger](executive-outcome-ledger.md).
That one lives in the agency code, is keyed by competence and effect, and
turns counts into a factor. The two share a word and nothing else; neither
refers to the other.

## One record

A record (`organism:src/organism/memory/experience.py::ExperienceRecord`) is
immutable and has ten fields:

- an identifier for the record and the identifier of the Organism it belongs
  to;
- a number called the tick class;
- up to 512 context tokens, an optional action token, and up to 128 outcome
  tokens;
- a status, one of seven words;
- up to 16 evidence references;
- a confidence class from 0 to 7;
- a source kind, one of five words.

Every token and reference is a string of at most 96 printable characters
without spaces. The record's docstring gives the reason for the abstraction:
it "deliberately stores abstract native tokens and evidence references,
never evaluator labels or arbitrary raw host payloads". That is a statement
about what a producer should put in. The record checks the shape of a token,
not where it came from.

### What the record refuses

Read from the code, and seen in an ad hoc run except where a test is named:

- a record with no context, no action and no outcome;
- a status of `observed`, `supported` or `contradicted` with no evidence
  reference;
- a source kind of `model` with a status of `observed`
  (`test_model_generated_record_cannot_claim_direct_observation`);
- a confidence class outside 0 to 7, a negative tick class, or a token of the
  wrong shape.

The third rule is the only one that relates the two classifications. The
docstring explains what it is for: the source kind marks "model-originated
proposals so the corpus builder can enforce the anti-self-confirmation
invariant". No corpus builder exists in the repository. The rule that does
exist is narrow: in the same run a record with source kind `model` and status
`supported`, carrying one evidence reference, was accepted.

### What the words do not establish

The seven statuses are observed, associated, hypothesized, predicted,
supported, contradicted and retired. The five source kinds are direct,
internal, action outcome, cognitive and model. They are labels a producer
attaches. Apart from the three rules above, no code reads them: nothing
moves a record from hypothesized to supported, nothing compares a prediction
with an outcome, and an evidence reference is a string that nothing
resolves. The confidence class is an integer that nothing computes or reads.

The tick class is a non-negative integer with no upper bound. The record does
not say which clock it belongs to or how a tick becomes a class, and the
ledger does not require it to increase.

### Identity and content

A record has a content hash: SHA-256 over its canonical form without the
record identifier. Two records that differ only in identifier have the same
hash, and a change to an outcome token changes it
(`test_content_hash_excludes_record_identity_but_includes_experience`).

A record written to plain data reads back equal
(`test_record_round_trips_its_canonical_payload`). The reader now requires
exactly the ten fields the writer emits. A payload with an unknown key, and
one without a list of tokens, were both refused in an ad hoc run; at the
earlier revision the first was ignored and the second read as empty. The
ledger's test for incomplete state covers the missing list
(`test_restore_rejects_missing_or_null_required_checkpoint_state`).

## The ledger

A ledger (`organism:src/organism/memory/ledger.py::ExperienceLedger`) is
created for one Organism identifier with a capacity between 16 and 8192,
2048 by default. It refuses a record of another Organism and a record whose
identifier it already holds
(`test_ledger_rejects_foreign_and_duplicate_record_identity`).

When full, appending drops the oldest record and returns it to the caller
(`test_ledger_is_bounded_and_reports_evicted_oldest_record`). Age here is
order of arrival, not the tick class. Nothing is done with the dropped record
unless the caller does it; the migration record notes that the archive class
which accompanied this ledger in its source was not copied.

The ledger's docstring says records are "append-only by identity" and that a
correction "is represented by a new record with its own epistemic state and
provenance". Two limits on that, both seen in an ad hoc run:

- once a record has been dropped, its identifier is free again: a record with
  the identifier of a dropped one was accepted;
- a new record is not linked to the one it corrects. No field names another
  record.

Looking a record up walks the list.

### Across a restart

The ledger writes its Organism identifier, its capacity and its records, in
order, with a schema version. Reading it back requires the caller to state
the Organism identifier and refuses a mismatch, a repeated record identifier
and more records than the capacity
(`test_ledger_round_trip_preserves_order_and_organism_identity`,
`test_restore_rejects_foreign_identity_duplicate_records_and_overflow`). The
capacity is restored (ad hoc run). Reading from nothing is now refused, as is
a payload missing any of its four fields
(`test_restore_rejects_missing_or_null_required_checkpoint_state`); at the
earlier revision it gave an empty ledger of default capacity. An empty ledger
is obtained by constructing one.

No checkpoint includes the ledger. The composed cognitive payload described
under [what a cognitive checkpoint carries](cognitive-checkpoint.md)
accepts a tuple of records handed to it by its caller and writes them; it
does not refer to a ledger, and a search found no code that takes records out
of a ledger to pass them. The one function in source that carries such a
payload from one step to the next writes back the records it read and adds
none (see [the accepted step](sense-to-checkpoint-transition.md#the-accepted-step)). The repository's migration record says of the
ledger that it "is not wired into the top-level Organism runtime or a
complete checkpoint".

## At each lifecycle boundary

| Boundary | What happens | Support |
|---|---|---|
| Birth | A new ledger is empty | Code |
| Checkpoint | The ledger can be exported whole; no checkpoint includes it. Records can be written into the cognitive payload if a caller supplies them | Code and tests; search of the repository |
| Restart | An exported ledger can be rebuilt for the same Organism identifier | Code and tests |
| Re-embodiment | Nothing here reacts. A record names an Organism and no body | Code; no operation performs a re-embodiment |
| Reproduction | No operation exists, and the genetics code does not refer to records | Search of the repository |

## Whose state this is

[ADR-0092](../../technical/adr/ADR-0092-organism-owns-the-meaning-of-its-private-longitudinal-state.md)
names memory among the private longitudinal state whose meaning the Organism
owns, and
[ADR-0081](../../technical/adr/ADR-0081-the-canonical-organism-is-longitudinal.md)
and [ADR-0103](../../technical/adr/ADR-0103-portable-organism-state.md) ask
that it continue with the Organism and travel in a portable checkpoint. The
directory lives in the Organism package, binds every record to one Organism
identifier and imports nothing from another domain.

No host time is read and nothing is random: identifiers and tick classes are
supplied by the caller, in line with what
[ADR-0090](../../technical/adr/ADR-0090-host-wall-clock-time-is-never-implicit-causal-authority.md)
asks, and for the plain reason that nothing here originates a value.

## Deterministic recording from transitions

`organism:src/organism/memory/recording.py` introduces explicit recording constructors
and bounded accumulation policies:

- **`ExperienceRecordingPolicy`:** Bounded configuration (`record_reception: bool`,
  `record_interpretation: bool`, `max_records: int` in [16, 8192], `activation_threshold: float`,
  `evidence_prefix: str`).
- **Direct sensory receipt (`record_sense_reception`):** Captures external input through the
  authorized causal boundary. Sets `source_kind: SourceKind.DIRECT`, `epistemic_status: EpistemicStatus.OBSERVED`,
  `confidence_class: 7`, and `evidence_refs: (f"{evidence_prefix}:{world_id}:{causal_tick}",)`.
  Refuses signals whose provenance disagrees with the reception provenance.
- **Cognitive interpretation (`record_cognitive_interpretation`):** Captures internal node
  activations above the configured threshold. Sets `source_kind: SourceKind.COGNITIVE`,
  `epistemic_status: EpistemicStatus.ASSOCIATED`, `confidence_class: 4`, and empty `evidence_refs`.
- **Action outcome knowledge (`record_action_outcome`):** Captures verified consequences following
  an executed motor intent. Sets `source_kind: SourceKind.ACTION_OUTCOME`, `epistemic_status: EpistemicStatus.SUPPORTED`
  (or `CONTRADICTED` if failed), `confidence_class: 6`, and binds verified outcome receipt references.
- **Bounded accumulation (`accumulate_experience_records`):** Deterministically ingests new
  records into the owner's `ExperienceLedger`, enforcing FIFO bounds without duplicate record IDs.
- **Runtime wiring:** In `organism:src/organism/cognition/owner_transition.py::advance_organism_from_sense_signals`,
  supplying an `experience_policy` automatically records sensory reception and cognitive activations,
  accumulating them into `runtime.experience_records` across accepted steps.

## What supports this description

| Claim | Support |
|---|---|
| Round trip of a record, content hash without the identifier, refusal of a model record marked observed | Code and tests in `organism:tests/memory/test_experience.py` |
| The bound and what is returned on overflow, refusal of foreign and repeated records, round trip of the ledger, refusals on reading back | Code and tests in `organism:tests/memory/test_ledger.py` |
| Deterministic sensory reception recording with provenance validation and evidence ref binding | Code in `organism:src/organism/memory/recording.py` and tests in `organism:tests/memory/test_recording.py::test_record_sense_reception_creates_valid_direct_record` |
| Cognitive activation interpretation recording with threshold filtering | Code in `organism:src/organism/memory/recording.py` and tests in `organism:tests/memory/test_recording.py::test_record_cognitive_interpretation_filters_by_threshold` |
| Action outcome empirical validation recording | Code in `organism:src/organism/memory/recording.py` and tests in `organism:tests/memory/test_recording.py::test_record_action_outcome_creates_valid_action_record` |
| Deterministic FIFO record accumulation | Code in `organism:src/organism/memory/recording.py` and tests in `organism:tests/memory/test_recording.py::test_accumulate_experience_records_enforces_fifo_bounds` |
| Transition step integration via `advance_organism_from_sense_signals` | Code in `organism:src/organism/cognition/owner_transition.py` |
| That this state is the Organism's and longitudinal | Accepted decisions ADR-0092, ADR-0081 and ADR-0103; statements of intent |

## Open questions

- What an external consumer does with accumulated experience records in longitudinal training.
- What happens to a dropped record when the FIFO ledger overflows.
