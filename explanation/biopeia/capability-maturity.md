# Capability maturity: what the documented evidence supports

This is a derived summary of unit documents at the individual review
revisions recorded for them, not a fresh audit of every source repository at
one shared revision and not a new status authority. Each row points to the
documents that own its detailed claims; consult those documents for their
reviewed-against revisions and evidence.
The labels below describe the evidence visible in those documents; they are
not release gates, quality scores, or claims of behaviour observed in a
complete running Biopeia system. Where evidence is limited to source or
tests, the summary says so. No row implies an end-to-end runtime observation.

## Summary

| Capability | Evidence-backed summary | What is not established | Canonical detail |
|---|---|---|---|
| Organism identity and continuation | Identity, transition and checkpoint mechanisms exist in source and have unit-test coverage. A cognitive sense-to-checkpoint transition is exercised by Organism tests. | A complete Organism checkpoint composed with all longitudinal state, or continuity observed through a live world cycle. | [Identity and checkpoint](../organism/identity-and-checkpoint.md); [transition and continuation](../organism/transition-and-continuation.md); [cognitive checkpoint](../organism/cognitive-checkpoint.md); [sense-to-checkpoint](../organism/sense-to-checkpoint-transition.md) |
| Cognition and adaptation | Graph execution, plasticity and selected transition composition are implemented and tested as bounded mechanisms. | A production learning loop that receives real environmental transduction and yields adaptive action. | [Cognitive graph](../organism/cognitive-graph.md); [graph plasticity](../organism/graph-plasticity.md); [sense-to-checkpoint](../organism/sense-to-checkpoint-transition.md) |
| Agency and action | Action-path records and functions exist; integration fixtures compose selected stages. | A production composition from sensed state through agency to a complete physical command; an organism-level capability to act demonstrated in a live run. | [Action path](../organism/action-path.md); [execution bindings](../organism/execution-binding-and-affordances.md); [competence development](../organism/competence-development.md) |
| Outcome and causal evidence | Bounded evidence and outcome structures exist; the current documents identify their source-level callers and test limits individually. | A validated causal-learning result or a complete feedback loop that consumes those records. | [Actuator evidence](../organism/actuator-evidence.md); [causal evidence](../organism/causal-evidence-and-controllability.md); [executive outcome ledger](../organism/executive-outcome-ledger.md); [prospective deliberation](../organism/prospective-deliberation.md) |
| Genome and inheritance | Genome records and persistence are documented. | General consumers that make inherited values functionally observable, or operational reproduction and population evolution. | [Genome and inheritance](../organism/genome-and-inheritance.md); [candidate hypotheses](research-hypotheses.md) |
| Embodiment | Physical and articulated state, projections and owner-side adoption are implemented and tested. | A production-connected physical solver path spanning World and all owners. | [Articulated body](../embodiment/articulated-body.md); [physical state](../embodiment/physical-state.md); [physical projection](../embodiment/physical-projection.md); [actuation projection](../embodiment/actuation-projection.md) |
| Environment | Static scenes, finite resources, dynamic state and procedural genesis have source-backed contracts and tests. | A complete environmental dynamics model or a demonstrated live coupling of environmental state to organism action. | [Static scene](../environment/static-scene.md); [finite resource](../environment/finite-resource.md); [dynamic state](../environment/dynamic-state.md); [procedural genesis](../environment/procedural-genesis.md) |
| World causal persistence | World has source mechanisms for durable transitions, journal/manifest and recovery; physical-step coordination is exercised through fixtures. | A complete production orchestration with the solver and owner adapters wired together, or a process-failure recovery campaign. | [Durable runtime](../world/durable-runtime.md); [physical step](../world/physical-step.md); [recovery](../world/recovery.md) |
| Modality | A dimensionless scalar identity contract exists; a World integration fixture carries a scalar-field signal into an Organism cognitive transition. | General sensory transduction, interpretation, persistent Modality state or a production sensory connection. | [Modality current state](../modality/current-state.md); [sense-to-checkpoint](../organism/sense-to-checkpoint-transition.md) |
| Observation | Semantic claim types and an in-memory plane exist; selected construction and delivery paths are exercised in tests. | Real publications from the semantic authorities into Observation during an integrated run. | [Semantic claim model](../observation/semantic-claim-model.md); [observation plane](../observation/observation-plane.md); [inherited projection](../observation/inherited-projection.md) |
| Lab evidence custody | Lab records an operator-initiated material transfer with evidence in a World cut. | A complete scientific campaign validating the integrated organism cycle. | [Operator material transfer](../lab/operator-material-transfer.md); [research hypotheses](research-hypotheses.md) |
| Integrated causal cycle | Separate tested slices cover scalar sensing/cognition, physical-step coordination, persistence, and evidence transfer. | One production execution joining environment, transduction, Organism agency, physical adoption, durable commit, observation and Lab evidence. | [One step across the domains](one-step-across-the-domains.md) |

## Reading the labels

“Exists in source” is not synonymous with “works as a system”. A unit test
supports only the exercised contract and inputs. An integration fixture
supports the composition present in that fixture, not an untested runtime
caller. Runtime observation and scientific validation require their own
evidence; this table does not claim either where the canonical unit document
does not report it.

The scientific hypotheses remain candidates until the owner confirms them.
This summary does not promote any candidate to a result, nor does it turn
accepted architecture into implemented behaviour.
