# Diagram Index

(Informative)

This chapter lists the diagrams to be maintained and provides placeholders.

## Planned Diagrams
- Stack (layered) diagram
- Data Plane / Control Plane flow diagram
- Epoch / Owner transition (conceptual sequence) diagram
- Runtime topology diagram

## Stack (Layered) Diagram (Placeholder)
```mermaid
flowchart TB
  L0[Hardware / OS]
  L1[Hakoniwa Assets]
  L2[Data Plane: EU + Endpoint]
  L3[Control Plane: Conductor + Registry + Remote API]
  L4[Declarative Design: Schema + Generator + Validation]

  L0 --> L1 --> L2 --> L3 --> L4
```

Caption: A conceptual stack view showing major layers and responsibility boundaries. It is not a deployment diagram. Registry is an informative/configuration role, not a semantic authority.

## Data Plane / Control Plane Flow Diagram (Placeholder)
```mermaid
flowchart LR
  subgraph DataPlane[Data Plane]
    EU[Execution Units]
    EP[Endpoint]
    EU --> EP
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

Caption: This diagram shows conceptual plane separation and boundary crossing. It is not a network or runtime deployment diagram. Registry is an informative/configuration role, not a semantic authority.

## Epoch / Owner Transition Diagram (Placeholder)
```mermaid
sequenceDiagram
  participant A as Asset A (Owner: Epoch N)
  participant B as Asset B (Owner: Epoch N+1)
  participant BRG as Bridge / Endpoint
  participant COND as Conductor

  Note over A,BRG: Data Plane execution under Epoch N
  A ->> BRG: Emit PDU (Epoch N)
  BRG -->> A: Deliver within Epoch N

  Note over COND: Control Plane fixes transition
  COND ->> BRG: Commit Point for Epoch N
  COND ->> B: Assign Owner for Epoch N+1
  BRG -->> B: Enable delivery for Epoch N+1

  Note over B,BRG: Data Plane execution under Epoch N+1
  B ->> BRG: Emit PDU (Epoch N+1)
  BRG -->> B: Deliver within Epoch N+1
```

Caption: A conceptual sequence showing how Conductor fixes a Commit Point and assigns a new Owner for a new Epoch. It is illustrative only and not a deployment or message-protocol specification.
