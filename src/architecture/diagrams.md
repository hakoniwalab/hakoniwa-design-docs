# Diagram Index

(Informative)

This chapter lists the diagrams to be maintained and provides placeholders.

## Planned Diagrams
- Stack (layered) diagram
- Data Plane / Control Plane flow diagram
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
