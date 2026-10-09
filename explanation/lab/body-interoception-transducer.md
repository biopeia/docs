# The body interoception transducer

Reviewed against `lab` at commit `4d5ff706b8329ddf25e1852ad53cbde5285d2851`.
Everything below describes that revision. Statements are marked by what
supports them: the code, the tests, an ad hoc run, or an accepted decision.
The body state it was tried against is Embodiment's, at
`embodiment` `a5129f03aa4b024e33d332f917b9235afe97959c`.

## What it is

A body has an internal condition: how full its reserve is, how intact it is,
how warm, how tired. If any of that is to reach whatever lives in the body,
something has to turn the body's numbers into signals. The transducer is a
small piece of apparatus that does this for four numbers, and it is built so
that the signals say nothing about what they measure.

It reads four quantities from a body state and returns four values between
zero and one, each under an identifier chosen by the caller. The identifiers
are arbitrary strings. The order in which the four quantities are assigned to
the four identifiers can be shuffled. A consumer of the output receives four
anonymous numbers.

The module says what it leaves out: "It does not assign labels, valence, or
action meaning to the underlying body-state scalars."

Nothing in the Biopeia repositories calls it at the revisions examined. Its
opening line describes it as an "Opaque body-interoception transducer used by
the Physics3D apparatus."; no such apparatus exists in this repository. It is
a component without a consumer, and what follows describes what it would do
if called.

Embodiment's articulated body specification reserves four receptor
identifiers that it names interoceptive
(`embodiment:src/embodiment/physics3d/articulated_spec.py`). No code passes
them to this transducer.

## What it reads

Five fields of a body state: the energy reserve and its maximum, structural
integrity, temperature and fatigue
(`lab:src/lab/apparatus/interoception.py::SomaticInteroceptionInput`). Lab
declares the shape it needs and imports nothing from Embodiment. Any object
with those five attributes is accepted; the tests use a stand-in of their
own. Confirmed by running the module that Embodiment's body state has the
five attributes and can be sampled.

It reads and does not write: sampling leaves the state unchanged
(`test_interoception_permutation_changes_slots_not_source_state`).

## What it returns

Four values in a fixed source order:

1. the reserve divided by its maximum;
2. structural integrity;
3. temperature;
4. fatigue;

each limited to the range from zero to one
(`test_interoception_projects_four_bounded_opaque_values`). They are then
handed out under the caller's four identifiers, in the order given by a
permutation: slot by slot, which source goes where
(`test_interoception_permutation_changes_slots_not_source_state`). Anything
that is not a permutation of the four sources is refused
(`test_interoception_rejects_non_permutations`). Four distinct identifiers
are required; with none given, construction fails.

That is the whole transformation. There is no noise, no delay, no scaling
beyond the limit, no adaptation, and nothing that depends on an earlier
sample. Two samples of the same state are equal.

### In what sense the output is opaque

The values carry no label, and the identifiers are whatever the caller chose.
That is the extent of it. Without an explicit permutation the sources are
assigned in the fixed order above, so opacity toward a consumer rests on the
caller choosing identifiers and a permutation that the consumer does not
know. Whoever builds the transducer knows the mapping.

Whether a consumer could tell the four signals apart, or learn what they
track, is a question about that consumer. Nothing here examines it.

### Values outside the expected range

Confirmed by running the module:

- a temperature above one is reported as one. The limit hides by how much;
- a maximum reserve of zero does not fail: the divisor has a small floor;
- a not-a-number reserve, integrity or temperature is reported as **one**,
  the top of the range, not as a fault. For integrity and for the reserve
  that is the value of a body in perfect condition.

Embodiment's body state refuses integrity, temperature and fatigue outside
zero to one when it is validated, so the last case concerns states that
bypass that validation or stand-ins that are not Embodiment's.

## What it keeps

One thing: the permutation. A checkpoint of the transducer is the schema
version and the list of source positions, and nothing else. Its description
is "Persist only the slot permutation, never physiology labels."
(`test_interoception_checkpoint_round_trip_keeps_only_ordinal_mapping`).

The identifiers are not in the checkpoint. They are supplied again on
restoring, and nothing ties them to the ones used before. Confirmed by
running the module:

- restoring with four different identifiers succeeds;
- restoring with the same identifiers in another order succeeds and silently
  changes which source each identifier receives.

So the mapping from source to identifier survives a restore only if the
caller supplies the identifiers in the same order. The transducer holds no
body identity, no episode identity and no calibration, and reads no clock.

Two smaller points from the same run: identifiers that are not strings are
converted to strings, and source positions given as fractional numbers are
truncated to whole numbers before the permutation check.

## Beside the accepted decisions

The decisions below describe the target. They are set beside the code and no
conformance is ruled here.

[ADR-0094](../../technical/adr/ADR-0094-somatic-state-ownership-body-holds-organism-regulates-and-feels.md)
says: "Somatic state reaches Organism only through body somatic state →
interoceptive transduction → opaque Organism signal, calibrated per embodiment
episode." The transducer performs a step of the middle kind: body numbers in,
unlabelled bounded numbers out. It has no calibration and no notion of an
episode, and nothing connects its output to an Organism. The decision leaves
open "interoceptive noise/reliability, numeric calibration, or channel
implementation".

[ADR-0099](../../technical/adr/ADR-0099-modality-contract-library.md) places
transduction with Modality and assigns transducer state to an owner:
"body-local calibration and episode transducer state to Embodiment/episode".
Here a transducer lives in Lab, as apparatus, and its one piece of state, the
permutation, is created, held and checkpointed by Lab code. The repository
explains the placement as an extraction of an apparatus piece from a former
mixed adapter. Which domain is to own the permutation in the target is not
decided by this code.

The repository bounds its own claim: "it does not assign meanings to channels
or claim scientific validity".

## What this is not evidence of

The tests show that four numbers are limited, permuted and round-tripped as
described. They do not show that any organism senses its body, that the
signals are informative, or that hiding labels has any effect on what a
consumer learns. No experiment is described or authorised here.

## What supports this description

| Claim | Support |
|---|---|
| The four bounded values and their source order; the permutation; refusal of non-permutations; the state left unchanged; the checkpoint holding only the permutation | Code and tests in `lab:tests/unit/test_interoception.py`; the 18 unit tests of the repository passed when run for this document |
| Embodiment's body state can be sampled; out-of-range and not-a-number inputs; restoring with other or reordered identifiers; conversion of identifiers and positions | Code, and one ad hoc run of the module at that revision with Embodiment at the revision pinned in `lab:pyproject.toml` |
| No consumer in Biopeia | A search of the seven domain repositories at their main branches on the day of review |
| How somatic state should reach an Organism and who should own transducer state | Accepted decisions ADR-0094 and ADR-0099; statements of intent |
| Why the transducer is in Lab | `lab:MIGRATION.md`; a statement by the repository |

## Open questions

- Which component is to call the transducer, and what would receive its
  output.
- Whether the permutation is apparatus configuration owned by Lab or episode
  transducer state owned by Embodiment.
- Whether a checkpoint should bind the identifiers it was made with.
- Whether a not-a-number input should be reported as a fault.
