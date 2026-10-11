# Modality: a narrow transduction contract, not a sensory system

Reviewed against `modality` at `79b779152d4bff2ab4191dc6601c8f1640e4cae3`,
`world` at `95f5064c6b06bd66bb58a72110b066afe4ca70b0`,
`organism` at `ba0011797a6a3b4d48c7731651e50560c4043f18`,
`embodiment` at `597cc4a09f4a5c94095b17ad0f2ba510df6d02c3`,
`environment` at `caa885a11ec0170717bb4b71d271ab171807197e`,
`observation` at `6aac3c76684834722440f53c9d8604ac4c16b138`, and
`lab` at `29e25d85e796d96a3f2e830fd870a2f74e8e2266`.

## The short answer

Modality is a capability repository for transduction, not a semantic
authority. The accepted architecture says it may map phenomena into opaque
signals without deciding what those signals mean. Persistent state, if a
future transducer needs any, remains owned by the relevant authority rather
than by Modality ([ADR-0099](../../technical/adr/ADR-0099-modality-contract-library.md),
[ADR-0110](../../technical/adr/ADR-0110-repository-consequence-and-dependency-direction.md)).

The repository is no longer empty. It contains one explicitly narrow,
stateless identity mapping for a dimensionless scalar field in `[0, 1]`.
That mapping is used by a World integration fixture to carry an Environment
sample through an Embodiment receptor into an Organism cognitive transition.
This is a tested slice, not a general sensory system, interpretation
mechanism, learning result, or production-connected path.

## What is decided

[ADR-0095](../../technical/adr/ADR-0095-surviving-semantic-authorities.md)
names Organism, Embodiment, Environment and World as primary semantic
authorities; Modality is not one of them. [ADR-0099](../../technical/adr/ADR-0099-modality-contract-library.md)
places Modality among contracts, libraries and implementation capabilities.
It may define transduction between phenomena and opaque signals/effectors,
but not Organism interpretation. It assigns any persistent state to its
existing owner (for example, body-local calibration to Embodiment and learned
perceptual adaptation to Organism), rather than creating a Modality-owned
semantic state category. [ADR-0073](../../technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md)
and [ADR-0110](../../technical/adr/ADR-0110-repository-consequence-and-dependency-direction.md)
retain this boundary. These are architectural decisions, not evidence that a
complete transduction path is implemented.

## The contract in source

`modality:src/modality/scalar_field.py` defines
`DimensionlessScalarFieldIdentityV1`. It declares contract identifier
`biopeia.modality.dimensionless-scalar-field-identity`, revision 1,
quantity kind `dimensionless_scalar_field`, unit `1`, and inclusive range
`[0, 1]`. `transduce` accepts finite numeric values in that range, rejects
booleans and invalid/out-of-range values, and returns the accepted number as
a float. It rejects rather than clips. The class carries no persistent
state, does not assign semantic meaning, and transports no Environment,
Embodiment, World or Organism identities/provenance. The package exports
this contract and its error type.

The tests
`test_first_scalar_field_transduction_is_explicit_identity` and
`test_first_scalar_field_transduction_rejects_invalid_values` check the
declared identity and rejection cases. They test this bounded mapping only;
they do not test perception, interpretation or learning.

## The World fixture

World's
`world:tests/integration/sensing/test_environment_to_organism_scalar_field.py`
is a hand-assembled integration fixture. It samples an
`IdentifiedFiniteScalarField` at the point projected from an
`EmbodimentReceptor`, applies the Modality identity mapping, constructs an
opaque signal with provenance, and calls
`advance_cognition_from_sense_signals` on a one-node Organism graph. The
fixture invokes World's physical-step coordinator with test-supplied
projection, solver, adoption and checkpoint ports. It asserts that the
resulting World cut commits and that the sample reaches the cognitive frame.

There is an important boundary: the cognitive transition is kept in the
fixture's `pending` values. The checkpoint-writing port serializes the
initial cognition state, not the computed transition candidate. The test
therefore demonstrates a signal-delivery/cognitive-computation slice within a
committed fixture step; it does not demonstrate adoption of that cognitive
candidate into the committed Organism continuation. The solver and adapters
are supplied by the fixture, not wired production components. The companion
stale-receptor test checks rejection before a next committed cut.

No evidence here establishes that the Organism learned what the value means,
that it selected an action because of it, or that a production runtime calls
this chain. The distinction between a numeric signal and its meaning remains
with the receiving Organism architecture.

## What remains absent

- A general operator catalogue or a general sensory-transduction framework.
- Persistent Modality-owned state.
- A production caller connecting Environment, Embodiment, Modality and
  Organism.
- Adoption of the cognitive candidate from the World sensing fixture into a
  committed Organism continuation.
- Evidence of semantic interpretation, adaptation, or scientific learning.
- A production path for motor-effect transduction.

The identity operation is deliberately narrow. It does not authorize the
historical operators or catalogue recorded in `modality:MIGRATION.md`, and it
does not imply that the migration's future-contract conditions have been
met. The approved physical-step design keeps Modality as a provisional
independent repository while its boundary remains useful; that repository
decision is separate from implementation maturity.

## Evidence boundary

| Claim | Support and limit |
|---|---|
| Modality is not a semantic authority and does not own interpretation | Accepted ADRs #0095, #0099, #0110 and #0073; decision evidence, not runtime behaviour |
| The scalar mapping is stateless, bounded identity transduction | Source at `modality:src/modality/scalar_field.py`; unit tests above exercise accepted and rejected values |
| Environment sample reaches an Organism cognitive transition in the fixture | World integration fixture and its assertions; one test-supplied composition only |
| The fixture's cognitive candidate is not adopted into the checkpoint written by that fixture | Inspection of `write_checkpoints` and `project_environment` in the fixture; not an assertion of production behaviour |
| No production caller joins the full path | Search of current source and tests in the seven reviewed repositories; a negative search result, not proof about future or external code |
| No learning or semantic understanding is demonstrated | Neither the narrow identity tests nor the integration fixture measures or asserts either outcome |
