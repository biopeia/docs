# Publication

How the documentation is assembled into one ordered work.

Three things are kept apart:

- the **corpus** (`explanation/`, `technical/`, `reference/`) says what is known;
- the **registry** (`registry/`) says where it comes from and what state it is in;
- the **publication** (this directory) says in which order it is presented.

`biopeia-master.yaml` is the composition of the main publication. It holds no
documentary text. It lists parts and appendices; each names chapters, which
are documents of this repository in reading order, and generated sections,
which are rendered from the registry. A published document therefore never
decides what the canonical documentation is: it presents sources that stay
canonical where they are.

The order goes from the system down into its domains and back up: Biopeia as
a whole, Organism, Embodiment, Environment, World, Modality and Observation,
Lab, and last the architecture that crosses domains, followed by the
appendices. `registry/findings.yaml` is audit material and is not published.

## Rules

- A chapter that does not exist, a document listed twice or an unknown
  generated section fails the build.
- Every document under `explanation/` is either a chapter or listed under
  `excluded` with a reason. A new document that nobody placed fails the
  build; nothing is left out silently. `README.md` files are navigation
  indexes and are never chapters.
- A part with no explanatory document of its own is not padded with new text
  here. Writing that document is documentation work, done in the corpus.

```bash
python tools/publication/model.py   # check the manifest
```

## Known gaps

- **Biopeia has no visual style.** The earlier documentation design system was
  deprecated and not carried over, and no replacement has been decided. Until
  one exists, published documents use neutral defaults only and choose no
  colours, typefaces or cover.
- **The first part has no explanatory document.** Nothing in `explanation/`
  yet says what Biopeia is, its principles, or how its domains and
  authorities are separated. The part currently shows only what the registry
  holds about the domains.
- **Notation, parameters and metrics are empty registries.** Their appendices
  say so instead of being omitted.

## Provenance

The publication capabilities (deterministic build, intermediate semantic
projection, editable DOCX, PDF with a real table of contents, build manifest
with hashes) follow those of the publication pipeline of the historical
source repository. Its code was not migrated: it was built around that
repository's component identifiers, books and registries. Everything here is
written against the Biopeia registries, which are the only source.
