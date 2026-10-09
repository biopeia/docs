# Modality: what was decided, and what the repository holds today

Reviewed against `modality` at commit `9bd1b77c9eabc271969109cfab52394dc5b52012`.
Other repositories were read at the head of their main branches on 2026-10-09:
`world@c162b67e698de9b47450264402677b0165e6e20e`,
`organism@6543188ff302a5f2dc8002c0086252d6061e5310`,
`embodiment@a5129f03aa4b024e33d332f917b9235afe97959c`,
`environment@f97ec22272b6be1e6742770e37cd370e7d96d6bc`,
`observation@397c0b4691b5e460e6ebc3914f9820ff434a3661` and
`lab@4d5ff706b8329ddf25e1852ad53cbde5285d2851`.

## The short answer

Something has to stand between a phenomenon in the environment or the body
and the number an organism receives. Turning one into the other is called
transduction, and Modality is the name Biopeia gives to the place where the
rules of transduction are meant to live.

At the commit reviewed, **that place is empty**. The `modality` package
exports nothing, contains no function, class or constant, and is imported by
no other Biopeia repository. This is deliberate and recorded: the repository
removed the operators it had, on the day it received them, because they had
been copied from the historical system without a reason of their own.

So this document describes a decided role with no implementation. It keeps
three things apart: what the accepted decisions say Modality is (intent),
what the repository contains (code, confirmed by running it), and what stands
in for transduction where a signal reaches an organism today (a test
fixture in another repository).

## What Modality is decided to be

These are accepted decisions. They state intent, not behaviour.

[ADR-0095](../../technical/adr/ADR-0095-surviving-semantic-authorities.md)
names the authorities: "Ratified primary semantic authorities: `ORGANISM`,
`EMBODIMENT`, `ENVIRONMENT`, `WORLD`." Modality is not among them.

[ADR-0099](../../technical/adr/ADR-0099-modality-contract-library.md) says
what it is instead: "Modality is a `CONTRACT / LIBRARY / IMPLEMENTATION
CAPABILITY`, not an independent semantic authority on current evidence."
Its subject is narrow: "It defines transduction between
physical/environmental phenomena and opaque signals/effectors, not Organism
interpretation." Two things follow from that sentence. The output is opaque:
what a signal means is for the Organism to work out, not for Modality to
declare. And the decision covers both directions, signals coming in and
effectors going out.

The same decision settles who owns any state a transducer needs. Modality
"need not be stateless", but it owns none of it: the state is assigned
"body-local calibration and episode transducer state to Embodiment/episode,
learned perceptual adaptation to Organism, medium parameters to Environment,
and pure scratch state to non-authoritative implementation". The decision
leaves one door open: "Reconsider authority only if future evidence
identifies persistent semantic state without an existing owner."

[ADR-0110](../../technical/adr/ADR-0110-repository-consequence-and-dependency-direction.md)
repeats the role in one clause, "Modality supplies transduction without
interpretation ownership", and counts Modality as a candidate repository for
a reusable contract, not as an authority.

The approved design
[Biopeia Physical-Step and Causal-Commit Integration v1](../../technical/design/runtime/biopeia-physical-step-integration-v1.md),
in its section "Modality repository disposition", decides the packaging
question. Modality stays a "provisional independent repository" during the
migration, and the design gives the reason: "its reusable transduction
contracts are a low-cost seam while stateful implementations are still being
discovered". It restates the ownership rule as four labels
(`ORGANISM_OWNED`, `EMBODIMENT_OWNED`, `ENVIRONMENT_OWNED`,
`IMPLEMENTATION_EPHEMERAL`) and adds: "There is no `MODALITY_OWNED` category
without a new explicit architecture decision." It also names when to think
again: when the migration is largely complete, when independent versioning
proves unnecessary, or when persistent coupling shows that the repository
adds no real boundary.
[ADR-0073](../../technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md),
item 9, records the same decision.

ADR-0099 says of itself that it "Defines TARGET only; no CURRENT compliance".
Nothing above is a claim about code.

## What the repository contains

Read from the tree at the commit reviewed, and confirmed by importing the
package extracted at that commit.

The source tree is one file, `modality:src/modality/__init__.py`. It holds a
docstring and one statement, which sets the package's list of exported names
to the empty tuple. The docstring describes the package as a namespace for
future contracts and states: "No concrete operator, numeric interpretation,
or modality catalogue is currently ratified for TARGET." Importing the
package showed no public name, no submodule, and no attribute named after
any of the removed operators.

There is one test,
`test_package_exposes_no_unratified_concrete_operator_or_catalogue` in
`modality:tests/test_unratified_surface.py`. It asserts that the list of
exported names is empty. It passed when run against the extracted tree. It
protects the absence of an interface; it exercises no behaviour, because
there is none.

The repository's continuous integration installs the package, runs that
test and builds a distribution. The package declares no dependency.

The rest is prose:

- `README.md` describes the repository as "reserved for reusable,
  non-authoritative contracts for opaque signal/effect transduction" and
  states a rule for everyone else: "callers must preserve an opaque signal
  unchanged rather than assign it an inherited numeric meaning". It also
  says what a future operator would need before it is admitted: "A future
  operator requires a target consumer and an explicit contract for
  input/output semantics, state ownership, initialization, update rule,
  range, saturation, time basis, determinism, and configuration."
- `MIGRATION.md` records where the removed code came from, an inventory of
  the historical sensory and host-reading code with a proposed disposition
  for each file (none of it copied), and the ownership rule above.
- `AGENTS.md` is guidance for agents. Its statement of what the repository
  owns was not updated when the code was removed; see "Statements that no
  longer match" below.

The rule that callers preserve a signal unchanged is a sentence in a README
and a docstring. No code in this repository can enforce it on a caller, and
none tries.

## What was removed, when, and why

All of this happened on one day, 2026-10-09, read from the repository's
history.

The first extraction (commit `1c4e560`) copied two modules unchanged from the
historical system's sensory package. The migration record gives the blob
identifiers that show the copies were exact.

One module offered a single function that applied one of five named
operations to a sequence of numbers: pass the first value through, take its
difference from the previous value, blend it into a decaying running value,
compare it with a threshold, or average the inputs. The result was multiplied
by a gain and limited to a fixed range. The function kept nothing between
calls: the previous value and the running value were handed in by the caller
and handed back, so the caller held them. The other module defined a
descriptor for a family of signals (which operations it allowed, how many
inputs, a capacity and a cost) and a default catalogue of four such
descriptors with abstract names.

Commit `709996a`, merged as pull request #7 of `biopeia/modality`, deleted
both modules and their tests, emptied the package's exports, and added the
test described above. The reason is recorded in `MIGRATION.md`. For the
operators: "the Architecture Owner later rejected inherited operators absent
independent TARGET justification". For the catalogue: "the descriptor/default
catalogue has no TARGET consumer or independent justification". The record
is explicit that the earlier copy carries no weight now: "the initial
copy-first record is retained as provenance, not current authorization". On
the state question it adds: "The removed source-derived transduction
functions did not own persistent state; this historical fact does not
authorize those operators in TARGET."

The removed code is described here only so that the history is legible. It is
not part of Biopeia at the commit reviewed and nothing in this document
should be read as a description of how transduction works.

## Who uses Modality today

Nobody. A search of the source and test trees of the other six repositories
at the commits listed at the top found no import of `modality` and no
dependency on it in any package metadata. The word appears in comments,
docstrings, migration records and, in one World test, as a label.

There was one user. World's first integration fixture called the removed
pass-through operation. World's migration record describes the change after
the removal: "No integration test imports `modality` any longer, so its pin
was removed from the `integration` extra."

## What this means for Environment → Modality → Organism

The intended path is that a phenomenon owned by Environment is transduced
into an opaque signal and that signal reaches the Organism. At the commits
reviewed, the code that comes closest is
`world:tests/integration/test_first_biopeia_causal_tick.py`, a test fixture.
What it does at this point of the path is three statements:

1. a variable called the environmental signal is set to the constant `0.5`.
   The fixture's comment says: "Explicit deterministic fixture input; no
   Environment law is under test." No Environment code produces the value;
2. a second variable, the opaque signal, is assigned the first, unchanged;
3. that value is given to Organism's cognitive transition as the input of
   one sense node of a two-node graph built by the fixture.

So, of the three links, only the last runs production code. The first is a
constant and the second is an assignment. The assignment is consistent with
the README's rule that callers preserve an opaque signal unchanged, and is
the only place where that rule is acted on.

The test `test_first_biopeia_causal_ticks_are_deterministic` asserts, for
each tick, that the recorded environmental signal equals the recorded
transduced signal. Given the assignment, that assertion cannot fail; it
records the pass-through and tests nothing about it. The same test asserts
that the graph's readout differs from the signal, which does exercise
Organism's code. The field that records the value is still named
`transduced_signal`, although nothing transduces it.

Both tests of that fixture passed in an ad hoc run with World at the commit
above and Organism, Embodiment and Observation at the revisions World pins,
with no Modality package present.

On the receiving side, Organism's cognitive transition describes its inputs
as "opaque modality signals". The function takes a mapping from node name to
number; it neither imports nor requires anything from Modality. The phrase
names a role for the input, not a dependency.

The other integration fixture, the
[physical causal step](../world/physical-step.md), feeds no sensory input to
Organism (a search of the fixture for a cognitive transition, a sense node,
a signal or a receptor found none), and its outbound path from command to effector does not pass through
Modality either. ADR-0099 includes effectors in what Modality defines; the
fixture's comment says Modality's contract is "sensory transduction only, not
motor-command adaptation". The decision and the comment are set side by side
here without ruling between them. At the commit reviewed the contract the
comment refers to does not exist in either direction.

### Transduction that exists elsewhere

A search of the seven repositories for the words transduction and modality
found one piece of code that turns body quantities into anonymous numbers,
and it is not in Modality. Code doing similar work under other names would
not have been found by that search. Lab's
`lab:src/lab/apparatus/interoception.py::OpaqueBodyInteroception` is
documented as: "Transduce selected body-state scalars into anonymous receptor
slots." It derives four values from a body's state, limits each to the range
from zero to one, and returns them under caller-supplied identifiers in an
order set by a permutation. It can save and restore that permutation
("Persist only the slot permutation, never physiology labels."). Within Lab's
source it is used only by its own unit tests.

This is mentioned because it is the only code found that calls itself a
transducer. It is Lab apparatus, it holds a small piece of
transducer state, and ADR-0099 assigns episode transducer state to
Embodiment. Whether that is a conflict is for the owners; it is recorded as a
finding and not judged here.

## State and time

At the commit reviewed Modality has no state: nothing is created, kept,
saved or restored, and no clock is read or advanced. The questions a
transducer raises are answered only by decision:

- whose state it is, by ADR-0099 and the four labels above;
- that a persistent state owned by Modality is not allowed without a new
  decision;
- that an operator's time basis must be stated before it is admitted, by the
  README's list of what a future operator requires.

One World unit test registers an owner labelled `modality` that writes a
checkpoint as a step participant. The label is an arbitrary string in a test
of World's roster mechanics; no Modality code is involved. It is noted
because a reader searching for Modality state will find it.

## Statements that no longer match

Found while tracing the above. Recorded as findings; nothing was changed.

- `modality:AGENTS.md` says the repository owns "bounded sensory transduction
  and modality capability contracts" in its current extracted slice, and
  calls the repository a copy-first extraction. The code it describes was
  removed and the commit that removed it did not touch this file.
- The reason given by ADR-0073 and by the approved design for keeping the
  repository separate is its reusable transduction contracts. At the commit
  reviewed the repository contains none. The decision is not thereby wrong:
  a namespace reserved for future contracts may be what the owner wants.
  But the stated reason describes code that is no longer there, and the
  design's own conditions for reconsidering the repository are not evaluated
  anywhere.
- `world`'s physical step fixture describes Modality's "current target
  contract", and `organism:MIGRATION.md` describes Modality as a repository
  "whose extracted v1 API is sensory transduction only". Neither exists now.
  `environment:MIGRATION.md` likewise lists transduction among the stages of
  World's first integration test.

## What supports this description

| Claim | Support |
|---|---|
| The role of Modality, the assignment of transducer state, the provisional repository and its review conditions | Accepted decisions ADR-0095, ADR-0099, ADR-0110, ADR-0073 and the approved physical-step design; statements of intent, not results |
| The package exports nothing and has no submodule | Code; the test `test_package_exposes_no_unratified_concrete_operator_or_catalogue`; an ad hoc import of the package extracted at the commit reviewed |
| What was removed, when and why | The repository's history (`1c4e560`, `709996a`, pull request #7) and its `MIGRATION.md` |
| No repository imports or depends on Modality | A search of the source, test and packaging files of the six other repositories at the commits listed; World's migration record |
| The signal in World's fixture is a constant passed through unchanged to Organism | Code of the fixture, read in full; an ad hoc run of its two tests without Modality installed |
| That the equality assertion cannot fail | Reading of the fixture: the second value is assigned from the first |
| Lab's interoception transducer, and that it is the only one found | Code of the module, read in full; not run. A search by the words transduction and modality, which would miss code named otherwise |
| That no transduction contract exists in either direction | Absence in the code at the commit reviewed; a negative result of reading and searching, not of a test |

Not verified: whether World's integration job ran in continuous integration
at World's current head, since that job runs only where credentials are
configured. The historical sensory code listed in `modality:MIGRATION.md` was
not read; that inventory is the repository's own account.
