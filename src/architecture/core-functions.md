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

## 2. Bounded Drift
**What Hakoniwa Guarantees**
- Logical-time drift is always bounded within the design-time limit (d_max).
- In a single-node configuration, the bound is d_max; in distributed configurations, it is 2·d_max.

**What Hakoniwa Does Not Decide**
- Automatic correction when d_max is exceeded
- Exact alignment of physical time and logical time

## 3. Owner Uniqueness
**What Hakoniwa Guarantees**
- The Owner of every EU is always unique.
- Responsibility for PDU writing is never ambiguous.

**What Hakoniwa Does Not Decide**
- Optimization strategy for Owner transitions
- Performance evaluation criteria for Owner

## 4. Epoch (Generation Identification)
**What Hakoniwa Guarantees**
- The generation of execution responsibility is uniquely identified by Epoch.
- Equality of Epoch is treated as semantic equality (equality-based).

**What Hakoniwa Does Not Decide**
- Optimization of Epoch switch timing
- Specific numbering scheme for generations

## 5. Commit Point (Semantic Fixation)
**What Hakoniwa Guarantees**
- Causal boundaries and responsibility are semantically fixed at Commit Points.
- A gap between Commit Point and physical execution start is allowed.

**What Hakoniwa Does Not Decide**
- Policies for triggering Commit Points
- Forced synchronization of physical start

## 6. Responsibility Separation (Conductor / Bridge / Hakoniwa Asset)
**What Hakoniwa Guarantees**
- Conductor manages only execution responsibility transitions and does not handle numerical solvers or optimization.
- Bridge ensures boundary consistency between Data Plane and Control Plane.
- Hakoniwa Asset operates as a parallel execution entity on the Data Plane.

**What Hakoniwa Does Not Decide**
- Internal algorithms of Conductor
- Communication methods for Bridge
- Implementation language or environment for Hakoniwa Asset

## 7. Declarative Design (Schema + Generator + Validation)
**What Hakoniwa Guarantees**
- Execution configurations are described declaratively.
- Design consistency is validated.

**What Hakoniwa Does Not Decide**
- Specific generation methods
- Implementation form of validation tools

## 8. Endpoint (Causality Boundary and Delivery/Lifetime Semantics)
**What Hakoniwa Guarantees**
- Endpoint is not a generic messaging API.
- Endpoint defines causality boundaries and delivery/lifetime semantics.

**What Hakoniwa Does Not Decide**
- Message format or optimization methods
- Numerical correction for delivery delays
