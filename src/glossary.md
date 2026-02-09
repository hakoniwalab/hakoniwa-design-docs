# Glossary

## Design Terms (Normative)
- Hakoniwa Asset: A unit executed as an OS process. It contains one or more Execution Units (EUs).
- Execution Unit (EU): An execution entity representing the same logical model in a distributed environment. An EU is a logical entity and may have instances across multiple assets.
- Owner / Non-Owner: The entity responsible for state updates and PDU writes for an EU / an entity without that responsibility.
- Epoch: A generation number during which the execution responsibility (Owner) for an EU is uniquely determined.
- Commit Point: A boundary where an Epoch update is agreed upon system-wide based on Conductor state transitions, and the execution result and responsibility of that Epoch are semantically fixed.
- Runtime Delegation (RD): A mechanism to safely switch the Owner of an EU during execution.
- Conductor (Hakoniwa Conductor): An entity that manages execution responsibility transitions for EUs, controls Epoch updates, and establishes Commit Points. The Conductor does not perform numerical computation or decide execution strategies or solvers.
- Data Plane: The domain responsible for transmitting, updating, and advancing time for execution data required for simulation (e.g., PDUs).
- Control Plane: The domain responsible for transferring execution responsibility, managing generations, fixing causal boundaries, and applying policies.
- Endpoint: A boundary for data transfer. It defines causality boundaries and delivery/lifetime semantics, not a generic messaging API.
- Bridge: An intermediary role that ensures boundary consistency between the Data Plane and Control Plane.
- Registry: A role that holds system-wide configuration and definition information, without responsibility or causality semantics.
- Remote API: The API surface for control operations and external integration.
- Bounded Drift: A time synchronization principle that keeps drift within a defined bound (e.g., d_max or 2·d_max).

## General Engineering Terms (Informative)
- Logical Time: A time axis defined on the simulation model.
- Wall-clock Time: Elapsed time in the real world.
- ΔT: The update step size used in numerical computation or communication.
- d_max (Maximum Allowable Delay): The maximum communication delay defined at system design time for distributed execution.
- PDU (Protocol Data Unit): A data unit used for communication between simulation components.
- FMI (Functional Mock-up Interface): An interface standard for exchanging and coupling numerical models (FMUs).
- FMI-CS (FMI for Co-Simulation): The FMI profile focused on co-simulation.
- FMU (Functional Mock-up Unit): A packaged model used in FMI.
- MA (Master Algorithm): The algorithm that orchestrates execution order, step control, and delay handling in FMI co-simulation.
- HLA (High Level Architecture): A framework for distributed event and logical-time simulation.
- RTI (Runtime Infrastructure): The HLA component that manages logical time progress and causal ordering.
- HILS (Hardware-in-the-Loop Simulation): A simulation setup that includes real hardware in the loop with real-time constraints.
