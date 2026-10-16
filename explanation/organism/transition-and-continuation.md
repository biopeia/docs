# The Organism transition boundary and the continuation registry

Reviewed against `organism` at commit `637bc21a7e2a1aa9e0870f55f134e839657687f4` (main on
2026-10-16); first written against `ba001179`. Everything below describes the
later revision. Statements are marked by what
supports them: the code, the tests, an ad hoc run, or an accepted decision.
Searches of the seven repositories were made on 2026-10-11 at the revisions
listed under [what supports this description](#what-supports-this-description).

## What it is

[The checkpoint envelope](identity-and-checkpoint.md) says which Organism some
bytes belong to. It does not say how far that Organism has come, whether it is
active, which body it is in, or which of two envelopes is the current one. Two
modules at the top of the Organism package add values that do.

The first (`organism:src/organism/transition.py`) wraps an envelope in a
**transition state**: the envelope, a counter of accepted steps, a lifecycle
word, the history of lifecycle changes, and two optional references, one to a
body context and one to a World tick. Two functions produce a next state from
a current one. One accepts an ordinary step and adds one to the counter. The
other changes the lifecycle word and leaves the counter alone.

The second (`organism:src/organism/continuation.py`) wraps a transition state
in a **continuation**: the state, an identifier for this line of
continuation, and, for a branch, where it came from. A **registry** remembers,
per Organism identity, the one continuation state it regards as current, and
hands out one lease on it at a time.

The nesting, from the outside in, is: continuation, transition state,
envelope, private bytes. Each layer is a JSON document carrying the next one
in base64.

Two limits frame everything below, and both are stated by the code itself.

The transition state's docstring: "The current bounded composition does not
claim that every Organism subsystem is already included; completeness is
governed separately by the owner-declared continuation closure contract."

The continuation module's opening: "The registry is an in-memory
compare-and-commit guard. Its durable snapshot may be stored by an Organism
owner, but this implementation does not coordinate separate processes or
copied stores and must not be treated as global identity uniqueness."

**No code outside the Organism repository uses either module.** In the
Organism source, one function calls the step acceptance (see
[who calls it](#who-calls-it)); nothing in source constructs a registry or
changes a lifecycle. Everything else that runs them is a test.

## The transition state

A transition state (`organism:src/organism/transition.py::OrganismTransitionState`)
is immutable and holds:

| Field | What it is |
|---|---|
| owner checkpoint | An envelope. Its private bytes are not read here |
| `organism_step` | A non-negative integer |
| lifecycle | One of `ACTIVE`, `DORMANT`, `TERMINATED`. It has no default: a state built without one is refused (ad hoc run) |
| lifecycle history | A tuple of records, each with an identifier, the state left, the state entered and a string called `request_ref` |
| embodiment | Optional. Three strings: a body identifier, an embodiment episode identifier, a morphology revision (`organism:src/organism/transition.py::EmbodimentContextRef`) |
| World correlation | Optional. A World identifier and a causal tick (`organism:src/organism/transition.py::WorldCausalCorrelation`) |

Construction checks that the history is consistent with the lifecycle: it
must start from `ACTIVE`, each record must leave the state the previous one
entered, no identifier may repeat, and the last state entered must be the
current lifecycle. The identity of the state is the identity of the envelope.

The embodiment reference is three identifiers and nothing else. The module
says: "Embodiment references identify the body context in which the Organism
participates; somatic/body state remains owned by Embodiment." Nothing here
checks that the body, the episode or the revision exist.

The World correlation is described by its class as "Optional correlation to a
World causal cut; never Organism time." The module opens with the same
separation: "World may correlate an accepted Organism transition with a World
causal tick, but that correlation is never the Organism progression counter."

### An ordinary step

`organism:src/organism/transition.py::accept_organism_transition` takes the
current state and a proposal: a new envelope, an embodiment reference and an
optional World correlation. It returns a new state whose counter is the old
one plus one, or it raises and returns nothing. It changes neither argument.

It refuses a proposal when:

- the proposed envelope belongs to another identity
  (`test_foreign_proposal_is_rejected_without_advancing_current_state`);
- the current lifecycle is not `ACTIVE`
  (`test_ordinary_progression_rejected_outside_active`);
- the proposed embodiment reference differs from the current one
  (`test_ordinary_transition_cannot_replace_embodiment_context`).

It accepts everything else (`test_accepted_transition_advances_organism_step_exactly_once`).
What that leaves unchecked, confirmed by an ad hoc run:

- **The envelope need not have changed.** A proposal carrying the same
  envelope as the current state was accepted and the counter rose to 1. The
  counter counts acceptances, not changes of state.
- **The private bytes are not opened.** Whether the proposed envelope holds a
  later state than the current one, or an earlier one, is not examined here.
- **The World correlation is copied, not compared.** A proposal correlated
  with tick 1 was accepted on top of a state correlated with tick 50 of the
  same World. A caller that wants World ticks to increase must check it; the
  one caller in source does.

The first and third are recorded in finding F-0143.

The counter and the World tick are independent by construction. The state is
immutable and only this function returns one with a higher counter, so a
state that is never passed to it does not advance, whatever World does; that
is read from the code. A proposal correlated with World tick 200 moved the
counter from 7 to 8
(`test_world_causal_tick_is_correlation_not_organism_step`). A second test
is named for the same property,
`test_world_step_without_organism_transition_does_not_advance`. Its body
binds the state to a second name and asserts that the two are equal; no
World step, and no call of any kind, occurs in it. It supports nothing
beyond what the immutability of the value already gives.

### A lifecycle change

`organism:src/organism/transition.py::transition_organism_lifecycle` takes the
current state, a target lifecycle, an identifier for the change and a
`request_ref`. It returns a state with the new lifecycle and one more record
in the history. The counter, the envelope and the World correlation are
carried over unchanged.

Four changes are permitted: `ACTIVE` to `DORMANT`, `DORMANT` to `ACTIVE`, and
either of those to `TERMINATED`. A change from a state to itself, and any
change out of `TERMINATED`, are refused
(`test_terminated_organism_cannot_transition_again`; `ACTIVE` to `ACTIVE` by
an ad hoc run).

A new embodiment reference may be given in exactly one case, when a `DORMANT`
state becomes `ACTIVE`
(`test_reactivation_can_bind_new_explicit_embodiment_context`). Given at any
other change it is refused (ad hoc run). Together with the third refusal of
the ordinary step, this is the only way the body context of a state can
change: the Organism is made dormant, then reactivated with a new reference.
The envelope and the counter pass through both changes untouched
(`test_reembodiment_preserves_identity_and_longitudinal_state`,
`test_dormant_reembodiment_can_reactivate_same_longitudinal_organism`, and an
ad hoc run comparing the envelope before and after).

What the function does not do should be stated as plainly. It does not decide
that an Organism becomes dormant or dies. It is told. Its docstring: "Body
death and World-presence termination are not inputs to this function; neither
implies longitudinal Organism termination." The test named for this,
`test_body_death_or_presence_loss_does_not_implicitly_terminate_organism`,
makes a state dormant and checks that it is not terminated; no body and no
World take part in it. `request_ref` is a non-empty string that nothing
resolves, and nothing checks who asked. Private state is not touched at
re-embodiment: no sense binding, no body-specific evidence and no part of the
cognitive payload is rebound or invalidated by this function, because it
never opens the envelope. Recorded, with the test of the previous section
that exercises no World step, as finding F-0146.

### Saving a transition state

A state encodes to one JSON object with nine fields, keys sorted, no optional
whitespace: a schema name, schema version 2, the identity, the counter, the
envelope in base64, the embodiment reference, the World correlation, the
lifecycle and the history. Decoding returns an equal state
(`test_transition_checkpoint_round_trips_progression_and_context`) and refuses
any other set of fields, a missing or invalid counter, a missing or invalid
lifecycle, and an envelope whose identity differs from the one in the
document (`test_transition_checkpoint_rejects_missing_or_invalid_organism_step`,
`test_restore_rejects_checkpoint_without_valid_lifecycle`,
`test_transition_checkpoint_rejects_foreign_nested_identity`).

The state offers the envelope's dependency check under the same name and
adds nothing to it (`test_dependency_verification_remains_owner_declared`).
What that check does and does not establish is in
[the envelope document](identity-and-checkpoint.md#what-the-closure-and-the-digests-do-not-establish).

## The continuation

A continuation (`organism:src/organism/continuation.py::OrganismContinuation`)
is a transition state, a continuation identifier, and optional ancestry. The
identifier is a wrapped UUID that the caller supplies; like the Organism
identity, it is never generated here. The class describes itself as "Portable
continuation metadata; it does not confer canonical authority." It encodes to
a JSON object of five fields with schema version 1 and decodes strictly
(`test_continuation_checkpoint_round_trips_without_claiming_canonical_authority`).

Ancestry is four values: the parent's Organism identity, the parent's
continuation identifier, the parent's counter, and the SHA-256 of the
parent's envelope. A continuation with ancestry must have an identity
different from its parent's.

### A branch

`organism:src/organism/continuation.py::branch_continuation` takes a source
continuation, a new identity, a new continuation identifier and a transition
state, and returns a continuation carrying that state with ancestry filled in
from the source (`test_branch_requires_new_owner_state_and_records_ancestry`).
It refuses the source's own identity or continuation identifier.

It does not make the branch's state. The caller must supply a transition
state whose envelope already belongs to the new identity. The docstring:
"This function never rewrites opaque private bytes or asserts that the fork
is canonical. The Organism owner must produce state for the new identity".
Nothing in the repository produces such a state from a source: no function
re-issues a cognitive payload under another identity (search of
`organism:src` for callers of `branch_continuation`, 2026-10-11: none). Nor
does the function compare the supplied state with the source. In an ad hoc
run a branch whose state held a different graph and a counter of 0 was made
from a source at counter 2; the ancestry recorded the source's counter and
digest, and that was the only connection between them.

A branch is a fork under a new identity. It is not an offspring: there is no
genome, no generation and no parent in the reproductive sense anywhere in
these two modules.

## The registry

`organism:src/organism/continuation.py::CanonicalContinuationRegistry` keeps,
for each Organism identity it knows, one record: a continuation identifier, a
counter, and the SHA-256 of the whole encoded continuation. It also keeps the
set of identities currently leased. It has five operations.

| Operation | What it does | Refuses |
|---|---|---|
| `register_genesis` | Records a continuation as current | An identity already recorded; a continuation with ancestry; a counter other than 0 |
| `designate_branch_from` | Records a branch as current for its own identity, given the source continuation | Ancestry that does not match the supplied source in identity, continuation identifier, counter or envelope digest; an identity already recorded |
| `acquire` | Returns a lease on a continuation | A continuation that is not byte for byte the recorded one; an identity already leased |
| lease `commit` | Replaces the record with a proposed next continuation | See below |
| lease `close` | Ends the lease | Nothing |

A commit is accepted in two shapes and no other
(`test_registry_rejects_ordinary_step_committed_directly_from_non_active_state`,
`test_registry_rejects_direct_ordinary_commit_with_changed_embodiment_context`,
`test_registry_commits_lifecycle_without_advancing_organism_step`,
`test_registry_allows_reactivation_to_bind_new_embodiment_context`):

- an ordinary step: both states `ACTIVE`, the counter exactly one higher, and
  the lifecycle history and embodiment reference unchanged;
- a lifecycle change: the counter, the envelope and the World correlation
  unchanged, the history one record longer, and the embodiment reference
  unchanged unless the change is `DORMANT` to `ACTIVE`.

In both, the identity, the continuation identifier and the ancestry must stay
the same. A commit that skipped a counter value was refused (ad hoc run).

What this gives, within one registry object:
`test_registry_rejects_duplicate_live_restore_and_stale_checkpoint` shows that
a second lease on a leased identity is refused, and that an earlier
continuation is refused once a later one has been committed. That is the
behaviour [ADR-0091](../../technical/adr/ADR-0091-one-non-terminated-continuation-per-organism-identity.md)
describes when it says "Restoring an older checkpoint while a later
continuation remains active is a fork unless the later continuation is
explicitly retired first".

### What the registry does not establish

Read from the code and confirmed by an ad hoc run at that revision. The first
three are limits the module declares.

- **It holds for one object in one process.** The registry writes its records
  to bytes and reads them back
  (`test_registry_snapshot_restores_exact_owner_authority_state`). The set of
  leased identities is not written. In the run, a continuation leased from
  one registry was leased again from a second registry restored from the
  first one's snapshot. The class says of itself: "The lock serializes
  operations on this registry object only. A deployment requiring
  cross-process safety must atomically persist/update its authority state and
  perform compare-and-commit there." No such store exists in the repository.
- **Designating a branch checks consistency, not authenticity.** The source
  continuation is an argument. A registry that had never recorded the source
  accepted the branch and leased it. The docstring: "This checks consistency,
  not authenticity. Durable owner storage must authorize the source and
  atomically record the resulting identity."
- **Genesis is whatever is registered first.** Any continuation at counter 0
  without ancestry is accepted for an identity not yet recorded. The
  docstring calls it "an explicitly authorized initial continuation"; the
  method receives no authorization and checks none.
- **An ordinary commit does not require the envelope to change**, for the
  same reason the step acceptance does not (ad hoc run).
- **A terminated continuation can still be leased.** Its record stays, and
  `acquire` compares bytes, not lifecycle. Nothing can then be committed from
  it, because no lifecycle change leaves `TERMINATED` and an ordinary step
  needs `ACTIVE` (ad hoc run for the lease; code for the rest).
- **Nothing links the registry to World.** No World checkpoint reference
  names a continuation identifier, and the registry reads no World state.

The first three are recorded as finding F-0141.

## Who calls it

Searched in all seven repositories on 2026-10-11 for
`accept_organism_transition`, `transition_organism_lifecycle`,
`OrganismTransitionState`, `OrganismContinuation`,
`CanonicalContinuationRegistry` and `branch_continuation`.

- In source, one function calls `accept_organism_transition`: the composed
  step described in
  [from an opaque sense signal to an accepted step](sense-to-checkpoint-transition.md).
  That function builds no continuation and uses no registry.
- No source in any repository calls `transition_organism_lifecycle`,
  constructs a registry, registers a genesis, designates a branch or calls
  `branch_continuation`. The top-level package re-exports the names.
- The callers are the Organism repository's own tests:
  `organism:tests/test_transition.py`, `organism:tests/test_continuation.py`
  and `organism:tests/source_unit/cognition/test_owner_transition.py`.
- The other six repositories do not mention any of the names. In particular,
  World's integration tests still advance a cognitive state directly and wrap
  it in a bare envelope; no World test advances `organism_step`.

So at this revision the counter, the lifecycle and the registry are values
with tested rules that nothing outside the Organism's tests drives. No
Organism has been made dormant, re-embodied, branched or terminated by
running code. Recorded as finding F-0140.

## Time and randomness

Neither module reads a clock or draws a random number. Identifiers are
supplied by the caller. The counter advances only by acceptance. The World
tick is stored as given. The digests are SHA-256 of deterministic encodings.

## At each lifecycle boundary

| Boundary | What happens | Support |
|---|---|---|
| Birth | A caller builds a state with a counter and a lifecycle it supplies; the registry accepts a first continuation only at counter 0 and without ancestry | Code, tests and an ad hoc run |
| Checkpoint | The transition state, the continuation and the registry's records each encode exactly; the set of live leases is not written | Code, tests and an ad hoc run |
| Restart | Each decodes strictly to an equal value; a restored registry has no live lease | Code, tests and an ad hoc run |
| Re-embodiment | The embodiment reference is replaced when a dormant state is reactivated with a new one; the counter, the envelope and the identity are unchanged; no private state is rebound | Code, `test_reactivation_can_bind_new_explicit_embodiment_context`, `test_reembodiment_context_and_longitudinal_state_survive_continuation_restore` |
| Reproduction | No operation exists. A branch is a fork with recorded ancestry under a new identity, made from state the caller supplies | Code; search of the repository |

## Beside the decisions

[ADR-0081](../../technical/adr/ADR-0081-the-canonical-organism-is-longitudinal.md)
says canonical re-embodiment "preserves same-Organism continuity and does not
silently reset cognition". The two-step change of body context leaves the
envelope byte for byte as it was, which is consistent with that as far as the
envelope goes.

[ADR-0088](../../technical/adr/ADR-0088-lifecycle-event-ontology.md) keeps
body death, Organism dormancy, World-presence termination and Organism death
distinct, and says: "The same Organism may persist dormant without active
embodiment and later re-embody in a new episode". The three lifecycle words
and the reactivation rule have that shape. The same decision says Organism
death is "resolved under an explicit lifecycle contract involving continuity
state, body viability, recoverability and authorized rules". Here termination
is one function call with a string; no such contract is evaluated.

[ADR-0091](../../technical/adr/ADR-0091-one-non-terminated-continuation-per-organism-identity.md)
requires that "Canonical-continuation designation must be explicit and
recorded" and reserves "its owner/storage topology" to a later pass. The
registry is an explicit, recorded designation inside one process and declares
that it is not more. The same decision says of branches that they "share
ancestry/provenance but are not offspring, do not advance generation";
the ancestry record matches that description.

[ADR-0092](../../technical/adr/ADR-0092-organism-owns-the-meaning-of-its-private-longitudinal-state.md)
places the meaning of private state with the Organism. Both modules live in
the Organism package, import nothing from another domain, and never read the
private bytes they carry.

These decisions define the target architecture. They are set beside the code
without a ruling on conformance. Nothing drives these values outside tests,
so conformance of a running system cannot be examined.

## What supports this description

| Claim | Support |
|---|---|
| Shape of a transition state, its construction checks, the two functions and what each refuses | Code of `organism:src/organism/transition.py` and tests in `organism:tests/test_transition.py` |
| An unchanged envelope is accepted as a step; a lower World tick is accepted; no default lifecycle; `ACTIVE` to `ACTIVE` refused; a new embodiment reference refused outside reactivation; the envelope is identical after dormancy and reactivation | Code, and one ad hoc run of the module at `organism` `ba0011797a6a3b4d48c7731651e50560c4043f18`; no test is kept for the first two |
| Shape of a continuation and of ancestry, the branch function, the registry's operations and the two shapes of commit | Code of `organism:src/organism/continuation.py` and tests in `organism:tests/test_continuation.py` |
| A branch state unrelated to its source is accepted; a restored registry grants a second lease; a registry that never saw the source designates the branch; a terminated continuation can be leased; a skipped counter is refused | Code, and the same ad hoc run |
| One caller of the step acceptance in source; no caller of the lifecycle change, the registry or the branch function in the source of any repository; no mention in the other six repositories | Searches on 2026-10-11 at `organism` `ba0011797a6a3b4d48c7731651e50560c4043f18`, `world` `95f5064c6b06bd66bb58a72110b066afe4ca70b0`, `embodiment` `597cc4a09f4a5c94095b17ad0f2ba510df6d02c3`, `environment` `e91bb67f81f3bc15715489cf1262328934454f1b`, `modality` `79b779152d4bff2ab4191dc6601c8f1640e4cae3`, `observation` `6aac3c76684834722440f53c9d8604ac4c16b138`, `lab` `29e25d85e796d96a3f2e830fd870a2f74e8e2266` |
| The limits of the registry | The module's own docstrings, and the ad hoc run |
| What continuity, lifecycle and canonical designation must mean | Accepted decisions ADR-0081, ADR-0088, ADR-0091, ADR-0092; statements of intent, not test results |

No transition state, continuation or registry snapshot written by a running
Organism was examined, because no component at this revision writes one
outside tests.

## Open questions

- Which component holds the registry for a running Organism, where its
  snapshot is stored, and what makes that store the single authority that
  ADR-0091 asks for.
- Which component decides that an Organism becomes dormant or terminated,
  from what evidence, and what `request_ref` is meant to resolve to.
- Whether a step that leaves the envelope unchanged should count.
- What produces the private state of a branch under its new identity.
- Whether World's checkpoint references are meant to name a continuation, a
  transition state or a bare envelope.
