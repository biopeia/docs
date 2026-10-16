# The operator material transfer

Reviewed against `lab` at commit `e7bb66c44517e279ca3180d929377682e251d796` (main on
2026-10-16); first written against `29e25d8`. Everything below describes the
later revision. Statements are marked by what
supports them: the code, the tests, or an accepted decision. A decision
states intent; it is not a result.

The code this component calls in other repositories is pinned in
`lab:pyproject.toml`:

- `embodiment` `c456401e9517bbb1fec02d84cbac7e94fddf9d68`
- `environment` `0ce1a4e3f4dd12529639f032929b8e09df4ce7d7`
- `observation` `d351df3d7cd2706fdd280a8d4e17359001689dd8`
- `world` `95bafc14ecd579b5573c4fadd1d7d3b5833b6c2f`

## What it is

Somebody outside the simulated life decides that a quantity should move from
a resource in the environment into a body, and asks for it. Nothing inside
the simulation caused it: no organism acted, no body touched anything.

### Fail-closed execution status

In the current implementation, **material transfer execution is explicitly
unsupported and fails closed**. Calling `apply_material_transfer` immediately raises
`MaterialTransferAuthorizationUnsupported` before touching World, inspecting
owner state, or writing checkpoints
(`lab:src/lab/interventions/material_transfer.py::apply_material_transfer`).

The reason is architectural: an `InterventionRequest` carries caller-declared
identifiers and constraints (`operator_id`, `intervention_id`, etc.); it does
not constitute authenticated identity or verified authorization. Under
Lab proposal #330 (`lab:docs/design/lab-target-authority-request-boundary-v1.md`), verified
authorization remains unsupported.

Integration tests executing the transfer path
(`tests/integration/test_material_transfer_intervention.py` and
`tests/integration/test_operator_material_transfer.py`) are skipped in CI
(`pytestmark = pytest.mark.skip`). A dedicated test verifies the fail-closed
rejection
(`tests/integration/test_material_transfer_authorization.py::test_material_transfer_fails_before_touching_world_or_owner_state`).

The module describes itself in those terms: "This is a caller-requested scalar
transfer, not an autonomous action, physical contact model, or demonstrated
material/energy equivalence."

It is a composition. Three other domains do the work that matters:

- Environment says how much the resource offers and removes what was taken.
  See [the finite resource](../environment/finite-resource.md).
- Embodiment says how much the body accepts.
- World commits the result as one causal tick. See
  [the durable World runtime](../world/durable-runtime.md).

Lab's own contribution is the request, the order in which the others are
asked, and one record of what happened: the evidence checkpoint.

## The request

A request (`lab:src/lab/interventions/material_transfer.py::InterventionRequest`)
names an operator, an intervention, a source, a target body, an upper bound on
the quantity, and a declared kind. It may also name a run, a study, an
experiment and a protocol.

The request is a declaration by the caller and nothing more. Its own
description is "Caller-declared request and constraints; not authentication or
permission." The operator identifier is a string the caller supplies; nothing
checks who the caller is.

### Intervention identity and run identity

The request keeps two identities apart, and the difference matters for what
may later be said about a transfer.

The **intervention identity** names one logical intervention. It is always
required. One intervention may contain multiple material acts; each has its
own **intervention action identity**. The **run identity** names a scientific
execution the act took place in, if there was one. The kind states which case
applies:

- an intervention declared as part of an experimental run must carry a run
  identity (`test_experimental_intervention_requires_real_run_context`);
- an intervention declared as non-experimental must not carry one. Read from
  the code; no test exercises this refusal.

The evidence checkpoint is filed under the intervention identity, never under
the run identity. The action identity and World transition identity are
distinct; the action identity is recorded in evidence and in a durable World
owner causal record. A run, when declared, remains separate
(`test_real_run_context_is_explicit_in_committed_evidence`). Tests cover
distinct actions under one intervention, duplicate-action rejection, immutable
intervention context and action-scoped limits.

What the code checks is the shape of these declarations: that a run identity
is present or absent, and not empty. It cannot know whether a run identity
names a real run. The tests establish that:

- a non-experimental request may carry a study and a protocol identifier
  while carrying no run;
- the same logical intervention can have multiple actions when immutable
  context matches and action identities are distinct;
- a transfer of zero commits a tick and writes evidence like any other.

## What happens in one transfer

Read from `lab:src/lab/interventions/material_transfer.py::apply_material_transfer`.

**Before anything is written**, Lab refuses the request unless all of the
following hold:

- the World is a durable World runtime, the resource is Environment's
  identified resource and the body is Embodiment's checkpoint object;
- the source and body named in the request are the identities the owners'
  own objects carry. Identity comes from the owners; the request can only
  agree with it (`test_request_identity_mismatch_fails_before_world_preparing`);
- the quantity requested is a finite, non-negative number no greater than the
  bound in the request;
- the World's registered owners are exactly this resource and this body;
- the bytes of the two objects in hand are the bytes of the checkpoints the
  World's current cut refers to. An object that has drifted from its committed
  state is refused
  (`test_world_genesis_checkpoint_identity_mismatch_fails_closed`).

A refusal at this stage leaves the World at its previous tick and usable.

**Then the exchange is worked out on copies.** Lab clones both objects through
their owners' checkpoint encodings and never changes the objects it was given
(`test_intervention_commits_durable_owner_cut_and_lab_evidence`). On the
copies:

1. the quantity offered is the lesser of what was requested and what the
   resource offers;
2. the body is handed a transfer of that quantity and answers how much it
   accepted. The transfer is labelled as an unspecified scalar material;
   Embodiment's acceptance rule ignores the label, as its own documentation
   says: "the current acceptance rule does not interpret either field";
3. the resource is debited by what the body accepted;
4. if the amount debited differs from the amount accepted, the transfer is
   abandoned with an error.

So four quantities exist and may all differ: requested, offered, accepted and
debited. Only the last two must be equal. With a resource holding 3 that
offers at most 2 per call and a body able to take 1.5 more, a request for 2.5
is offered 2, accepted 1.5 and debited 1.5. With a nearly full body the
resource loses only what the body took
(`test_short_body_acceptance_debits_only_accepted_material`).

In the body, the accepted quantity is added to the scalar Embodiment calls
its energy reserve, one for one. That is Embodiment's current rule, not a
claim by Lab that material is energy; the evidence labels the quantity
`unspecified_scalar_material`.

**Then World is asked to commit.** Lab calls one durable World tick and hands
it a callback. Inside the callback Lab writes three checkpoint files: the new
state of the resource, the new state of the body, and its own evidence. It
returns a reference to each. World verifies and publishes the cut as
described in [the durable World runtime](../world/durable-runtime.md); the
resource and the body take part as the registered owners, and the evidence
takes part as a participant of this step only, with a validation contract
that Lab registers in the same call.

One transfer is therefore exactly one World tick and exactly one offer by the
resource. The finite resource bounds a transfer per call and has no notion of
a tick ([the finite resource](../environment/finite-resource.md)); here the
two coincide because Lab asks once.

**After the commit**, Lab passes a small description of the tick to
Observation's projection and returns the committed World record, the action
identity, the evidence reference, the projected events and the two changed
copies. The caller must adopt the copies: a second call with the original
objects is refused because they no longer match the committed cut, and the
World stays committed and usable. Confirmed by an ad hoc run.

## The evidence checkpoint

The evidence is a small JSON document, written with sorted keys. The current
schema is version 2. It records intervention identity, action identity,
operator, declared kind, transition identity, World and causal tick, source
and target body, quantities and their label; run, study, experiment and
protocol appear only when supplied. Tests cover action identity, duplicate
action rejection, context immutability and action-scoped limits.

It is stored by a store that Lab provides
(`lab:src/lab/interventions/material_transfer.py::MaterialTransferCheckpointStore`).
Each file name is made of three parts: a shortened hash of the owner
identity, the checkpoint identifier, and the hash of the content. A file is
written once and never replaced: an existing file with different content is an error. The same store
writes the Environment and Embodiment checkpoint files. The bytes of those
come from the owners' own encodings; Lab writes them to disk without reading
their meaning.

What World receives is a
[checkpoint reference](../world/causal-manifest.md) and a Lab-owned validation
contract. The contract requires evidence schema version 2 and checks required
identity fields, including intervention and action identity; it does not
validate the scientific-method interpretation of the payload. The associated
owner causal record is opaque to World.

### What the record does and does not preserve

The current implementation establishes the following bounded behavior.

- **World does not interpret Lab evidence.** The generic tick record is distinct
  from the opaque owner causal record Lab commits for an intervention action.
  World preserves and validates that record under the owner contract; Lab
  retains semantic interpretation and scientific custody.
- **The action/evidence relation is durable in the tested journal path.** The
  journal retains the owner causal record beyond its tick, and tests cover
  retrieval after later ticks and restart. This does not make World the
  scientific custodian of the evidence.
- **At World's head the journal also keeps the evidence checkpoint reference
  of every tick.** World now writes a causal-cut record per tick that lists
  each participant's checkpoint reference, the step participant included
  (see [the durable World runtime](../world/durable-runtime.md)). In an ad
  hoc run, after a second transfer the journal still held the reference to
  the first transfer's evidence. The World revision Lab pins predates that
  record, so no Lab test exercises it.
- A failure after a callback writes evidence may leave an unreferenced file;
  its existence alone does not establish a committed intervention. The
  committed World owner record and Lab evidence reference are the tested path.

Tests establish the action/evidence relation in the journal and checkpoint
path used here. They do not establish a general power-loss guarantee, external
evidence immutability or scientific admissibility of physical interpretation.

## When it fails

A failure inside the tick, after the transition has opened, leaves the World
needing explicit recovery and the tick not advanced; the original objects are
unchanged (`test_owner_checkpoint_failure_leaves_no_committed_next_cut`). The
runtime then refuses further ticks, including a retry of the transfer, and
the files written for the failed tick, the evidence file among them, stay on
disk. Confirmed by an ad hoc run.

Lab provides no recovery step of its own. Recovery is World's, through the
restorer the caller supplies, as described in
[the durable World runtime](../world/durable-runtime.md).

## What reaches Observation

Lab no longer passes ad hoc telemetry to Observation's legacy inherited projection.
Instead, observation publication is an explicit, separate post-commit operation:
`lab:src/lab/interventions/material_transfer.py::publish_material_transfer_observations`.

The function takes the committed `MaterialTransferResult`, the durable World runtime,
and an in-process `ObservationPlane`. It emits two independently owned state claims:

1. **Environment resource state observation:** projected from the committed resource
   checkpoint bytes via `environment.identified_resource.project_committed_resource_state`
   and wrapped by `observation.environment_resource_state_observation`.
2. **Embodiment reserve state observation:** projected from the committed body
   checkpoint bytes via `embodiment.checkpoint.project_committed_reserve_state`
   and wrapped by `observation.embodiment_reserve_state_observation`.

These owner observations are published together against the exact committed cut
through `world.observation_publication.publish_committed_owner_observations`.

### Cryptographic and journal binding

Publication fails with a `ValueError` unless the following bindings strictly hold:

- **Explicit run context:** `result.experiment_id` and `result.run_id` must be present.
- **World cut match:** `cut.world_id` and `cut.causal_tick` must match `result.record`.
- **Exact transition record:** `world.records` must contain exactly one committed
  transition record (`world.causal_tick.committed`) for that tick, and `result.record`
  must equal it (`test_publication_rejects_missing_committed_world_transition_record`,
  `test_publication_rejects_ambiguous_committed_world_transition_records`).
- **Verified cut receipt:** `world.committed_cut_for` must match `cut`.
- **Exact Lab evidence cut participant:** `cut.owner_checkpoint_references` must contain
  exactly one Lab evidence checkpoint reference matching `result.evidence_reference`.
- **Committed action record:** `world.records` must contain exactly one matching
  `world.owner_record.committed` for `lab-intervention-evidence` and the action identity.
- **Evidence byte integrity:** the evidence file on disk must match its SHA-256 and
  pass `LabInterventionEvidenceCodec.validate_checkpoint`.
- **Payload context correspondence:** `intervention_id`, `intervention_action_id`,
  `transition_id`, `world_id`, `causal_tick`, `run_id`, `experiment_id`, `operator_id`,
  and `applicability` must match between the journal action record and the evidence payload.

The published messages are read back and associated with the Lab execution context
via `LabObservationAssociation` and `associate_current_messages`.

## Owner checkpoint restoration

When restoring or recovering a World after a transfer, World asks each registered owner's
checkpoint contract to validate the checkpoint and verify restoration.

Historically, Environment's resource class required an `OwnerRestorationReference`
instance method, creating a contract mismatch with World's 3-argument verification.
Lab resolves this through `lab:src/lab/interventions/material_transfer_restoration.py::MaterialTransferOwnerRestoration`.

The restorer:

1. Validates that the cut contains exactly one Environment and one Embodiment owner reference.
2. Reads and validates the checkpoint bytes against `IdentifiedFiniteResource.validate_checkpoint`
   and `EmbodimentCheckpoint.validate_checkpoint`.
3. Instantiates `IdentifiedFiniteResource.from_checkpoint_bytes` and `EmbodimentCheckpoint.from_bytes`.
4. Exposes `contracts(resource_id, body_id)`:
   - `_EnvironmentRestoreContract.verify_restoration` maps World's `CheckpointReference`
     into Environment's `OwnerRestorationReference(owner_identity, schema_version, checkpoint_sha256)`.
   - `_EmbodimentRestoreContract.verify_restoration` checks that re-serialized body bytes
     match the reference SHA-256 and passes `EmbodimentCheckpoint.verify_restoration`.

## What Lab does not own

- **The quantity in the resource.** Environment's object computes the offer
  and the debit. Lab chooses how much to ask for.
- **What the body accepts, and the body's state.** Embodiment's rule decides.
- **The commit.** World decides whether the tick happened.
- **Any organism.** None takes part. The World must hold exactly the resource
  and the body: a World that also registers an Organism owner is refused with
  "World genesis owner roster must exactly match the Environment and Embodiment
  owners". The transfer as written cannot be applied in a World where an
  organism lives.
- **Who the operator is, and whether they may.** Not checked anywhere here.
- **The meaning of the quantity.** No unit, no conversion, no contact.

What Lab does hold is the evidence checkpoint and the files of its store.

## Beside the accepted decisions

The decisions below describe the target. They are set beside the code and no
conformance is ruled here.

[ADR-0073](../../technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md),
item 8, is titled "Lab intervention is attributable, not privileged." It
says a causal intervention records "an explicit intervention identity,
applicable experiment/run, operator/principal reference, requested action,
target authority, causal applicability, and provenance". The evidence holds an
intervention identifier, the optional run, study, experiment and protocol, the
operator string, the requested quantity, the source and target, and the
declared kind. It holds no field for purpose and none naming the code
revision or the caller.

The same item says: "`intervention_id` identifies the intervention and is
never an alias for `run_id`". The code keeps the two in separate fields and a
test asserts they differ. It also accepts one intervention identifier for
several transfers.

It says interventions outside a run "cannot later be attributed to a
scientific run by timestamp proximity, operator, process, or intervention
identity." The code records the declared kind at the time of the transfer.
Nothing in this component performs or prevents a later attribution.

It says "Lab cannot silently write authoritative life state". The code
changes copies and leaves adoption to World's commit. It also says a
"caller-supplied `operator_id` is not authentication or authorization", which
the code repeats, and it limits the claim such a transfer supports to
"controlled experimental transfer only, not equivalence to an endogenous
physical mechanism without specific evidence".

[ADR-0101](../../technical/adr/ADR-0101-operator-control.md) says "Operator
Control is a `PRIVILEGED INTERVENTION CAPABILITY`, not an independent semantic
authority" and that its commands are "explicit attributable requests to the
relevant causal authority". ADR-0073 uses the words "not privileged" for Lab
intervention. The two records use the word in different senses or disagree;
this document does not settle which.

[ADR-0102](../../technical/adr/ADR-0102-lab.md) says of Lab: "It does not own
Organism, World, Environment, Embodiment, ordinary reproduction or ordinary
cognition." [ADR-0100](../../technical/adr/ADR-0100-observation-capability-and-evidence-custody.md)
says "Observation can emit facts; Lab/scientific apparatus records durable
evidence." The evidence checkpoint is the only durable record this component
writes for Lab; what it preserves over time is described above.

[ADR-0082](../../technical/adr/ADR-0082-canonical-reproduction-is-endogenous-to-life.md)
and
[ADR-0087](../../technical/adr/ADR-0087-organism-originates-ordinary-reproduction.md)
concern reproduction. They share the rule that Lab acts on life only as an
explicit, recorded intervention, and do not otherwise bear on a scalar
transfer.

## What this is not evidence of

The tests are contract tests of a composition. They show that, under the
conditions they set up, the pieces are called in the stated order and the
stated values are written. They are not scientific evidence, and no
experiment is described, run or authorised here. In particular nothing shows
that the transfer resembles feeding, contact, or any process an organism
could bring about.

## Time

The only clock is World's causal tick, advanced by one per committed
transfer. Lab reads no host time and writes no timestamp into the evidence.

## What supports this description

| Claim | Support |
|---|---|
| Validation of the request; refusal on identity mismatch and on drifted owner state; the committed cut and its four participants; content of the evidence; short acceptance; failure leaving recovery required; inputs not mutated | Code and tests in `lab:tests/integration/test_material_transfer_intervention.py` and `lab:tests/integration/test_operator_material_transfer.py` |
| The tests pass at the pinned revisions | Lab's continuous integration, which now installs the revisions pinned in `lab:pyproject.toml` (embodiment `028e2f912eccbe554a9d7f8543fe9dfe2bb94218`, environment `a979688e90b279ccfe003d77eddb787272fd5ebf`, observation `be82907d1d677b2362e369d15eb1e8e964d893aa`, world `4d264b24d0501a51d8b56b9cbe762aff3402da7b`) and runs `tests/integration`. `lab:MIGRATION.md` records 17 passed at those pins. Not run again for this document |
| What the tests do at the heads | An ad hoc run with the four other repositories at the heads named at the top: of 17 integration cases 14 passed and 3 failed; the 32 unit tests passed. The failures are described below |
| Refusal of a run identity on a non-experimental request; refusal of a World with other owners | Code only; neither was run or is tested |
| What the evidence contract checks | Code |
| A second action under one intervention identity; zero transfer; stale objects refused; retry refused after failure; files left by a failed tick; the two projected records and their content; the evidence reference kept in World's journal | Code, and ad hoc runs of the module with the other repositories at the heads named at the top |
| What a transfer may claim, what an intervention should record, who owns what | Accepted decisions ADR-0073, ADR-0100, ADR-0101, ADR-0102; statements of intent |
| The reading of a leftover evidence file; the bounded single-source, single-body scope | `lab:MIGRATION.md`; a statement by the repository, not a result |

The integration tests are now run by Lab's continuous integration. Its
workflow has a job that installs the pinned revisions and runs
`tests/integration`; at the revision first documented it ran the unit suite
only. The repository states what that establishes: "These CI jobs validate
packaging and the tested software contracts; they do not establish scientific
validity, efficacy, or equivalence."

The pinned revisions are behind the heads of the other repositories on the
day of review: Embodiment by 8 commits, Environment by 12, Observation by 2
and World by 28. Lab's migration notes now name the same revisions as
`lab:pyproject.toml`; in some places they still give the paths of the unit
tests without the directory they now live in.

### At the heads of the other repositories

The three integration cases that failed in the ad hoc run fail for two
reasons, and neither is in Lab's source.

- **Environment's resource no longer answers World's second question in the
  form World asks it.** The tests hand World the class of Environment's
  identified resource as that owner's checkpoint contract. World asks a
  contract two things with the same three arguments: is this checkpoint
  valid, and is this restoration verified. At Environment's head the second
  method of that class takes a restoration reference instead and belongs to
  an instance. World treats the resulting error as a refusal, so restoring a
  World after a transfer, or recovering one after a failed transfer, fails
  with "owner restoration validation failed"
  (`test_one_intervention_can_commit_distinct_actions_and_preserve_evidence_after_restart`,
  `test_candidate_journal_and_evidence_are_not_committed_if_manifest_publication_fails`).
  With a contract that answers in the three-argument form, the same restore
  succeeded (ad hoc run). A transfer itself still commits, because a commit
  asks only the first question. The repository records the mismatch in
  `lab:MIGRATION.md` and says the pins cannot move until it is resolved.
- **One test assumes the transfer's record is the first in the journal.** At
  World's head the first record is the causal-cut record of tick zero
  (`test_intervention_commits_durable_owner_cut_and_lab_evidence`). The
  transfer commits; the assertion about the position does not hold.

Both are recorded as findings. They concern how the repositories fit at
their heads, not the behaviour of the transfer at the revisions Lab tests.

No crash, power-loss or concurrent-process test exists for this component.

## Open questions

- Where the history of interventions is meant to live once the World has
  moved past the tick that referred to the evidence. World's journal now
  keeps the reference of every tick; whether that is the intended place is
  not stated.
- Whether an intervention identifier is meant to be unique, and who would
  check it.
- Whether the transfer is meant to work in a World that holds an organism.
- What Observation is meant to receive about a transfer. Today it is given
  the tick and the resource's remaining quantity, and nothing of the body.
- How the two uses of the word privileged in ADR-0073 and ADR-0101 relate.
