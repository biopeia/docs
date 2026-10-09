# Organism identity and the checkpoint envelope

Reviewed against `organism` at commit `6543188ff302a5f2dc8002c0086252d6061e5310`.
Everything below describes that revision. Statements are marked by what
supports them: the code, the tests, an ad hoc run, or an accepted decision.

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
be ordered, and nothing in an envelope says which of them is later.

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
method with a reader. One caller in the package does so: restoring the
composed cognitive payload from an envelope that declares dependencies
requires a reader and verifies the closure first
(`test_organism_checkpoint_restore_requires_and_verifies_dependency_closure`).

This is the behaviour
[ADR-0103](../../technical/adr/ADR-0103-portable-organism-state.md) asks of a
portable checkpoint, which must carry its dependency closure "as embedded data
or verified content-addressed durable references", and it adds: "A checkpoint
referencing missing private-model content is not a complete portable
continuation." The code and the decision are set side by side here; whether
the first conforms to the second is not ruled on, for the reason in the next
section.

## What the closure and the digests do not establish

Read from the code and confirmed by running the module at that revision.

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
normalizers and a generative resident's state. It refuses to restore when the
identity inside the payload differs from the identity on the envelope
(`test_cognitive_checkpoint_rejects_identity_mismatch`).

Its own description ends with "This is not a complete Organism checkpoint."
That composition was not reviewed for this document beyond its use of the
envelope. Other Organism state that has its own export and restore functions,
for example the [executive outcome ledger](executive-outcome-ledger.md), is
not part of it. No component at this revision assembles a complete Organism.

The envelope is also not what crosses to World in the only cross-domain
composition that exists. In World's physical step fixture the Organism's
checkpoint is a JSON document written by the fixture
(see [the physical causal step](../world/physical-step.md) and finding
F-0002).

## Continuations and branches

[ADR-0081](../../technical/adr/ADR-0081-the-canonical-organism-is-longitudinal.md)
defines the Organism as longitudinal: "identity survives body,
embodiment-session, world-presence, runtime-instance and checkpoint changes
when the operation continues that same Organism".
[ADR-0091](../../technical/adr/ADR-0091-one-non-terminated-continuation-per-organism-identity.md)
adds a constraint on that continuity: "A canonical longitudinal Organism has
at most one non-terminated continuation under one authoritative identity."
and "every non-canonical fork/copy/branch receives a new identity".

Beside those decisions, the code at this revision:

- keeps the identity through encoding and decoding, which is the one
  continuity operation it implements;
- has no record of which continuations of an identity exist. Two envelopes
  holding different private state under the same identity were both decoded,
  and nothing could tell which, if either, is the canonical one;
- has no operation that makes a branch. The repository's README lists, among
  the contents of the slice, "immutable Organism identity values, including
  explicit fresh identities for branches". An identity value can of course be
  created with a new UUID, but nothing in the package takes a checkpoint and
  produces a branch with a new identity and recorded ancestry;
- has no notion of retirement, dormancy, generation or parentage.

ADR-0091 itself leaves the mechanism open: it says the owner and storage of
the canonical designation are reserved to a later pass. The absence is
therefore stated, not judged.

## At each lifecycle boundary

The documentation registry asks, of every Organism component, what happens to
its state at five boundaries. For this component the answers rest on
different kinds of support and should not be read as equally strong.

| Boundary | What happens | Support |
|---|---|---|
| Birth | The identity is supplied by the caller and wrapped | Code and test |
| Checkpoint | Identity, private bytes and dependency list are preserved exactly | Code and tests |
| Restart | Decoding returns an equal value; nothing here restarts anything | Code and tests |
| Re-embodiment | The envelope has no field that names a body, so there is nothing to change | Absence in the code; that identity survives is ADR-0081, a statement of intent |
| Reproduction | No operation exists | Nothing in the code; that offspring and branches receive new identities is ADR-0091, a statement of intent |

## What supports this description

| Claim | Support |
|---|---|
| Identity wraps a supplied value and is recovered from text | Code and `organism:tests/test_identity.py` |
| Envelope shape, deterministic encoding, strict decoding, digest check, closure check | Code and tests in `organism:tests/test_checkpoint.py` |
| `create` accepts a non-UUID; the constructor accepts strings; state and digest, or the identity, can be replaced together; other read errors escape; duplicate dependencies and an empty closure pass | Code, and one ad hoc run of the module at that revision; no test is kept for these |
| Two different states under one identity both decode | The same ad hoc run |
| Restoring a composed payload verifies declared dependencies and the identity | Code and tests in `organism:tests/source_unit/cognition/test_portable_checkpoint.py`; the composed payload itself was not reviewed |
| The closure covers declared references only | Code, and the repository's own `organism:MIGRATION.md` |
| No branch, retirement or continuation record exists | Search of the repository at that revision |
| What identity and a portable checkpoint must mean | Accepted decisions ADR-0081, ADR-0091, ADR-0092, ADR-0103; statements of intent, not test results |

No persisted envelope from a real run was examined, because no component at
this revision writes one outside the tests.

## Open questions

- Which component will hold the record of continuations that ADR-0091
  requires, and whether the envelope needs a field, such as a tick or a
  predecessor, to make two checkpoints of one identity comparable.
- Whether the private-state digest is meant as protection against anything
  more than accidental damage.
- Who decides which dependencies a given private state requires, so that
  "declared" and "required" can be compared.
