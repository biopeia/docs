# The operator material transfer

Reviewed against `lab` at commit `4d5ff706b8329ddf25e1852ad53cbde5285d2851`.
Everything below describes that revision. Statements are marked by what
supports them: the code, the tests, an ad hoc run, or an accepted decision.
A decision states intent; it is not a result.

The code this component calls in other repositories was read at
`embodiment` `a5129f03aa4b024e33d332f917b9235afe97959c`,
`environment` `f97ec22272b6be1e6742770e37cd370e7d96d6bc`,
`observation` `397c0b4691b5e460e6ebc3914f9820ff434a3661` and
`world` `c162b67e698de9b47450264402677b0165e6e20e`.

## What it is

Somebody outside the simulated life decides that a quantity should move from
a resource in the environment into a body, and asks for it. Nothing inside
the simulation caused it: no organism acted, no body touched anything. The
operator material transfer is the one place in Lab where such a request is
carried out, and it is built so that the request leaves a trace and so that
Lab itself decides as little as possible.

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

The **intervention identity** names this act of intervening. It is always
required. The **run identity** names a scientific execution the act took
place in, if there was one. The kind states which case applies:

- an intervention declared as part of an experimental run must carry a run
  identity (`test_experimental_intervention_requires_real_run_context`);
- an intervention declared as non-experimental must not carry one. Read from
  the code; no test exercises this refusal.

The evidence checkpoint is filed under the intervention identity, never under
the run identity, and when a run is declared it is written into the evidence
as a separate field
(`test_real_run_context_is_explicit_in_committed_evidence`). The identifier of
the World transition is a third identity, and must differ from the
intervention identity
(`test_transition_id_is_distinct_from_intervention_id`).

What the code checks is the shape of these declarations: that a run identity
is present or absent, and not empty. It cannot know whether a run identity
names a real run. Three further things were confirmed by running the module:

- a non-experimental request may carry a study and a protocol identifier
  while carrying no run;
- the same intervention identity can be used for two successive transfers in
  one World, and both commit;
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
Observation's projection and returns the committed World record, the evidence
reference, the projected events and the two changed copies. The caller must
adopt the copies: a second call with the original objects is refused because
they no longer match the committed cut. Confirmed by running the module.

## The evidence checkpoint

The evidence is a small JSON document, written with sorted keys. Its content
is fixed by `test_intervention_commits_durable_owner_cut_and_lab_evidence`:
the intervention and operator identifiers, the declared kind, the transition
identifier, the World and the causal tick, the source and the target body,
the four quantities, and the label of the quantity. Run, study, experiment
and protocol appear only when the request carried them.

It is stored by a store that Lab provides
(`lab:src/lab/interventions/material_transfer.py::MaterialTransferCheckpointStore`).
Each file name is made of three parts: a shortened hash of the owner
identity, the checkpoint identifier, and the hash of the content. A file is
written once and never replaced: an existing file with different content is an error. The same store
writes the Environment and Embodiment checkpoint files. The bytes of those
come from the owners' own encodings; Lab writes them to disk without reading
their meaning.

What World is told about the evidence is a
[checkpoint reference](../world/causal-manifest.md) and a contract. The
contract Lab supplies answers yes to any JSON object whose schema version is
1 and whose intervention identifier equals the identity in the reference. It
does not look at any other field. Confirmed by running the module: a document
holding only those two fields is accepted.

### What the record does and does not preserve

Three facts, each confirmed by running the module, belong together.

- **The World record does not carry the intervention.** The record World
  appends for the tick holds the acting presence and nothing about the
  transfer. Lab's migration notes say so: "World's generic causal record does
  not itself contain the intervention payload." The only link between the
  tick and the evidence is the reference in the World manifest.
- **That link lasts one tick.** The evidence is a participant of its own step
  only. After the next committed tick the manifest no longer refers to it,
  and no file in the World's durable state names the earlier evidence or its
  intervention. The evidence file remains on disk.
- **A failed transfer can leave an evidence file too.** If World fails after
  the callback has written the files, the evidence file stays on disk,
  complete, stating the tick it would have had. The migration notes state how
  it must be read: "an orphaned file after a failed preparation is not accepted
  state or evidence". Nothing in the file says so.

Taken together: while a transfer is the latest committed tick, the manifest
tells its evidence apart from a leftover. Once the World has moved on, the
durable state examined here no longer distinguishes an evidence file whose
transfer committed from one whose transfer did not. Whether another record is
meant to hold that history is not decided in the code.

## When it fails

A failure inside the tick, after the transition has opened, leaves the World
needing explicit recovery and the tick not advanced; the original objects are
unchanged (`test_owner_checkpoint_failure_leaves_no_committed_next_cut`). The
runtime then refuses further ticks, including a retry of the transfer.
Confirmed by running the module.

Lab provides no recovery step of its own. Recovery is World's, through the
restorer the caller supplies, as described in
[the durable World runtime](../world/durable-runtime.md).

## What reaches Observation

After the commit Lab offers Observation's projection six values: a source
name, the body identifier, the tick (twice), a body kind, the ratio of the
body's reserve to its capacity, and the quantity remaining in the resource.
The projection returns three events, of types body, cognition and vitals
(`test_intervention_commits_durable_owner_cut_and_lab_evidence`). None of
them carries a run identifier.

Confirmed by running the module at these revisions:

- the remaining quantity appears in the vitals event;
- the reserve ratio appears in no event. The projection copies only the keys
  it knows, and this is not one of them;
- the event of type cognition carries the source, the body identifier and the
  tick, and nothing else. No organism takes part in the transfer; the event
  exists because the projection always returns three. Its type is a name
  given by the projection and describes no cognitive content here.

The projection describes itself as working "without fabricating absent
observations". The events are returned to the caller; this component does not
store or send them.

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
| The tests pass | Run for this document in a clean environment built from the revisions pinned in `lab:pyproject.toml` (embodiment `0562febd8dfffaa826c339600bb548ea172fa256`, environment `a979688e90b279ccfe003d77eddb787272fd5ebf`, observation `cb07ace206058719a9aa9df65e2eb1f837130ee9`, world `dadf2743ee4ff9f22703d2d6643fca9fd9bfa025`): 10 integration and 18 unit tests passed. Run again with the four other repositories at the revisions named at the top: the 10 integration tests passed |
| Refusal of a run identity on a non-experimental request; refusal of a World with other owners | Code only; neither was run or is tested |
| The evidence contract checking two fields | Code, and an ad hoc run |
| Reuse of an intervention identity; zero transfer; stale objects refused; retry refused after failure; the World record carrying no intervention; the evidence reference lasting one tick; a complete evidence file left by a failed tick; the reserve ratio absent from the events; the content of the cognition event | Code, and ad hoc runs of the module, once with the other repositories at the pinned revisions and once at the revisions named at the top, with identical output |
| What a transfer may claim, what an intervention should record, who owns what | Accepted decisions ADR-0073, ADR-0100, ADR-0101, ADR-0102; statements of intent |
| The reading of a leftover evidence file; the bounded single-source, single-body scope | `lab:MIGRATION.md`; a statement by the repository, not a result |

The integration tests are not run by Lab's continuous integration, which
runs the unit suite only. The repository says so: "A green package CI run
validates only the isolated unit suite; it is not integration evidence."

The pinned revisions are between one and four commits behind the main
branches of the other repositories on the day of review. Lab's migration
notes name a different, older set of revisions from the one in
`lab:pyproject.toml`, and in some places give the paths of the unit tests
without the directory they now live in.

No crash, power-loss or concurrent-process test exists for this component.

## Open questions

- Where the history of interventions is meant to live once the World has
  moved past the tick that referred to the evidence.
- Whether an intervention identifier is meant to be unique, and who would
  check it.
- Whether the transfer is meant to work in a World that holds an organism.
- Whether the body's reserve ratio is meant to reach Observation, and whether
  an event of type cognition should be produced for an act no organism took
  part in.
- How the two uses of the word privileged in ADR-0073 and ADR-0101 relate.
