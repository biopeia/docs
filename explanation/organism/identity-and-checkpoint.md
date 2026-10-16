# Organism identity and the checkpoint envelope

Reviewed against `organism` at commit `637bc21a7e2a1aa9e0870f55f134e839657687f4`
(main on 2026-10-16); first written against `ba001179`. Everything below describes that revision.
Statements are marked by what supports them: the code, the tests, an ad hoc run, or an accepted decision.
Searches were repeated on 2026-10-16. In addition to the base envelope contract,
`checkpoint.py` defines `OrganismLongitudinalCheckpoint`, an aggregate that encodes and
verifies the complete continuation-closure taxonomy across all 10 longitudinal subsystems.

## What it is

Two questions have to be answerable before an Organism can outlive a process:
which Organism is this, and what must be kept for it to continue. The package
answers each with one small value.

The first is an identity: a wrapped UUID and nothing more. The second is a
checkpoint envelope: the identity, a block of bytes that only the Organism
understands, and a list of other things those bytes need in order to be
restored. The envelope is deliberately ignorant. It does not know what the
bytes mean, how they were assembled, or how to turn them back into a running
Organism.

Two further values now wrap the envelope, and they answer questions the
envelope cannot: how many steps the Organism has taken, whether it is active,
dormant or terminated, which body context it is in, and which saved state of
an identity is the current one. They are described in
[the transition boundary and the continuation registry](transition-and-continuation.md).
This document stays with the identity and the envelope, and says where the
new layer changes what could be said about them.

That ignorance is the design intent recorded in
[ADR-0092](../../technical/adr/ADR-0092-organism-owns-the-meaning-of-its-private-longitudinal-state.md):
the Organism owns the meaning of its private state, and the decision says to
"Prefer an opaque Organism-defined checkpoint/restore contract coordinated by
World." The module describes itself in narrower terms than a persistence
format: "This module defines an in-memory contract, not a durable wire/storage
format."

## Identity

An identity (`organism:src/organism/identity.py::OrganismIdentity`) is an
immutable value holding one UUID. Two identities are the same when their UUIDs
are equal. It carries no name, no generation, no parent, no time of creation
and no body.

There are two ways to obtain one, and neither generates anything.

- `create` wraps a value the caller already has. The code states why: "this
  package does not draw from host entropy for state that can participate in
  causal life". Where identities come from is left to the caller
  (`test_identity_wraps_explicit_value_without_generating_host_entropy`).
- `parse` reads the textual form of a UUID. Its docstring calls this
  "Reconstitute an existing identity for an explicitly authorized
  continuation." The function takes a string and returns an identity; it
  receives no authorization and checks none.

So what makes an Organism the same Organism, as far as this code can tell, is
equality of a UUID that someone outside the package supplied. That is the
whole mechanism.

What is not checked, confirmed by running the module:

- **That the wrapped value is a UUID.** `create` does not validate its
  argument: an identity wrapping the string `not-a-uuid` was constructed.
  `parse` does validate, and accepts the alternative spellings of a UUID that
  the standard library accepts, returning the same identity for each.
- **That an identity is in use once.** See
  [continuations and branches](#continuations-and-branches).

## The envelope

A checkpoint (`organism:src/organism/checkpoint.py::OrganismCheckpoint`) is an
immutable value with three parts: an identity, the private state as bytes, and
zero or more dependencies. A dependency
(`organism:src/organism/checkpoint.py::CheckpointDependency`) is a locator,
which is any non-empty string, and a lowercase SHA-256 digest
(`test_dependency_requires_valid_digest`).

Encoded, the envelope is one JSON object in a deterministic form: keys sorted,
no insignificant whitespace. It has exactly six fields: a schema name, a
schema version (1), the identity as text, the private state in base64, the
SHA-256 of the private state, and the list of dependencies. Encoding the same
checkpoint twice gave identical bytes.

Decoding is strict in shape and returns an equal checkpoint
(`test_portable_envelope_round_trips_opaque_longitudinal_state`). It refuses:

- any set of top-level fields other than exactly those six, and any other
  schema name or version, including a version given as a boolean
  (`test_portable_envelope_rejects_unknown_version_and_extra_fields`,
  `test_portable_envelope_rejects_boolean_schema_version`);
- private state whose digest does not match the recorded one
  (`test_portable_envelope_rejects_private_state_corruption`);
- a dependency entry with any fields other than a locator and a digest;
- bytes that are not such a document at all.

What the envelope does *not* carry is as informative as what it does. There is
no tick, no World, no body or embodiment, no time, no sequence number and no
reference to a previous checkpoint. Two envelopes for the same identity cannot
be ordered, and nothing in an envelope says which of them is later. That
remains true of the envelope. An order now exists one layer out: a
[transition state](transition-and-continuation.md#the-transition-state)
carries an envelope together with a step counter, a lifecycle and optional
references to a body context and a World tick.

## The dependency closure

Private state may be too large, or too shared, to embed: the weights of a
private model are the example the tests use. The envelope then names the
content by locator and digest instead. A checkpoint is complete only if
everything it names can be fetched and is what the digest says.

Checking this is one method. The caller supplies a function from locator to
bytes; for each dependency the method fetches, hashes and compares. A locator
that cannot be read raises one error
(`test_missing_dependency_means_checkpoint_is_not_complete`), content with a
different hash raises another (`test_changed_dependency_is_rejected`), and
silence means every declared dependency was present and intact
(`test_checkpoint_verifies_dependency_closure`).

The envelope does not perform this check when it is decoded. Decoding
validates the document; the closure is verified only when someone calls the
method with a reader (`test_checkpoint_verifies_dependency_closure`).
The composed cognitive payload does not call it: restoring that payload
from an envelope refuses any declared dependency outright
(`test_owner_payload_rejects_caller_declared_dependencies`). (Corrected
on 2026-10-16: the tests first cited here had been replaced by organism
`c34147a` before this document's revision; finding F-0168.)
The transition state offers the same check under the same name and passes it
straight to the envelope (`test_dependency_verification_remains_owner_declared`).

> Note added on 2026-10-17 against `organism` `779c097d21236cba0409f5fc52fbcd71bf2049d9`: the envelope's
> encoding is canonical, but decoding accepts other byte forms of the same
> state, such as indentation, key order, escapes or a trailing newline. Each
> has a different SHA-256 (finding F-0175;
> `docs:research/organism-codec-canonicality-v1.md`). The rest of this
> document keeps the review revision stated at its top.

This is the behaviour
[ADR-0103](../../technical/adr/ADR-0103-portable-organism-state.md) asks of a
portable checkpoint, which must carry its dependency closure "as embedded data
or verified content-addressed durable references", and it adds: "A checkpoint
referencing missing private-model content is not a complete portable
continuation." The code and the decision are set side by side here; whether
the first conforms to the second is not ruled on, for the reason in the next
section.

## What the closure and the digests do not establish

Read from the code and confirmed by running the module at `organism`
`6543188ff302a5f2dc8002c0086252d6061e5310`; the module is unchanged since.

- **Only declared dependencies are checked.** The method knows the list in the
  envelope, not what the private state actually needs. A checkpoint with no
  dependencies passes with a reader that fails on every locator. The
  repository states this limit itself, in its migration notes: "This validates
  declared references only; it does not demonstrate that current private-model
  artifacts are all represented in the envelope."
- **The digest of the private state detects corruption, not substitution.**
  The digest travels in the same document as the state. Replacing both
  together produced an envelope that decoded without complaint, and so did
  replacing the identity. An envelope is trustworthy only as far as an
  external record of its hash is; World's checkpoint references carry one.
- **Only two reading failures count as "missing".** The method treats
  `FileNotFoundError` and `KeyError` as a missing dependency. A reader that
  raised `PermissionError` let that error escape unchanged.
- **A locator need not be content-addressed.** Any non-empty string is
  accepted, and the same dependency may be listed twice.
- **The constructor does not check types.** A checkpoint whose identity and
  private state were plain strings was constructed; such a value fails only
  later, when encoded.

## What a portable checkpoint carries today

The envelope transports whatever bytes it is given. What those bytes contain
is decided by whoever fills it, and at this revision one composition exists
(`organism:src/organism/cognition/portable_checkpoint.py::CognitiveRuntimeCheckpoint`):
the cognitive graph with its learned weights, the recurrent activation state
with its tick, experience records, and optionally safety state, sensory
normalizers, a generative resident's state and a group of genetic state. It refuses to restore when the
identity inside the payload differs from the identity on the envelope
(`test_cognitive_checkpoint_rejects_identity_mismatch`).

Its own description ends with "This is not a complete Organism checkpoint."
That composition is described in
[what a cognitive checkpoint carries](cognitive-checkpoint.md). Other
Organism state that has its own export and restore functions, for example
the [executive outcome ledger](executive-outcome-ledger.md), is not part of
it. No component at this revision assembles a complete Organism.

One function in source now writes an envelope: the
[accepted step](sense-to-checkpoint-transition.md#the-accepted-step) restores
the cognitive payload from the envelope of a transition state, advances it
and wraps the result in a new envelope under the same identity, declaring the
same dependencies as the old one. Nothing in the source of any repository
calls that function (search of the seven repositories, 2026-10-11).

The envelope is also not what crosses to World in World's physical step
fixture, where the Organism's checkpoint is a JSON document written by the
fixture (see [the physical causal step](../world/physical-step.md) and
finding F-0002; that fixture belongs to the World documentation and was not
re-read for this review). In another World integration test,
`world:tests/integration/test_durable_checkpoint_restore_slice.py`, the
bytes handed to World are an encoded envelope holding a cognitive payload. No
World test hands over a transition state or a continuation (search of
`world` for `OrganismTransitionState` and `OrganismContinuation`,
2026-10-11: no mention).

## Continuations and branches

[ADR-0081](../../technical/adr/ADR-0081-the-canonical-organism-is-longitudinal.md)
defines the Organism as longitudinal: "identity survives body,
embodiment-session, world-presence, runtime-instance and checkpoint changes
when the operation continues that same Organism".
[ADR-0091](../../technical/adr/ADR-0091-one-non-terminated-continuation-per-organism-identity.md)
adds a constraint on that continuity: "A canonical longitudinal Organism has
at most one non-terminated continuation under one authoritative identity."
and "every non-canonical fork/copy/branch receives a new identity".

Beside those decisions, the identity and the envelope by themselves:

- keep the identity through encoding and decoding, which is the one
  continuity operation they implement;
- have no record of which continuations of an identity exist. Two envelopes
  holding different private state under the same identity were both decoded,
  and nothing in either could tell which, if either, is the canonical one;
- have no notion of a branch, of retirement, dormancy, generation or
  parentage.

At the earlier revision that was the whole answer, and this section said
that nothing in the package recorded continuations, made a branch or knew
dormancy. **That is no longer true of the package.** A second module now
provides, and
[its own document](transition-and-continuation.md) describes:

- a registry that records, per identity, the one continuation state it
  regards as current, refuses an earlier state once a later one is committed,
  and grants one lease at a time
  (`test_registry_rejects_duplicate_live_restore_and_stale_checkpoint`);
- a function that makes a branch: a continuation under a new identity with
  recorded ancestry, from private state the caller must supply
  (`test_branch_requires_new_owner_state_and_records_ancestry`);
- three lifecycle states, active, dormant and terminated, with a recorded
  history of changes between them
  (`test_terminated_organism_cannot_transition_again`).

Three limits belong beside that list. The registry describes itself as "an
in-memory compare-and-commit guard" that "must not be treated as global
identity uniqueness". Nothing in the source of any repository constructs a
registry, makes a branch or changes a lifecycle; tests do. And there is
still no generation or parentage anywhere: a branch is not an offspring.
The earlier absence was recorded as finding F-0031; the limits of what now
exists are recorded as finding F-0141.

ADR-0091 itself leaves the mechanism open: it says the owner and storage of
the canonical designation are reserved to a later pass. What exists is
therefore stated, not judged.

## The longitudinal aggregate: OrganismLongitudinalCheckpoint

Beyond the opaque `OrganismCheckpoint` envelope, `checkpoint.py` provides
`OrganismLongitudinalCheckpoint` (`schema: "biopeia.organism-longitudinal-checkpoint"`,
`schema_version: 1`), an aggregate that captures the complete named owner state
through subsystem codecs.

### Required component closure

The aggregate requires exact presence of the ten named longitudinal components
(`REQUIRED_LONGITUDINAL_COMPONENTS`):

1. `lifecycle`
2. `cognitive_transition`
3. `cognitive_graph`
4. `experience_memory`
5. `genetic_expression`
6. `learning_safety`
7. `sensory_normalizers`
8. `agency`
9. `competencies`
10. `action_commitments`

Missing or unregistered extra components are strictly rejected fail-closed
(`test_longitudinal_checkpoint_rejects_missing_or_unknown_components`).

### Capture, serialization and restoration

- **Capture:** `OrganismLongitudinalCheckpoint.capture_components(identity, states, encoders)`
  requires a complete, identity-bound encoder registry matching `REQUIRED_LONGITUDINAL_COMPONENTS`.
  Each encoder receives the component state and the owner `OrganismIdentity`, guaranteeing
  that components cannot be captured across mismatched identities
  (`test_capture_uses_a_complete_identity_bound_encoder_registry`).
- **Wire representation:** Each component is stored as an envelope with base64 payload and
  its exact SHA-256 digest (`payload_base64`, `sha256`). A tampered component digest or
  duplicate JSON key fails closed (`test_longitudinal_checkpoint_rejects_tampered_component_digest`,
  `test_longitudinal_checkpoint_rejects_duplicate_json_keys`).
- **Restoration:** `checkpoint.restore_components(decoders, read_dependency=...)` requires a
  complete decoder registry matching the component closure. It explicitly verifies the
  external dependency closure before invoking decoders; missing dependencies or mismatched
  hashes fail closed (`test_restore_requires_complete_decoders_and_dependency_closure`).
- **Envelope bridge:** The aggregate bridges bidirectionally with the outer envelope
  via `checkpoint.to_organism_checkpoint()` and `OrganismLongitudinalCheckpoint.from_organism_checkpoint()`,
  verifying identity and dependency consistency on restoration
  (`test_longitudinal_checkpoint_round_trips_exact_component_bytes`).

## At each lifecycle boundary

The documentation registry asks, of every Organism component, what happens to
its state at five boundaries. For this component the answers rest on
different kinds of support and should not be read as equally strong.

| Boundary | What happens | Support |
|---|---|---|
| Birth | The identity is supplied by the caller and wrapped | Code and test |
| Checkpoint | Identity, private bytes and dependency list are preserved exactly; `OrganismLongitudinalCheckpoint` verifies component closure and component SHA-256 digests | Code and tests |
| Restart | Decoding returns an equal value; decoders restore exact subsystem state only after external dependency closure verification | Code and tests |
| Re-embodiment | The envelope has no field that names a body, so there is nothing to change. The body reference lives in the transition state around it, and replacing it leaves the envelope byte for byte the same | Absence in the code, and `test_reembodiment_preserves_identity_and_longitudinal_state`; that identity survives is ADR-0081, a statement of intent |
| Reproduction | No operation exists. A branch under a new identity can be recorded one layer out; it is not an offspring | Nothing in the code of these two modules; that offspring and branches receive new identities is ADR-0091, a statement of intent |

## What supports this description

| Claim | Support |
|---|---|
| Identity wraps a supplied value and is recovered from text | Code and `organism:tests/test_identity.py` |
| Envelope shape, deterministic encoding, strict decoding, digest check, closure check | Code and tests in `organism:tests/test_checkpoint.py` |
| Longitudinal aggregate enforces 10-component closure, round-trips exact component bytes, and bridges to envelope | Code and tests in `organism:tests/source_unit/test_longitudinal_checkpoint.py::test_longitudinal_checkpoint_round_trips_exact_component_bytes` |
| Longitudinal aggregate rejects missing or unknown components | Code and `organism:tests/source_unit/test_longitudinal_checkpoint.py::test_longitudinal_checkpoint_rejects_missing_or_unknown_components` |
| Complete identity-bound encoder registry required for component capture | Code and `organism:tests/source_unit/test_longitudinal_checkpoint.py::test_capture_uses_a_complete_identity_bound_encoder_registry` |
| Tampered component digests and duplicate JSON keys rejected | Code and `organism:tests/source_unit/test_longitudinal_checkpoint.py::test_longitudinal_checkpoint_rejects_tampered_component_digest`, `test_longitudinal_checkpoint_rejects_duplicate_json_keys` |
| Subsystem restoration requires complete decoders and verified external dependency closure | Code and `organism:tests/source_unit/test_longitudinal_checkpoint.py::test_restore_requires_complete_decoders_and_dependency_closure` |
| `create` accepts a non-UUID; the constructor accepts strings; state and digest, or the identity, can be replaced together; other read errors escape; duplicate dependencies and an empty closure pass | Code, and one ad hoc run of the module at `organism` `6543188ff302a5f2dc8002c0086252d6061e5310`, the two modules being unchanged since; no test is kept for these |
| Two different states under one identity both decode | The same ad hoc run |
| Restoring a composed payload verifies declared dependencies and the identity | Code and tests in `organism:tests/source_unit/cognition/test_portable_checkpoint.py`; the composed payload has its own document |
| The closure covers declared references only | Code, and the repository's own `organism:MIGRATION.md` |
| The identity and the envelope hold no branch, lifecycle or continuation record; a second module of the package now does, and nothing in source uses it | Code of the two modules; search of the seven repositories on 2026-10-11 for the names of the second module |
| What identity and a portable checkpoint must mean | Accepted decisions ADR-0081, ADR-0091, ADR-0092, ADR-0103; statements of intent, not test results |

No persisted envelope from a real run was examined, because no component at
this revision writes one outside the tests.

## Open questions

- Which component will hold, for a running Organism, the registry of
  continuations that now exists, and where its record will be stored so that
  it is the single authority ADR-0091 asks for.
- Whether the private-state digest is meant as protection against anything
  more than accidental damage.
- Who decides which dependencies a given private state requires, so that
  "declared" and "required" can be compared.
