# Hakoniwa Architecture Overview

(Normative)

## Purpose and Scope
This chapter defines the Hakoniwa architecture based on responsibilities and boundaries. The content here is a design norm independent of implementation repositories. Implementation composition and naming are separated into an appendix and are not covered in this chapter.

## Data Plane and Control Plane
Hakoniwa clearly separates the Data Plane and the Control Plane.

- Data Plane: The domain responsible for transmitting, updating, and advancing time for execution data required for simulation (e.g., PDUs).
- Control Plane: The domain responsible for transferring execution responsibility, managing generations, fixing causal boundaries, and applying policies.

This separation is a foundational principle to balance performance-first distributed execution with responsibility and causality semantics.

### Data Plane / Control Plane Comparison

| Plane | Responsibility | Primary concern | Typical components | What is guaranteed |
| --- | --- | --- | --- | --- |
| Data Plane | Transmission, update, and time progression of execution data | Execution performance and parallelism | Hakoniwa Asset, EU, Endpoint | Causality boundaries and delivery/lifetime semantics are explicitly defined |
| Control Plane | Responsibility transitions, generation management, causal boundary fixation | Uniqueness of responsibility and semantic fixation | Conductor, Registry, Remote API | Semantic fixation of responsibility and causal boundaries at Commit Points |

## Component Design Roles (Responsibilities)
The following are design roles, not repository names.

- **Hakoniwa Asset**: A unit executed as an OS process. It holds EU (Execution Unit) instances and runs in parallel on the Data Plane.
- **Execution Unit (EU)**: A logical execution entity. It can have instances across multiple assets. Ownership (Owner) is always unique.
- **Endpoint**: A boundary for data transfer. It is not a generic messaging API; it defines **causality boundaries** and **delivery/lifetime semantics**.
- **Bridge**: A boundary-crossing role between the Data Plane and Control Plane. It maintains consistency across both planes and ensures cross-boundary connectivity.
- **Conductor**: The core of the Control Plane. It manages execution responsibility transitions for EUs and fixes Epoch and Commit Point. It does not decide numerical solvers or optimization.
- **Registry**: A role that holds system-wide configuration and definition information. It does not hold responsibility or causality semantics.
- **Remote API**: The API surface for control operations and external integration. Control Plane operations are performed through it.

## Architectural Guarantees and Non-Guarantees
### Guaranteed (Architecture Level)
- Data Plane and Control Plane are separated by responsibility.
- Execution responsibility (Owner) is always unique.
- Causal boundaries are semantically fixed at Commit Points.
- Endpoint defines causality boundaries and delivery/lifetime semantics.

### Out of Scope (Architecture Level)
- Selection of numerical solvers and optimization policies
- Optimization of execution placement and load balancing
- Numerical handling of delayed data (interpolation, extrapolation, etc.)
- Choice of implementation languages or frameworks

## Link to Core Semantics
The architectural guarantees in this chapter are realized based on the minimum semantics defined in `architecture/core-functions.md` (Owner uniqueness, Epoch, Commit Point, Data Plane/Control Plane separation, and Endpoint causality boundaries). The architecture assigns these semantics to concrete responsibilities and boundaries.

## Concept Diagram (Simplified)
```mermaid
flowchart LR
  subgraph DataPlane[Data Plane]
    ASSET[Hakoniwa Assets]
    EU[Execution Units]
    EP[Endpoint]
    ASSET --> EU --> EP
  end

  subgraph ControlPlane[Control Plane]
    COND[Conductor]
    REG[Registry]
    API[Remote API]
    API --> COND --> REG
  end

  EP <--> BRG[Bridge]
  BRG <--> COND
```
