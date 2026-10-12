# Markov models and Markov Brains for Organism cognition: research report v1

**Scope:** documentary research only. This report is not an architecture decision, protocol authorization, experiment authorization, or scientific conclusion.

## Executive assessment

The term *Markov* names different things here and should not be used as if it identifies one candidate architecture:

1. A **Markov chain** is a stochastic process whose next-state distribution depends on its current state (or a specified finite history for a higher-order chain). It is a mathematical model, not by itself a learning mechanism or cognitive architecture.
2. A **hidden Markov model (HMM)** adds latent states and an observation/emission model. Inference estimates beliefs over hidden states; learning model parameters is a separate operation. A HMM does not imply online plasticity, evolution, agency, or semantic interpretation.
3. **Variable-order Markov models / variable-length Markov chains / context trees** predict a categorical next symbol using a context whose length can vary. They offer a compact sequence-prediction family, but do not intrinsically explain why a sequence matters to an organism.
4. **Markov Brains** are evolvable networks assembled from heterogeneous computational gates. Their “Markov” name does not mean they are simply a Markov-chain predictor. Published work adds feedback gates to permit lifetime adaptation; this is distinct from genetic evolution between generations.

**Recommendation: postpone execution of a new experiment; continue bounded research and protocol preparation.** The primary literature establishes that some Markov-Brain configurations can evolve within-lifetime feedback-based adaptation on specified tasks. It does not establish benefit for Biopeia's Organism, compatibility with its authority boundaries, or that a Markov model improves the current cognitive mechanisms. Current Organism source contains predictive and plasticity components, but this audit found no evidence that the cognition transition is wired into the production Organism step. Open owner findings #44 and #45 also raise unresolved efficacy and checkpoint-continuity questions. These are material confounds for an experiment comparing added prediction or learning. This report therefore supports neither adopting nor rejecting any model family.

## Question and method

Question: could Markov sequence models or Markov-Brain-like mechanisms add scientifically useful, internally owned predictive adaptation to Organism, without importing external semantic/reward authority or confusing individual learning with evolution?

Method: review foundational/primary sources; inspect current `biopeia/organism` main at `699881b7f7cef195244e69b01977d40fc66a6f9c`; inspect current explanatory documents in `biopeia/docs` main at `a49c71571d187548b5e0587faffd150c0f94e8c4`; run the targeted cognition learning/composition tests. No runtime experiment, integration trial, genome modification, or production change was performed.

Evidence levels below are kept separate: published result ≠ Biopeia implementation; implementation ≠ composed production behavior; passing unit tests ≠ efficacy or runtime observation.

## Comparison

| Family | Formal object / assumptions | State or memory | Learning mode it supplies | Predictive use | Main limits for this question |
|---|---|---|---|---|---|
| Finite-order Markov chain | Discrete state process; transition probability conditioned on current state or last *k* states | Explicit finite state/history | Parameter estimation is external to the definition; online adaptation is optional | Next-state distribution | State discretization and order are design choices; Markov property is an approximation, not a causal explanation |
| HMM | Latent-state Markov process plus observation/emission distributions | Distribution over latent states and transition/emission parameters | Inference/parameter learning require a selected method and data regime | Predict observations via latent-state posterior | Latent states are not automatically Organism-owned concepts; identifiability, model mismatch, and external labels/objectives require scrutiny |
| Variable-order Markov / VLMC / context tree | Discrete sequence with context length selected by a context-tree/model-selection rule | Suffix/context tree; bounded or selected history | Fit/selection from sequence data; continual update is not guaranteed by the family | Conditional next-symbol distribution with context-dependent memory | Categorical sequence focus; model-selection and stationarity assumptions matter; prediction alone does not establish agency, learning efficacy, or semantics |
| Markov Brain | Evolvable network of heterogeneous deterministic/probabilistic logic gates | Gate/network state, with feedback gates in lifetime-learning variants | Evolution across generations; feedback-gate mechanism can enable within-lifetime adaptation | Task behavior emerges from network/controller; not simply next-symbol prediction | Results depend on gate set, encoding, evolutionary setup, environment and fitness; external fitness can carry authority; not a drop-in statistical predictor |
| Current Organism cognition components | Bounded directed graph, explicit-tick activation, separate learning/plasticity and private-model components | Previous activation frames and separately represented mutable/checkpoint state | Local update functions exist; composition supplies caller arguments; production caller coverage remains uncertain | Predictor nodes/error objects and shadow prediction candidates exist in source | A name or isolated composition does not prove an Organism-level cognitive loop, predictive advantage, or exact continuation |

These families are alternatives or potentially composable tools, not interchangeable implementations. A useful comparison must fix the prediction target, input alphabet/representation, memory budget, training signal, online update policy, and baseline before judging results.

## Published evidence

- **Markov Brain framework.** Hintze et al. describe Markov Brains as evolvable networks of heterogeneous computational components, with component functions, connections, sensor inputs, and motor outputs subject to evolutionary optimization. This is a framework for computational organisms, not a synonym for a Markov transition model.
- **Lifetime learning in Markov Brains.** Sheneman & Hintze introduce feedback gates into this framework. They report evolved networks that use internal feedback to adapt within an individual's lifetime without an external objective feedback signal, in their specified computational model and tasks. The result is existence evidence for those setups, not general evidence that internally generated feedback is normatively correct, that all reward-like control is absent, or that the mechanism transfers to Organism.
- **Variable-length Markov chains.** Bühlmann & Wyner develop context models for categorical time series, data-driven context selection/fitting, prediction, and asymptotic properties under their stated assumptions. This supports considering context trees for compact sequence prediction; it does not supply an Organism semantics or an online cognitive learning loop.

The publication results are task- and setup-bound. The report does not claim an independent reproduction of the papers.

## Current Biopeia implementation and evidence

Source baseline: `biopeia/organism@699881b7f7cef195244e69b01977d40fc66a6f9c`.

- `src/organism/cognition/graph.py` defines bounded nodes/edges and explicit-tick activation. Predictor nodes carry a target node identifier, but graph activation itself is a numerical graph pass, not a general probabilistic state estimator.
- `src/organism/cognition/learning.py` computes one-step prediction-error records and defines eligibility and Oja-style weight-update helpers. It also defines shadow prediction candidates that compare accumulated losses to persistence baselines and do not themselves mutate the graph.
- `src/organism/cognition/composition.py` now calls `advance_cognition`, computes prediction errors and calls update helpers using eligibility/modulation arguments provided by its caller. This is a composed package function, not by itself proof of production Organism-step integration.
- In the audited `src/organism` tree, references to `advance_cognition` are its definition plus calls inside cognition package modules (`composition.py`, `sense_input.py`); this did not establish a caller from the organism-level production step. That bounded source search is not a whole-system runtime trace.
- The relevant current documentation (`cognitive-graph.md`, `graph-plasticity.md`, `cognitive-checkpoint.md`) describes earlier source baselines and must not be treated as a complete account of this newer composition without a documentation update. This report does not silently revise their authority.
- Owner Issues [organism#44](https://github.com/biopeia/organism/issues/44) and [organism#45](https://github.com/biopeia/organism/issues/45) remain open at report preparation. Their earlier observations were made at older revisions; they are treated here as unresolved owner-tracked questions, not reasserted as reproduced findings at this report's baseline.

Targeted check at the baseline checkout: `uv run pytest -q tests/source_unit/cognition/test_learning.py tests/source_unit/cognition/test_composition.py` → **28 passed**. These tests cover unit/composition behavior only. They do not establish a predictive improvement, an organism-level call path, scientific efficacy, or runtime behavior. No new rerun of historical efficacy or checkpoint examples was performed.

## Architectural / constitutional fit to assess

| Constraint | Screening result |
|---|---|
| No externally injected objective/reward authority | HMM/VLMC fitting can be unsupervised, but choice of targets, loss, and model-selection criteria remains an authority-bearing design choice. Markov-Brain evolutionary studies often require fitness; the internally generated feedback result must not be generalized into “no objective” without examining the complete task/evolution setup. No model is cleared by this screen. |
| Genome encodes capabilities without semantic labels | A gate/genome encoding may specify computational structure. Introducing named task states, externally meaningful labels, or hand-authored semantic wiring would require separate justification. No such change is proposed. |
| Postnatal cognitive development | Variable-order models could in principle update from an owned stream; Markov-Brain feedback gates can support within-lifetime adaptation in the cited work. Neither fact shows a valid Organism developmental process. |
| World / Lab / Organism boundary | Any training sequence, outcome, fitness, or label needs an explicit owner and provenance. A Lab evaluator must not silently become an Organism semantic authority. |
| Cognitive time independent of physical `dt` | All comparisons must use the declared Organism cognitive tick / event sequence, not assume physical timestep equivalence. This report defines no clock mapping. |
| Continuity / re-embodiment | Learned parameters and context history raise state ownership, checkpoint completeness, privacy and re-embodiment questions. Open #45 is directly relevant; no model state should be adopted before its persistence contract is decided. |

## Falsifiable hypotheses for a future protocol

These are candidates for a future design/protocol review, **not authorization to execute**. Use held-out episodes or a preregistered split, disclose all exclusions, compare identical observation/action histories, and report uncertainty and compute/state costs.

- **H1 — predictive gain:** On a specified internally owned categorical sequence, a predeclared context-tree predictor achieves lower held-out log loss than both (a) a zero-information/base-rate predictor and (b) a persistence/last-symbol baseline. Null: it does not beat either baseline, or the gain disappears under a held-out split.
- **H2 — useful variable context:** A variable-order model achieves comparable or lower held-out loss than a fixed-order model at lower/equal memory budget, across predeclared sequence regimes. Null: context selection does not improve the loss/resource trade-off or fails under distribution shift.
- **H3 — adaptation distinct from evolution:** A lifetime-adaptive mechanism improves held-out within-lifetime prediction over a frozen matched model without external outcome/fitness signals. Null: apparent gain is explained by leakage, history size, or an external target/reward; or there is no gain. A separate study would be required for evolutionary adaptation across generations.
- **H4 — continuation:** Resuming from an accepted checkpoint produces the declared predictive distribution and adaptation trajectory within a predeclared tolerance versus uninterrupted execution. Null: differences exceed tolerance or required state is absent. This should not be tested until the owner defines acceptable continuity and #45 is resolved.

Metrics should include per-step predictive log loss (and calibration where probabilities are emitted), baseline-relative gain, memory/state bytes, update cost, cold-start behavior, drift/shift sensitivity, and checkpoint divergence. Do not collapse these into a single “cognition” score. A lower predictive loss is not evidence of causal understanding, agency, semantic knowledge, or adaptive value to the organism.

## Risks and open questions

1. **Markov insufficiency:** A fixed or selected finite context may omit relevant history, latent state, interventions, or nonstationarity. If residual dependence remains after the chosen context, the Markov approximation is inadequate for the stated target.
2. **Target leakage / authority:** Who selected the symbolization, target, and evaluation baseline? Does outcome data leak labels or Lab semantics into Organism state?
3. **Confounding learning with evolution:** Evolution across genomes and adaptation within a lifetime require separate experimental units, controls and conclusions.
4. **Confounding implementation with efficacy:** Current isolated tests do not establish integrated production behavior. Before experiments, identify the intended actual call path and fix/document the unresolved efficacy and persistence questions through their owners.
5. **State continuity and privacy:** Context histories, transition counts and latent-state posteriors may persist learned information. Ownership, retention, checkpoint exactness and re-embodiment handling need explicit review.
6. **Baseline asymmetry:** Comparing a stateful model to a stateless baseline or giving one candidate more history/compute would not isolate model-family benefit.
7. **Published-task transfer:** A result on a benchmark/task does not demonstrate performance on an Organism-owned task or fit with Biopeia constraints.

## Disposition

**Postpone execution of a new experiment; continue documentary investigation and protocol preparation.** Do not discard Markov/VLMC/HMM/Markov-Brain families. First reconcile current cognition documentation and implementation path, obtain owner disposition of organism#44/#45 (and any updated #43-related integration evidence), and have Lab review a protocol whose target, state owner, labels, baselines, and authorization class are explicit. Any future experiment needs its own authorization under the applicable scientific policy. The evidence in this report is insufficient to select or adopt an architecture.

This disposition is a research recommendation only. It neither changes Organism architecture nor decides the scientific status of any hypothesis.

## References

1. Baum, L. E. & Petrie, T. (1966). “Statistical Inference for Probabilistic Functions of Finite State Markov Chains.” *Annals of Mathematical Statistics* 37(6), 1554–1563. https://doi.org/10.1214/aoms/1177699147
2. Baum, L. E., Petrie, T., Soules, G. & Weiss, N. (1970). “A Maximization Technique Occurring in the Statistical Analysis of Probabilistic Functions of Markov Chains.” *Annals of Mathematical Statistics* 41(1), 164–171. https://doi.org/10.1214/aoms/1177697196
3. Bühlmann, P. & Wyner, A. J. (1999). “Variable Length Markov Chains.” *The Annals of Statistics* 27(2), 480–513. https://doi.org/10.1214/aos/1018031204
4. Begleiter, R., El-Yaniv, R. & Yona, G. (2004). “On Prediction Using Variable Order Markov Models.” *Journal of Artificial Intelligence Research* 22, 385–421. https://doi.org/10.1613/jair.1491
5. Rissanen, J. (1983). “A Universal Data Compression System.” *IEEE Transactions on Information Theory* 29(5), 656–664. https://doi.org/10.1109/TIT.1983.1056741
6. Sheneman, L. & Hintze, A. (2017). “Evolving autonomous learning in cognitive networks.” *Scientific Reports* 7, 16712. https://doi.org/10.1038/s41598-017-16548-2. Full text: https://pmc.ncbi.nlm.nih.gov/articles/PMC5711912/
7. Hintze, A. et al. (2017). “Markov Brains: A Technical Introduction.” arXiv:1709.05601. https://arxiv.org/abs/1709.05601

## Revision and evidence record

- Report version: 1; prepared 2026-10-12.
- Docs baseline: `biopeia/docs@a49c71571d187548b5e0587faffd150c0f94e8c4`.
- Organism implementation/test baseline: `biopeia/organism@699881b7f7cef195244e69b01977d40fc66a6f9c`.
- Validation performed: targeted Organism learning/composition tests (28 passed); report links/references and Markdown still require repository validation and review before acceptance.
- No runtime test, experiment, architectural change, protocol approval, or scientific acceptance was performed.
