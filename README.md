# hakoniwa-design-docs

This repository contains the **design source of truth** for **Hakoniwa**.

It centralizes terminology, assumptions, semantic guarantees, mathematical proofs,
architectural boundaries, and positioning of Hakoniwa as a distributed execution
and simulation platform.

The documents in this repository are written as **primary design artifacts** and
can be built into human-readable whitepapers (PDF / HTML).

**Normative（設計上の規範）** in this repository means implementation-independent rules that must be satisfied for a system to be considered “Hakoniwa.” **Informative（参考情報）** content provides context and examples but is not binding.

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
- English (default)
  - Positioning document: [Hakoniwa positioning](src/position.md) (`src/position.md`)
  - Glossary: [Hakoniwa glossary](src/glossary.md) (`src/glossary.md`)
  - Architecture overview (Normative): [Hakoniwa Architecture Overview](src/architecture/overview.md) (`src/architecture/overview.md`)
  - Core functions (Normative): [Hakoniwa Core Functions (Minimum Semantics)](src/architecture/core-functions.md) (`src/architecture/core-functions.md`)
  - Repository mapping (Appendix): [Repository Mapping](src/architecture/repository-mapping.md) (`src/architecture/repository-mapping.md`)
  - Diagrams (Informative): [Diagram Index](src/architecture/diagrams.md) (`src/architecture/diagrams.md`)
- Japanese (`-ja`)
  - 位置付け: [箱庭の立ち位置](src/position-ja.md) (`src/position-ja.md`)
  - 用語集: [用語集](src/glossary-ja.md) (`src/glossary-ja.md`)
  - アーキテクチャ概要（Normative）: [箱庭アーキテクチャ全体像](src/architecture/overview-ja.md) (`src/architecture/overview-ja.md`)
  - コア機能（Normative）: [箱庭のコア機能（最小意味論）](src/architecture/core-functions-ja.md) (`src/architecture/core-functions-ja.md`)
  - リポジトリ対応表（Appendix）: [リポジトリ対応表](src/architecture/repository-mapping-ja.md) (`src/architecture/repository-mapping-ja.md`)
  - 図版一覧（Informative）: [図版一覧](src/architecture/diagrams-ja.md) (`src/architecture/diagrams-ja.md`)

---

## Build

Design documents are written in Markdown and intended to be **built** into
whitepapers.

Typical outputs:
- PDF (for distribution and review)
- HTML (for web reading)

Build scripts:
- English PDF: `./scripts/build-pdf-en.sh`
- Japanese PDF: `./scripts/build-pdf-ja.sh`

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
