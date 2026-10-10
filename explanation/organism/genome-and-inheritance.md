# The genome, its expression and the germline record

Reviewed against `organism` at commit `0c2c543e71d335a45e6e07a791c20de1e58c6404`.
Everything below describes that revision. Statements are marked by what
supports them: the code, the tests, an ad hoc run, or neither. Searches of the
repository were made on 2026-10-10 at that revision.

## What it is

The Organism package contains a directory called `genetics`. Its own header
calls it "Genome v2: inherited predispositions, expression and germline".
Read by what it does, it is three things:

- a **genome**: an immutable table of 42 numbers, with a strict reader that
  refuses anything malformed, and two hashes;
- an **expression state**: five numbers derived from the genome that a
  regulator moves, between bounds the genome sets, in response to six signals
  it is handed;
- a **germline record**: a note of what those five numbers were at birth, and
  optional marks that shift them, with an optional rule for recording new
  marks.

What it is not matters as much. **No operation in the repository produces an
offspring.** There is no mutation, no recombination, no copying of a genome
from parent to child, and no decision to reproduce. The repository says so of
itself; its migration record describes this directory as "Copied genome and
inheritance mechanisms. This does not demonstrate endogenous
reproduction/evolution." The words mutation, recombination, inheritance and
evolvability appear here as names of fields and of one value type. They
describe data that a reproduction step would need. The step is absent.

A second absence is as important. **Nothing outside this directory reads a
gene value.** The genome can be loaded, validated, hashed and written to a
checkpoint payload. The cognition code that grows and prunes structure takes
its thresholds as arguments of its own, and no code in the repository passes
a genome value, or a value of the expression state, to it. This document
therefore describes a self-contained description of a constitution that is
not yet connected to the thing it would constitute.

## The genome

A genome (`organism:src/organism/genetics/genome.py::Genome`) carries a schema
version, an identifier, a statement of which kernel versions it is compatible
with, and six groups of genes:

| Group | Loci | What the values are named for |
|---|---|---|
| development | 5 | soft ceilings on nodes, edges and sense nodes; a growth sensitivity; a consolidation interval |
| plasticity | 9 | a learning rate and a structural plasticity, each as a range of four numbers; an eligibility decay |
| regulation | 7 | five gains, one per signal; a smoothing and a decay |
| sensorimotor | 5 | a baseline of spontaneous activity; three gains; a habituation |
| structure | 10 | a growth threshold and a pruning threshold, each as a range; a minimum support; a tentative lifetime |
| evolvability | 6 | five scales named for mutation, one per group above; a linkage named for recombination |

Four quantities are stored as a range of four numbers: a baseline, a minimum,
a maximum and an adaptation rate. The range is what lets the expression state
move: the baseline is where it starts, the minimum and maximum are how far it
may go, the adaptation rate is how fast.

The genome has no parents, no generation and no list of free-form loci. The
tests check that those fields of an earlier format are gone
(`test_v2_payload_loads_without_retired_genome_fields`). It also has no genes
for a body. A type for them remains only to refuse construction, with a
message ending "physical health belong to the embodiment"
(`test_motor_genes_constructor_fails_fast`, `test_genome_v2_has_no_motor_genes`).

### What a genome must satisfy to be read

The reader (`organism:src/organism/genetics/genome.py::GenomeCodec`) accepts
a plain mapping and refuses it unless:

- its keys are exactly the nine expected, and each group's keys are exactly
  those of the group (`test_load_rejects_missing_top_level_key`,
  `test_load_rejects_unknown_top_level_key`);
- the schema version is 2 (`test_load_rejects_removed_v1_schema`);
- the identifier begins with `genome_` and uses a small set of characters
  (`test_load_rejects_malformed_genome_id`);
- the compatibility statement parses as comparisons against version numbers
  (`test_load_rejects_malformed_kernel_compatibility`);
- every number has the right type, is finite and lies inside the bounds a
  separate schema gives for its locus
  (`test_load_rejects_invalid_development_fields`,
  `test_load_rejects_wrong_json_type_as_genome_error`);
- each range has its baseline between its minimum and maximum;
- the ceiling on sense nodes does not exceed the ceiling on nodes
  (`test_load_rejects_sensory_budget_above_node_budget`).

A second check, made when a genome is about to be used, compares it with the
running kernel: the running version must satisfy the compatibility statement,
and the genome's ceilings must not exceed the hard limits of the kernel
(`test_validate_rejects_kernel_version_outside_declared_range`,
`test_validate_rejects_kernel_limit_overflow`).

These checks belong to the reader. The genome type itself checks nothing: in
an ad hoc run, a copy of a valid genome with an identifier containing spaces
was constructed without complaint and produced a hash.

### The schema is not part of the genome

The bounds come from a closed catalogue of the 42 loci
(`organism:src/organism/genetics/schema.py::DEFAULT_GENOME_SCHEMA`). For each
locus it gives a type, a minimum and a maximum, and several values named for
inheritance: a mutation probability, a mutation scale, a mutation mode, a
flag `inheritable`, a flag `regulable`, and a recombination group. The module
states the relation: "The schema describes which values may vary genetically.
It is not part of an individual genotype and therefore never changes an
organism's genotype hash."

Of these, the bounds are used by the reader and `regulable` is used by the
germline record. A search for the mutation probability, scale and mode, for
`inheritable`, and for the function that lists recombination groups found no
reader of any of them outside the schema module itself. In the catalogue every
locus is marked inheritable and five are marked regulable: the four baselines
of the ranges and the baseline of spontaneous activity.

### Two hashes

A genome answers with two SHA-256 values.

The **genome hash** covers everything: identifier, compatibility statement
and genes. The **genotype hash** covers the schema version and the genes
only. The code describes the identifier as "Lineage/materialization identity,
distinct from genotype_hash." Two genomes built from the packaged seed under
different identifiers had different genome hashes and the same genotype hash
(ad hoc run). The genome hash does not depend on the order of keys in the
input and changes when a gene changes
(`test_hash_is_key_order_independent_and_changes_with_content`).

### Where a genome comes from

One genome is packaged with the code, as a data file. Two functions read it:
one returns it as it is, after the kernel check
(`organism:src/organism/cognition/birth.py::load_base_genome`, covered by
`test_base_genome_is_semantics_free_and_within_kernel_limits`); the other
returns it under an identifier supplied by the caller
(`organism:src/organism/genetics/factory.py::create_standard_genome`). The
identifier is given, never generated. The first is called by one
other function of the same module, which pairs it with an empty graph; that
function and the first are otherwise called only by tests. Nothing calls the
second.

So at this revision every genome that can be obtained without writing one by
hand has the same genes.

## Expression: five numbers that move

The expression state
(`organism:src/organism/genetics/expression.py::GeneExpressionState`) holds
an effective learning rate, an effective structural plasticity, an effective
growth threshold, an effective pruning threshold and an exploration drive. It
also keeps the five values it started with, which it calls the birth
expression, and a count of updates.

At creation each value is the genome's baseline, limited to the genome's own
range. A regulator
(`organism:src/organism/genetics/expression.py::ExpressionRegulator`) then
produces a new state from an old one and six signals, each a number between 0
and 1: uncertainty, novelty, prediction error, controllability loss,
embodiment mismatch and resource pressure. The regulator does not compute the
signals. A caller supplies them, and no caller exists in the repository.

The computation, read from the code:

```text
mismatch = sum of (gain x signal) over the first five signals, limited to 0..1
pressure = the larger of mismatch and resource pressure

learning rate, structural plasticity:
    target = birth + (maximum - birth) x mismatch
growth threshold, pruning threshold:
    target = birth - (birth - minimum) x mismatch
each of the four moves toward its target by at most
    adaptation rate x pressure

learning rate only, afterwards:
    value = value + decay x (birth - value)

exploration drive:
    target = birth + three gains x (uncertainty, prediction error,
             embodiment mismatch), less a habituation term that vanishes
             when any of those three signals is 1
    value  = value + smoothing x (target - value) + decay x (birth - value)
```

In words: when the signals rise, learning and structural plasticity rise
toward their maxima, the two thresholds fall toward their minima, and the
exploration drive rises. The names of the signals are the names of the
arguments. Nothing in this package establishes that a number passed as
`uncertainty` measures uncertainty.

An update can be frozen, in which case the state is returned unchanged
(ad hoc run).

### What the numbers did in a run

With the packaged genome, and with no test kept for any of this:

| Sequence of updates | Learning rate | Structural plasticity | Growth threshold | Pruning threshold | Exploration |
|---|---|---|---|---|---|
| at creation | 0.02 | 0.5 | 0.18 | 0.01 | 0.1 |
| 200 with the first five signals at 1 | 0.0788 | 1.0 | 0.02 | 0.0 | 0.85 |
| then 2000 with every signal at 0 | 0.02 | 1.0 | 0.02 | 0.0 | 0.0917 |
| instead, then 200 with only resource pressure at 1 | 0.02 | 0.5 | 0.18 | 0.01 | 0.0917 |

Three things follow from the table and the formula.

- **Three of the five do not come back by themselves.** The step is
  proportional to the pressure. With every signal at zero the step is zero,
  so structural plasticity and the two thresholds stay where the last
  pressure left them. The learning rate and the exploration drive have a
  separate decay term and return. A comment in the code says that
  "regulation_decay supplies the slow return toward the constitutive"
  baseline; the code applies that decay to two of the five.
- **Resource pressure moves nothing by itself.** It only enlarges the step.
  Alone it sets every target to the birth value, which is how the third row
  returns to the first.
- **The exploration drive rests below its birth value** when the signals are
  zero, because the habituation term is then at its largest.

### What the clock is

The module opens with the sentence "Evidence observed through tick t may
update this state only for tick t+1." The regulator takes no tick. It counts
calls. Whether a call corresponds to a causal tick, and whether the signals it
is given were observed before that tick, is for a caller to arrange, and
there is none. The sentence is a statement of intent about use; nothing in
this package enforces or tests it.

## The germline record

The germline record
(`organism:src/organism/genetics/germline.py::GermlineState`) is created from
a genome and, optionally, from marks. A mark names one locus and carries a
shift, a strength between 0 and 1, and a number of generations left. It may
target only a regulable locus.

The record keeps its own birth expression, which is a different table from the
one in the expression state: all 42 loci, with the marked ones shifted by
shift times strength. When an expression state is created with a germline
record, it starts from those shifted values instead of the genome's baselines
(ad hoc run: a mark of +0.01 on the learning-rate baseline gave an effective
learning rate of 0.03 at creation instead of 0.02).

The two tables limit a value differently. The germline record limits it to
the bounds of the schema; the expression state limits it again to the range
of the genome. A mark of +0.4 on the same locus gave 0.42 in the first and
0.08 in the second (ad hoc run).

### Marks an individual acquires

The record can also write marks of its own. The class that configures this
describes itself as "Optional transgenerational extension, outside the
baseline genotype." It is off in three places at once: a flag on the record,
and two flags on a protocol value. With any of the three off, a request to
capture returns nothing and clears its counters.

With all three on, the record is handed the current expression values. For
each regulable locus whose current value differs from its birth value by at
least a threshold (0.02 by default), it increments a counter. When the
counter reaches 64 the record stores a mark holding the difference. A call in
which the difference falls below the threshold resets the counter. At most
eight marks are kept by default. In an ad hoc run the mark appeared on the
64th consecutive call and not on the 63rd; the constant is named for ticks,
and what it counts is calls.

A mark the individual acquired does not change that individual's own
expression. The code says so: "Acquired marks are records for possible
transmission, not an extra control signal for the living individual." The
run confirmed it: after the capture, the effective value was still the
genome's.

A mark has a method that weakens it and uses up one generation; with the
default weakening of 0.2 a mark with three generations left survived two
applications and was gone at the third (ad hoc run).

### The package that nothing fills

One value type is named for inheritance
(`organism:src/organism/genetics/germline.py::InheritancePackage`). It holds a
genome, marks, a non-empty list of distinct parent identifiers and a
generation number of at least 1, and it checks those shapes. A search for
its name, for the capture method, and for the weakening method found no
caller of any of them in source or tests. Nothing builds a package from a
parent, nothing weakens a mark between generations, and nothing gives a
package to a new Organism.

## What is and is not heritable

Because no operation performs inheritance, this section can only report what
the data structures are shaped to carry.

| Item | Position in the code |
|---|---|
| The 42 genes | A package would carry a whole genome. Every locus is flagged inheritable; nothing reads the flag |
| Marks received from a parent | Carried in the package; shift the birth expression of the recipient |
| Marks acquired in a lifetime | Stored for transmission only under the protocol that is off by default |
| The five effective values and their update count | Not in the package |
| Body properties | Not in the genome at all; the type for them refuses construction |
| Anything learned: graph, weights, experience records, outcome history | Not referred to by this directory |

## The self-check that names things that are not there

One module (`organism:src/organism/genetics/bindings.py`) lists, for every
locus, a name for the runtime consumer of that gene, a name for an observable
projection, and a name for a test said to show the gene has an effect. A
function checks that each of the 42 loci matches "exactly one rule or Genome
v2 fails its constitutional self-check".

The check passes (ad hoc run: 42 bindings, 22 distinct consumer names, 18
distinct test names). What it checks is that a table of strings is complete.
None of the 18 test names is defined in the repository, the consumer names
are not identifiers of anything in the code, and the function itself has no
caller. Six of the consumer names are for mutation and recombination, which
do not exist here. The migration record lists two test modules for this
directory as deferred and not copied; the directory reserved for its tests
holds no test.

## Randomness and time

Because a later decision turns on it, every source of randomness in this
directory was looked for. There is none. No module in `genetics` imports a
random-number generator, an operating-system entropy source, a clock or an
identifier generator, and none calls the built-in hash whose value varies
between processes. Genome identifiers are supplied by the caller. Every
function here returns the same output for the same input.

That is a statement about what exists. A mutation or recombination step would
need random draws, and since there is no such step there is nothing to say
about where its draws would come from. Elsewhere in the repository, outside
this directory, one cognition function receives a random-number generator as
an argument; nothing in source constructs one.

No host time is read. The only durations are the two counters of calls
described above.

## Across a restart

Each of the three parts can be written to plain data and read back
(`organism:src/organism/genetics/checkpoint.py`). The genome payload carries
its hashes and restore checks them; expression restore checks range, and
germline restore checks whether marks target regulable loci. Tests cover the
current cognition and genetics genome-checkpoint readers, including rejection
of missing, invalid and mismatched `genotype_hash` values. This is checkpoint
codec evidence, not evidence that these records are included in the composed
portable Organism checkpoint.

Some things the germline reader accepts, each seen in the same run:

- an entry in a list of marks that is not a mapping is skipped without error;
- the birth expression in the payload replaces the one derived from the
  genome and the marks, without being compared with it: a payload saying 0.4
  where the genome and mark give 0.03 was accepted, and the record then
  reported both numbers, one from each table;
- acquired marks are accepted in a record whose capture flag is off.

The expression reader likewise accepts a birth value that differs from the
genome's baseline, as long as it lies in the range.

The cognition reader
(`organism:src/organism/cognition/checkpoint.py::restore_genome_checkpoint`)
and the genetics reader now both require and validate `genotype_hash`. The
tests `test_exported_payload_carries_both_required_genome_hashes`,
`test_cognition_and_genetics_codecs_both_reject_invalid_genotype_hash`,
`test_cognition_and_genetics_codecs_both_reject_mismatched_genotype_hash` and
`test_cognition_and_genetics_codecs_both_reject_missing_genotype_hash` exercise
that parity. The broader genetics expression and germline behaviors described
above are not all covered by these tests.

As with the [executive outcome ledger](executive-outcome-ledger.md), what
matters most is what these payloads are not part of. A search of the
composed cognitive payload and of the checkpoint envelope, described under
[identity and the checkpoint envelope](identity-and-checkpoint.md), found no
reference to a genome, an expression state or a germline record. No
checkpoint in the repository carries them.

## At each lifecycle boundary

| Boundary | What happens | Support |
|---|---|---|
| Birth | A genome is read from the packaged seed; expression and germline records are derived from it. Nothing in source performs a birth | Code and test for the seed; ad hoc run for the rest |
| Checkpoint | Each part can be exported; no checkpoint includes any of them | Code and ad hoc run; search of the repository |
| Restart | Each part can be rebuilt from its export, with the leniencies listed above | Code and ad hoc run |
| Re-embodiment | Nothing here reacts. One signal is named for embodiment mismatch and one gene is its gain; a caller would have to supply the signal | Code; no operation performs a re-embodiment |
| Reproduction | A value type is shaped to carry a genome and marks to an offspring. No operation fills it | Code; search of the repository |

## Beside the decisions

Four accepted decisions speak to this area. Each defines the target
architecture and says of itself that it does not assert that current code
complies. They are set beside the code here without a ruling on conformance.

[ADR-0082](../../technical/adr/ADR-0082-canonical-reproduction-is-endogenous-to-life.md)
asks to "Keep reproduction mechanism, endogenous reproduction, population
dynamics, selection and evolution distinct." Of those five, this directory
holds data structures for the first and nothing for the others.

[ADR-0087](../../technical/adr/ADR-0087-organism-originates-ordinary-reproduction.md)
makes the Organism the origin of ordinary reproduction: "internal
physiological capacity/state originates the transition". No readiness, no
transition and no trigger exist in this directory, so the code neither
places that origin in the Organism nor places it elsewhere.

[ADR-0094](../../technical/adr/ADR-0094-somatic-state-ownership-body-holds-organism-regulates-and-feels.md)
gives the Organism the allocation between maintenance and reproduction and
adds: "The allocation rule may be heritable under the accepted germline
rules." No locus among the 42 is named for such an allocation, and no code
computes one.

[ADR-0108](../../technical/adr/ADR-0108-reproduction-and-causal-entropy.md)
requires that "OS entropy contributing to causal identity/state must be
removed, explicitly injected or placed under controlled causal RNG before
conformance." This directory draws on no entropy at all, as reported above.
The reproduction path that decision speaks of was not copied into this
repository, so the question it raises cannot be examined here.

[ADR-0081](../../technical/adr/ADR-0081-the-canonical-organism-is-longitudinal.md)
lists "permitted inherited/epigenetic state" among what continuity of an
Organism preserves, and
[ADR-0103](../../technical/adr/ADR-0103-portable-organism-state.md) asks a
portable checkpoint to carry what is needed to restore private state. The
three payloads exist; no checkpoint composes them.

[ADR-0092](../../technical/adr/ADR-0092-organism-owns-the-meaning-of-its-private-longitudinal-state.md)
places this state under the Organism's authority. The directory imports
nothing from another domain, which is consistent with that and does not
establish it.

## What supports this description

| Claim | Support |
|---|---|
| Shape of the genome, what the reader refuses, the kernel check, key-order independence of the genome hash, absence of body genes, content of the packaged seed | Code and tests in `organism:tests/source_unit/cognition/test_genome.py`, `organism:tests/source_unit/cognition/test_birth.py` and `organism:tests/source_unit/actuation/test_genome_motor_genes.py` |
| Round trip and refusal of a tampered genome payload | Code and tests in `organism:tests/source_unit/cognition/test_checkpoint.py`, which exercise the reader in the cognition package, not the one in this directory |
| The regulator's computation and the table of values; frozen updates; the germline record, marks, capture after 64 calls, weakening of marks; the binding counts; the three round trips and what the readers accept; the two hashes under two identifiers; the difference between the two genome readers | Code, and ad hoc runs of the modules at that revision. No test in the repository covers `expression.py`, `germline.py`, `bindings.py`, `schema.py` or `checkpoint.py` of this directory |
| No mutation, recombination or reproduction operation; no reader of a gene value or of the expression state outside the directory; no caller of the package type, the capture, the weakening, the binding check or the identifier factory; no reader of the mutation fields of the schema; none of the 18 test names defined; no checkpoint carrying genetic state; no source of randomness or host time | Searches of `src` and `tests` at that revision, made on 2026-10-10, for the names concerned and for imports of random, entropy, clock and identifier modules |
| That the directory does not demonstrate endogenous reproduction or evolution | The repository's own migration record |
| What reproduction, heritable allocation and causal entropy must be | Accepted decisions ADR-0082, ADR-0087, ADR-0094, ADR-0108; statements of intent |

No genome from a run of an Organism was examined, because nothing runs one at
this revision. That these genes shape an Organism's development, or that the
regulator's response is useful, is not supported by anything reviewed here.

## Open questions

- Which component computes the six signals, and from what.
- Which component reads the five effective values, and whether the gene
  values that are not regulated are meant to be read from the genome or from
  the kernel limits that currently hold similar numbers.
- Whether three of the five effective values are meant to stay displaced
  when all signals are zero.
- Whether a restored germline record should be refused when its birth
  expression disagrees with its genome and marks.
- Which of the two genome readers is the intended one.
