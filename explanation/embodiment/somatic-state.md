# Somatic state: what a body holds

Reviewed against `embodiment` at commit `6114f3d9bcc0d5c44ecbfb6262f87f5824f92903`.
Everything below describes that revision. Statements are marked by what
supports them: the code, the tests, an ad hoc run, or an accepted decision.
The ad hoc runs were made at an earlier revision,
`a5129f03aa4b024e33d332f917b9235afe97959c`, and were not repeated. Between
the two revisions the body record and the transfer module are unchanged; the
ledger, the configuration and the checkpoint changed only in what a
checkpoint carries and what restoring refuses (comparison of the five source
files on 2026-10-10).

## What it is

A body in Biopeia is more than a position. It has a reserve of energy that
activity draws down, a structure that can be worn, an age, and a condition
that ranges from active to dead. The accepted architecture gives all of
this to the body and not to the Organism that inhabits it: "A body instance
owns its energy reserve/capacity, structural integrity, accumulated damage,
age, senescence and viability"
([ADR-0094](../../technical/adr/ADR-0094-somatic-state-ownership-body-holds-organism-regulates-and-feels.md)).

This document describes the code that holds that state today. It has to be
read with one fact in mind. What exists is a **record with a few
operations**: values, bounds, a way to spend and receive energy, a rule
from energy to condition, and a checkpoint. What does not exist is the
process that would make the record evolve by itself. Nothing in this
repository advances a body through time. The repository's migration record
says the historical per-tick body cycle was dropped and that new somatic
dynamics "remain a required
TARGET capability, but are not implemented"; an open issue,
[embodiment#20](https://github.com/biopeia/embodiment/issues/20), asks for
them. The repository calls itself "a migration rehearsal, not a declaration
that the extracted code
already satisfies the ratified TARGET contracts".

The names in the code (`LivingBodyState`, `VitalState`, `fatigue`,
`senescence`) are names. What each one does is stated below, and for several
the answer is that it is stored.

## The body's record

One mutable object
(`embodiment:src/embodiment/physiology.py::LivingBodyState`) holds:

| Value | Bounds | What this repository does with it |
|---|---|---|
| energy reserve, and its maximum | 0 to the maximum; maximum positive | spent, received, compared with thresholds |
| structural integrity | 0 to 1 | lowered by wear, raised by a positive change; at 0 the body is marked dead |
| per-structure records: integrity, wear, damage, repair progress, functional capacity | each 0 to 1 | integrity, wear, damage and repair progress change with every structural change; functional capacity is never written |
| vital state, number of transitions, tick of death | five states | set by the rules below |
| age, in ticks | non-negative integer | incremented by one call, while alive |
| temperature, fatigue, growth progress, senescence | each 0 to 1 | validated, checkpointed, exported; never changed |
| per-kind capacity, replenishment and reserve | see the ledger | owned here, operated by the ledger |

The energy amounts have no unit. The code says so where it exports them:
"This method deliberately makes no
claim that they are joules or any other physical energy unit", and labels
them a model amount.

The bounds are checked when the object is built and when it is restored.
They are not checked on assignment: the object is an ordinary mutable
record, and setting the reserve to a negative number was accepted (ad hoc
run).

### Structure

Structural integrity is one number when no structures are tracked. When
they are, it is the mean of their integrities and is recomputed from them.
A structural change is applied identically to every structure: the code
describes it as a "Uniform, untargeted integrity change". A negative change
adds to each structure's wear and damage; a positive one adds to its repair
progress and does not reduce wear or damage (ad hoc run).

No test in this repository exercises structures. No code in it creates
them.

## Energy: one pool, four accounts

The ledger
(`embodiment:src/embodiment/metabolism.py::MetabolicLedger`) is the way
activity is charged to a body. It keeps four named accounts, `observation`,
`cognition`, `persistence` and `maintenance`, each with a capacity, a
reserve and a replenishment per ledger tick. The ledger does not hold these
numbers itself: they are dictionaries on the body's record, which is how
they come to be checkpointed with it.

The accounts are bookkeeping, and the code is direct about it: "Per-kind
balances are bounded accounting channels, not independent physical
currencies". There is one physical pool, the body's energy reserve.

- **A charge** names an account and an amount. The account's reserve falls,
  no lower than minus its capacity; the amount spent this tick rises, no
  higher than twice the capacity; and the body's energy reserve falls by
  the full amount, no lower than zero
  (`test_body_backed_metabolic_charge_debits_physical_energy_once`).
- **Advancing** the ledger refills each account by its replenishment up to
  its capacity, charges the maintenance account, increments the ledger's
  tick, returns a snapshot and clears the amounts spent. Refilling accounts
  adds nothing to the body's energy: after several advances the accounts
  were full and the energy reserve was where the charges had left it (ad
  hoc run).
- **Intake** adds to the body's energy up to its maximum and credits either
  one account or, for untyped intake, the accounts in proportion to their
  deficits.

Because the two are bounded differently, the sum of the accounts and the
energy reserve are not kept equal, and are not meant to be.

A ledger built without a body creates one whose energy and maximum are the
sum of the account capacities, 4.0 with the defaults. A body built by
itself starts with 1.0 of 2.0. A ledger attached to an existing body leaves
that body's energy as it finds it (ad hoc run).

The intent this corresponds to is in ADR-0094: "all embodied expenditure,
including cognition, is charged to body somatic state". The same decision
says it does not determine "per-kind metabolic reserve ownership". The code
places the per-kind accounts on the body's record; the migration record
notes that ownership of this accounting "remains subject to boundary
review".

## From energy to condition

The ledger turns the ratio of energy reserve to maximum into a pressure:
`normal`, `elevated` below 0.5, `severe` below 0.2, `unrecoverable` at 0 or
below. The three thresholds are the only values of the physiology
configuration that any code in this repository reads. The configuration
(`embodiment:src/embodiment/physiology_config.py::PhysiologyConfig`)
declares twenty-six more, for repair, fatigue, temperature, activity
scaling, growth, senescence and reproduction. They are validated and
unused.

A controller
(`embodiment:src/embodiment/physiology.py::PhysiologyController`) maps
pressure to vital state when it is advanced:

```text
no energy, or unrecoverable  ─▶ dead
severe                       ─▶ agonizing, or dormant if the caller says the body is resting
elevated                     ─▶ stressed
normal                       ─▶ active
```

All states but one are reversible. A body went from active to stressed to
agonizing to dormant and, after receiving energy, back to active (ad hoc
run). Dead is final. Energy offered to a dead body is not accepted
(`test_matching_transfer_to_dead_body_is_not_accepted`); that no transition
leaves the state and that attempting to mark the body alive raises are read
from the code and were confirmed by the same run.

`VitalState.DEAD` is the death of a body in this record. The migration
record states that the extraction "does not reinterpret it as TARGET
`ORGANISM_DEATH`". Nothing here is a statement about an Organism dying.

### Three ways to die, at different moments

Read from the code and confirmed by a run.

- Spending energy directly on the record, through its own method, marks the
  body dead the moment the reserve reaches zero
  (`test_depleted_body_state_uses_current_code_dead_vital_label`).
- Structural integrity reaching zero marks it dead at once.
- Spending through the ledger does not. A charge that emptied the reserve
  left the body with zero energy, pressure `unrecoverable` and vital state
  `active`. It became dead only when a controller was next advanced.

So the same depletion is or is not death, for a while, depending on which
path spent the energy.

## Clocks

Four counters appear, and nothing in this repository ties them together.

- The body's **age** advances by one when its owner calls the method for
  it. Nothing here calls it.
- The **ledger's tick** advances by one each time the ledger is advanced.
- The controller is advanced with a **tick supplied by the caller**, which
  becomes the tick of death if the body dies in that call.
- The **World causal tick** does not appear in somatic state at all.

The tick of death is documented as a "Body-local age tick". When death comes
from the record's own methods it is the body's age. When it comes from the
controller it is whatever the caller passed: a body of age 0 was given tick
of death 3 (ad hoc run). No physical duration enters any of these
operations.

## Receiving material

One function lets something outside the body add to it
(`embodiment:src/embodiment/intake.py::absorb_material_transfer`). A
transfer names a source, a target body, an amount and a composition. If it
is addressed to another body nothing happens and zero is returned; otherwise
the body accepts as much as fits below its maximum, and nothing if it is
dead (`test_transfer_to_matching_body_accepts_only_available_capacity`,
`test_transfer_for_different_body_is_rejected_without_state_change`). The
source and composition are not interpreted. This path raises the energy
reserve without crediting any account of the ledger (ad hoc run). Where the
material came from and whether the transfer was permitted are the caller's
business; the module says "The caller owns obtaining and authorizing the
transfer". The caller that exists is Lab's operator material transfer
(`lab:src/lab/interventions/material_transfer.py`), not documented here.

## Checkpoint

A body's record and its ledger are saved together under a body identifier
and an embodiment episode identifier
(`embodiment:src/embodiment/checkpoint.py::EmbodimentCheckpoint`), as
canonical JSON. The ledger must be bound to that very record. Restoring
rejects unknown fields in the envelope, a field given twice, a wrong or
boolean schema version, numbers too large to be finite, and a ledger whose
stated energy disagrees with the body's
(`test_checkpoint_round_trip_is_deterministic_and_preserves_episode_identity`,
`test_checkpoint_rejects_unknown_envelope_fields`,
`test_checkpoint_rejects_duplicate_json_fields`,
`test_checkpoint_rejects_boolean_schema_version`,
`test_checkpoint_rejects_oversized_json_integers`,
`test_checkpoint_rejects_ledger_body_energy_mismatch`,
`test_checkpoint_requires_ledger_bound_to_same_body_object`).

The type answers the two questions World's durable runtime asks of an
owner: whether bytes are valid for an identity and a schema, and the same
after restoration
(`test_owner_checkpoint_validation_checks_identity_schema_and_bytes`). The
identity compared is the body identifier; the episode is not part of the
question. The schema it answers to is named `embodiment-checkpoint-v2`; the
earlier name is refused.

The ledger's part of the bytes carries the physiology configuration and
the amounts spent in the current tick. A ledger with its own thresholds and
a charge already made reports the same configuration, the same pressure and
the same spent amount after a round trip, and advancing the original and
the restored ledger gives the same result
(`test_checkpoint_preserves_custom_physiology_and_pending_spend`). A caller
may pass a configuration when restoring a ledger; one that differs from the
stored one is refused (code). The ledger's part is refused if it is in the
earlier format, lacks a field or has an unknown one, or holds a
configuration or spent amounts that are invalid or out of range
(`test_metabolic_checkpoint_rejects_old_schema_missing_or_unknown_fields`,
`test_metabolic_checkpoint_rejects_invalid_config_and_spent_values`,
`test_metabolic_checkpoint_rejects_out_of_range_pending_spend`). Bytes
written in the earlier format are therefore not restorable; no conversion
exists in the repository (code).

An earlier revision saved neither the configuration nor the spent amounts,
recorded as finding F-0025; that is no longer so.

The module calls this "a migration-stage format, not a finalized portable
World checkpoint". One limit remains:

- **It names no World and no causal tick.** The bytes say which body and
  which episode, not when. The physical state of the same body is a
  separate checkpoint that does name them; see
  [the physical state](physical-state.md).

## What crosses to the Organism, and what does not

ADR-0094 says somatic state reaches the Organism "only through body somatic
state → interoceptive transduction → opaque Organism signal". This
repository contains the first of those three and neither of the others. The
record offers a read-only export of its values for observation. No code
here transduces them, and the record's own note says that "Cognition never
receives these field names directly". Whether that holds is a property of
other repositories and was not examined.

Neither does somatic state reach the solver. The projection of the body for
a physical step states that no energy, integrity, temperature, fatigue,
damage or viability value is converted to mechanics, and the
[actuation projection](actuation-projection.md) projects commands for a
dead body.

## Lifecycle

What the code shows: a record is created with defaults or given values; it
is preserved by the checkpoint; it survives a
restart only if those bytes were stored elsewhere.

What the code does not contain: any path for re-embodiment or reproduction.
That this state ends with the body, is not transferred to a new one, and is
not inherited by offspring is the intent of ADR-0094. The configuration
carries three reproduction parameters that nothing reads.

## Who uses it

Across the main branches of the seven domain repositories on 2026-10-09,
searched for this document: Lab's material transfer and two of World's
integration tests build or restore the checkpoint. Nothing outside this
repository's own code and tests charges a ledger or advances a controller.
The Organism repository does not import this package.

## What supports this description

| Claim | Support |
|---|---|
| Record round trip, charge debiting energy once, depletion marking death, transfers, checkpoint strictness and owner validation | Code and tests in `embodiment:tests/test_somatic_state.py`, `embodiment:tests/test_intake.py` and `embodiment:tests/test_checkpoint.py`, run at that revision (all pass) |
| Bounds not enforced on assignment; structure arithmetic; account bounds; refilling adds no energy; defaults of body and ledger; reversibility of states; dead is final | Code, and one ad hoc run of the modules at the earlier revision named above; no test is kept for these |
| A ledger charge empties the reserve without death; tick of death taken from the caller | Code, and the same ad hoc run |
| Which values are never changed, which configuration values are never read, who calls what | A search of the source at that revision, and of the other repositories' main branches |
| What a body owns, what reaches the Organism, what ends with a body | Accepted decisions ADR-0094 and [ADR-0095](../../technical/adr/ADR-0095-surviving-semantic-authorities.md); statements of intent, not test results |

No trajectory of a body over time exists to examine: no run, no stored
checkpoint from an experiment and no experiment was used. Nothing here
supports a claim about viability, homeostasis or metabolism as phenomena.

## Notes in the code that point elsewhere

Several comments describe a larger system than this repository holds. They
refer to an audit file under `research/audits/` that is not in the
repository, to a "homeostatic repair cycle" that is not in it, to the
"persistent Symbiont historical scheduler
cycle", and to continuous wear being "deferred to Phase M2". One states
that any direct assignment of integrity is routed through the single
structural write path; the record has no such attribute, and assigning the
aggregate directly left it at 0.99 while the mean of the structures was
0.65 (ad hoc run).

## Open questions

- What advances a body through time, in which domain, on which clock. This
  is the subject of embodiment#20.
- Whether the configuration, now carried by every checkpoint, may change
  during the life of a body. Restoring refuses a different one; nothing
  else in the code changes or fixes it.
- Whether depletion through the ledger should be death at once, as it is
  through the record.
- Whether the per-kind accounts are somatic state. ADR-0094 leaves it
  undecided.
