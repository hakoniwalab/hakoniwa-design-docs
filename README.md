# hakoniwa-design-docs

This repository contains the **design source of truth** for **Hakoniwa**.

It centralizes terminology, assumptions, semantic guarantees, mathematical proofs,
architectural boundaries, and positioning of Hakoniwa as a distributed execution
and simulation platform.

The documents in this repository are written as **primary design artifacts** and
can be built into human-readable whitepapers (PDF / HTML).

---

## Purpose

Hakoniwa has grown beyond what can be reasonably explained by per-repository
READMEs alone.

This repository exists to:

- Define **terminology** (e.g., ExecutionUnit, Owner, Epoch, Commit Point)
- Make **assumptions and guarantees explicit**
- Provide **mathematical foundations** (e.g., bounded-drift time synchronization)
- Clarify **architectural responsibilities and boundaries**
- Explain **positioning** relative to other simulation frameworks (e.g., HLA, FMI)
- Serve as a **single source of truth** for design intent

---

## Scope

### Included
- Design assumptions and non-assumptions
- Semantic models and invariants
- Formal or semi-formal proofs
- Architecture-level descriptions
- Positioning and evaluation axes

### Excluded
- Component implementation details
- Step-by-step setup or operational manuals
- Generator CLI usage and runtime configuration specifics

Those belong to individual component repositories
(e.g., `hakoniwa-rd-core`, `hakoniwa-pdu-bridge-core`, etc.).

---

## Document Structure (Planned)

- `src/`: Core design documents (Markdown, authoritative)
- Positioning document: [Hakoniwa positioning](src/position.md) (`src/position.md`)
- Glossary: [Hakoniwa glossary](src/glossary.md) (`src/glossary.md`)
- `src/proofs/`
  - Mathematical proofs and formal reasoning
- `diagrams/`
  - Architecture and concept diagrams (SVG as primary format)
- `dist/`
  - Generated artifacts (PDF / HTML)  
    *(not committed; produced via build/CI)*

---

## Build

Design documents are written in Markdown and intended to be **built** into
whitepapers.

Typical outputs:
- PDF (for distribution and review)
- HTML (for web reading)

Build instructions will be added once the document set stabilizes.

---

## Relationship to Other Repositories

This repository defines **what Hakoniwa is**.

Other repositories define **how Hakoniwa is implemented**.

Each implementation repository should reference the relevant sections of
`hakoniwa-design-docs` rather than duplicating design explanations.

---

## Status

This repository is under active construction.
Documents may be incomplete, but the intent is to keep all statements
**explicit, reviewable, and consistent**.
