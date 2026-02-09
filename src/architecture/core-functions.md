# Hakoniwa Core Functions (Minimum Semantics)

(Normative)

This chapter defines the minimum semantics provided by Hakoniwa (the minimum semantics required to prevent breakdown), independent of implementation. All definitions here are normative. Optimization, policies, and operational decisions are out of scope.

## 1. Distributed Execution Model (Parallel-First)
**What Hakoniwa Guarantees**
- Multiple assets are assumed to run in parallel.
- Execution responsibility and causal boundaries are semantically fixed even under parallel execution.

**What Hakoniwa Does Not Decide**
- Optimization of execution placement
- Degree of parallelism and scheduling strategy

**Invariant:** Responsibility and causal boundaries are semantically fixed even under parallel execution (this does not imply optimality or efficiency).

## 2. Bounded Drift
**What Hakoniwa Guarantees**
- Logical-time drift is always bounded within the design-time limit (d_max).
- In a single-node configuration, the bound is d_max; in distributed configurations, it is 2·d_max.

**What Hakoniwa Does Not Decide**
- Automatic correction when d_max is exceeded
- Exact alignment of physical time and logical time

**Invariant:** Logical-time drift does not exceed the design bounds (d_max / 2·d_max); it does not imply physical-time synchronization or zero delay.

## 3. Owner Uniqueness
**What Hakoniwa Guarantees**
- The Owner of every EU is always unique.
- Responsibility for PDU writing is never ambiguous.

**What Hakoniwa Does Not Decide**
- Optimization strategy for Owner transitions
- Performance evaluation criteria for Owner

**Invariant:** The Owner of an EU is unique at any point in time (this does not forbid Owner transitions).

## 4. Epoch (Generation Identification)
**What Hakoniwa Guarantees**
- The generation of execution responsibility is uniquely identified by Epoch.
- Equality of Epoch is treated as semantic equality (equality-based).

**What Hakoniwa Does Not Decide**
- Optimization of Epoch switch timing
- Specific numbering scheme for generations

**Invariant:** Equality of Epoch implies semantic identity (it does not imply simultaneous physical execution).

## 5. Commit Point (Semantic Fixation)
**What Hakoniwa Guarantees**
- Causal boundaries and responsibility are semantically fixed at Commit Points.
- A gap between Commit Point and physical execution start is allowed.

**What Hakoniwa Does Not Decide**
- Policies for triggering Commit Points
- Forced synchronization of physical start

**Invariant:** Commit Point is the semantic fixation point for responsibility and causal boundaries (not a physical start synchronization point).

## 6. Responsibility Separation (Conductor / Bridge / Hakoniwa Asset)
**What Hakoniwa Guarantees**
- Conductor manages only execution responsibility transitions and does not handle numerical solvers or optimization.
- Bridge ensures boundary consistency between Data Plane and Control Plane.
- Hakoniwa Asset operates as a parallel execution entity on the Data Plane.

**What Hakoniwa Does Not Decide**
- Internal algorithms of Conductor
- Communication methods for Bridge
- Implementation language or environment for Hakoniwa Asset

**Invariant:** Responsibilities are separated across Conductor, Bridge, and Hakoniwa Asset without overlap (this does not preclude a single-process implementation).

## 7. Declarative Design (Schema + Generator + Validation)
**What Hakoniwa Guarantees**
- Execution configurations are described declaratively.
- Design consistency is validated.

**What Hakoniwa Does Not Decide**
- Specific generation methods
- Implementation form of validation tools

**Invariant:** Execution configuration is declarative and its consistency is validated (the generation toolchain is not constrained).

## 8. Endpoint (Causality Boundary and Delivery/Lifetime Semantics)
**What Hakoniwa Guarantees**
- Endpoint is not a generic messaging API.
- Endpoint defines causality boundaries and delivery/lifetime semantics.

**What Hakoniwa Does Not Decide**
- Message format or optimization methods
- Numerical correction for delivery delays

**Invariant:** Endpoint specifies causality boundaries and delivery/lifetime semantics (it is not a generic messaging API).

**Clarification:** A causality boundary fixes which data/events belong to which Owner/Epoch, preventing post-hoc reinterpretation even under bounded drift or physical start delays.
