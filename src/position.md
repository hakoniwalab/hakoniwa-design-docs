# The Positioning of Hakoniwa
— Design Assumptions, Evaluation Axes, and Semantics for a Distributed Simulation Execution Platform —

## 1. Introduction (Purpose & Scope)
This document clarifies the positioning of Hakoniwa within distributed and cooperative simulation technologies, not by comparing superiority to existing technologies, but by answering:
- What problem settings are assumed.
- What is guaranteed and what is not.
- Which evaluation axes the design is based on.

We refer to the following as comparison points:
- HLA (High Level Architecture)
- FMI (Functional Mock-up Interface, especially Co-Simulation)
- Hakoniwa

This document does not aim to cover historical background or implementation details. It focuses on design philosophy and semantic positioning.

## 2. Terminology
### 2.1 Terms Related to Time and Execution
- Logical Time: A time axis defined on the simulation model.
- Wall-clock Time: Elapsed time in the real world.
- ΔT: The update step size used in numerical computation or communication.
- d_max (Maximum Allowable Delay): The maximum communication delay defined at system design time for distributed execution.

### 2.2 Hakoniwa-Specific Terms
- Hakoniwa Asset: A unit executed as an OS process. It contains one or more Execution Units (EUs).
- Execution Unit (EU): An execution entity representing the same logical model in a distributed environment. An EU is a logical entity and may have instances across multiple assets.
- Owner / Non-Owner: The entity responsible for state updates and PDU writes for an EU.
- Epoch: A generation number during which the execution responsibility (Owner) for an EU is uniquely determined.
- Commit Point: A boundary where an Epoch update is agreed upon system-wide based on Conductor state transitions, and the execution result and responsibility of that Epoch are semantically fixed.
- Runtime Delegation (RD): A mechanism to safely switch the Owner of an EU during execution.
- Conductor (Hakoniwa Conductor): An entity that manages execution responsibility transitions for EUs, controls Epoch updates, and establishes Commit Points. The Conductor does not perform numerical computation or decide execution strategies or solvers. Decisions are made based on externally provided policies, but the policy contents and optimality are outside Hakoniwa’s scope.

## 3. Problem Setting: What Causes Failure in Distributed Execution
Hakoniwa starts from the following question:

In distributed simulation, what truly causes breakdowns:
is it the small time offsets themselves,
or the ambiguity of execution responsibility and causality?

In distributed environments, time drift is unavoidable due to communication delay and parallel execution. Hakoniwa does not attempt to eliminate drift; it designs for a structure where causality and responsibility do not collapse even when drift exists.

## 4. Assumptions of Existing Technologies
### 4.1 FMI (especially FMI-CS)
FMI is an interface standard for exchanging and coupling numerical models (FMUs).
- FMU inputs/outputs and dependencies are defined.
- Execution order, step control, and delay handling are delegated to the Master Algorithm (MA).

By intentionally leaving MA out of scope, FMI permits diverse solvers and tool implementations. As a result, causality and delay handling in distributed execution are not guaranteed by the standard.

### 4.2 HLA
HLA is a framework for distributed event and logical-time simulation.
- RTI manages logical time progress and causal ordering.
- Time consistency and reproducibility are top-level concepts.

HLA enforces time and causality across the entire system.

### 4.3 Summary of Comparison
In short:
- FMI focuses on model exchange and coupling.
- HLA governs time and causality.
Hakoniwa focuses on managing execution responsibility in distributed execution.

## 5. Core Assumptions of Hakoniwa
Hakoniwa is designed with the following assumptions:
- Time drift inevitably occurs in distributed execution.
- Execution performance (real-time or faster) is the highest priority.
- Strict global logical time consistency is not a goal.
- Execution responsibility and causal boundaries must not be ambiguous.

## 6. Core Mechanisms of Hakoniwa
### 6.1 Bounded-Drift Time Synchronization
Hakoniwa adopts a bounded-drift distributed time synchronization mechanism based on d_max.

This mechanism assumes that each asset continues to execute in parallel and does not aim for strict global time alignment. Instead, it guarantees that time drift during distributed execution always remains within a controllable bound.

Concrete guarantees depend on the execution configuration:
- In a single-node configuration with multiple assets, the simulation time difference between any assets is always at most d_max.
- In a distributed configuration with one server and multiple clients, considering the path client A → server → client B, if each direction has delay up to d_max, the round trip is 2·d_max. Thus the simulation time difference between any clients is always at most 2·d_max.

These guarantees always hold in logical time.

If, in wall-clock time, communication delay exceeds d_max, Hakoniwa does not automatically correct time consistency. Such situations are treated as outside design assumptions and are left to higher-level operational decisions such as stopping or reconfiguring execution.

This mechanism does not guarantee causality or execution responsibility. Those are handled separately by Runtime Delegation and Commit Point.

### 6.2 Runtime Delegation (RD)
Runtime Delegation (RD) is realized through EU state transitions managed by the Conductor.
- Epoch manages generations of execution responsibility.
- Commit Point fixes causality and responsibility.
- The Commit Point and the start of execution by the new Owner may not coincide.

This is because Commit Point is a semantic fixation, whereas the new Owner’s process start and execution begin depend on distributed process creation and communication. This gap is inevitable and is assumed by design.

RD is not primarily for failover or load balancing. It is a design principle to preserve uniqueness of responsibility and causality in distributed execution.

## 7. What Hakoniwa Decides and Does Not Decide
### 7.1 What Hakoniwa Decides
- The Owner for each EU is always unique.
- Responsibility for PDU writing is never ambiguous.
- Time drift is bounded (d_max or 2·d_max).
- Causality and responsibility are fixed at Commit Points.
- Execution responsibility transitions are managed by the Conductor.

### 7.2 What Hakoniwa Does Not Decide
- Numerical methods (Jacobi, Gauss–Seidel, etc.).
- Policies for triggering RD.
- Optimal strategies for placement and load balancing.
- Numerical handling of delayed data (use as-is, interpolate, extrapolate, etc.).

These are design freedoms left to the user.

## 8. Evaluation Axes
Hakoniwa adopts the following primary evaluation axes:
1. Execution performance: Distributed execution at real-time or faster.
2. Bounded drift: Time drift remains within a controllable range.
3. Uniqueness of execution responsibility: The execution owner is never ambiguous.
4. Semantic determinacy: Causal boundaries are explicitly fixed at Commit Points.

Hakoniwa does not treat the following as primary evaluation axes:
- Full reproducibility in global logical time.
- Bitwise equality at the floating-point level.
- Automatically optimized execution strategies.

Hakoniwa provides only the minimum semantics necessary to prevent breakdown.

## 9. Intended Use Cases (Reference)
### 9.1 Suitable Scenarios
Hakoniwa is suitable for:
- HILS (Hardware-in-the-Loop Simulation) with real-time constraints.
- Cooperative simulations in environments with changing load and placement (edge-cloud offloading, etc.).
- Systems requiring dynamic responsibility switching on node failures.

### 9.2 Unsuitable Scenarios
Other options may be better when:
- Full reproducibility is required (floating-point level matching).
- Strict logical-time consistency is prioritized over execution performance.

## 10. Technical Comparison Matrix (Reference)

The following table summarizes the fundamental design assumptions and evaluation
axes of HLA, FMI (Co-Simulation), and Hakoniwa.

| Aspect | HLA | FMI (Co-Simulation) | Hakoniwa |
|------|-----|----------------------|----------|
| Primary focus | Logical time & causality control | Model exchange & coupling | Execution responsibility in distributed execution |
| Time management | Strict global logical time | Delegated to Master Algorithm | Bounded drift (d_max, 2·d_max) |
| Global time consistency | Required | Not specified | Not required |
| Real-time performance | Secondary | Depends on MA | Primary |
| Handling of time drift | Prevented by synchronization | Delegated to MA | Accepted and bounded |
| Execution responsibility | Implicit in RTI ordering | Not defined | Explicit (Owner / Epoch) |
| Responsibility switching | Not a primary concept | Not defined | Core mechanism (RD) |
| Causality fixation | Time-based ordering | Tool-dependent | Commit Point (semantic boundary) |
| Reproducibility | High | Tool-dependent | Not guaranteed |
| Dynamic reconfiguration | Costly | Tool-dependent | Assumed and supported |
| Numerical method selection | Framework-level | User / MA-defined | User-defined |
| Target use cases | Scientific / event-driven simulation | Model integration | Real-time, adaptive, distributed execution |


## 11. Positioning Summary
Hakoniwa is a distributed simulation execution platform that:
- operates on a distributed execution model allowing bounded time drift, and
- assigns semantic uniqueness to causality and execution responsibility.

Hakoniwa does not enforce time consistency, nor does it prescribe numerical solvers. It assumes high-performance distributed execution and specifies only the minimum semantics required to prevent breakdown. This is the design position of Hakoniwa.

Hakoniwa does not negate conventional time-synchronization-centered theory; it complements it by addressing problem domains with different failure modes and requirements.

## Author’s Note
This document does not claim superiority of any technology. It aims to clarify differences in problem setting, assumptions, and evaluation axes.

## 13. FAQ — Common Questions and Critical Discussion
### 13.1 Questions About Design Philosophy
**Q1. Isn’t “execution responsibility” just hiding poor time management?**  
**A:** This critique mixes different problem layers. In Hakoniwa, time management and execution responsibility address different layers.
- Time management (physical layer): “When” data was produced.
- Execution responsibility (semantic layer): “Who” is responsible for that data.

In real distributed systems (e.g., financial transactions, database transactions), the responsibility for state changes often matters more than physical time synchronization.

Hakoniwa is a practical response to the CAP theorem: it prioritizes availability (execution performance) and controls consistency as “bounded drift.” Execution responsibility does not hide time issues; it fixes causality independent of time as a higher-level design principle.

**Q2. Why give up perfect time synchronization?**  
**A:** It is not “giving up,” but an honest design choice based on reality.

Perfect synchronization is impossible in distributed environments due to:
- Network delay variation.
- Asymmetric processing load.
- Clock drift.

HLA-style strict time management waits for all components to synchronize, which causes problems when:
1. Real-time performance is the top priority (e.g., HILS):
   - A single delayed component stalls the entire system.
   - The classic convoy effect.
2. The system configuration changes dynamically (e.g., edge-cloud collaboration):
   - Every node change requires global re-synchronization.

Hakoniwa chooses achievable guarantees: “bounded drift” and “clear responsibility.”

**Q3. Under what conditions does bounded drift hold?**  
**A:** The guarantee holds within the maximum allowable delay d_max defined at design time.

As long as d_max is respected, logical-time drift remains bounded. If communication delay exceeds d_max, it is outside design assumptions. Hakoniwa does not auto-correct in such cases; handling is delegated to operational decisions such as stopping or reconfiguring execution.

This separation clarifies responsibility: the framework guarantees behavior within design conditions; out-of-scope conditions are handled by operations.

### 13.2 Questions About Implementation and Operations
**Q4. Isn’t delegating numerical methods and delayed-data handling to users a responsibility dodge?**  
**A:** No. It is a strategic design decision.

Hakoniwa’s philosophy is to provide only the minimum rules to prevent semantic breakdown, and to leave domain-specific optimization to domain experts.

This mirrors the Unix philosophy: “Do one thing and do it well.”

Comparison:
- Java: memory management enforced by the language (safe but restrictive).
- C++: memory management delegated to developers (risky but flexible).

Neither is always correct; it depends on the use case. Hakoniwa adopts the latter philosophy.

Reasons for “not deciding”:
- Numerical methods: Jacobi may be best for one problem, Gauss–Seidel for another. A fixed choice would constrain users.
- Delayed data handling: Some simulations need interpolation; others should use stale values as-is.

Hakoniwa specifies only “who is responsible for the data,” not how to process it numerically.

**Q5. What is the impact of Commit Point and new Owner start time not matching?**  
**A:** It is not a defect; it reflects distributed reality.

Example: organizational role change.
- Commit Point: “Effective today, a new manager is appointed” (semantic fixation).
- Execution start: the new manager actually starts work (physical start).

These do not coincide, but responsibility is clear:
- Events before the Commit Point are the previous owner’s responsibility.
- Events after the Commit Point are the new owner’s responsibility.

Hakoniwa fixes responsibility at the Commit Point. The physical startup delay does not cause ambiguity. Assuming they always coincide would be unrealistic.

### 13.3 Questions About Applicability
**Q7. Is Hakoniwa unusable for scientific validation simulations?**  
**A:** It depends. Hakoniwa clearly declares its scope.

Suitable:
- Real-time priority (HILS).
- Dynamic load or configuration changes (edge-cloud collaboration).
- Dynamic responsibility switching on node failures.

Unsuitable:
- Full reproducibility at floating-point precision.
- Strict logical-time consistency over execution performance.

Important note: HLA also has limits.
- Real-time systems requiring sub-10ms response.
- Large-scale distributed environments where global synchronization becomes a bottleneck.

Selection should be based on fit to requirements, not superiority.

**Q8. Which should we choose: HLA or Hakoniwa?**  
**A:** Use the following guideline:

The relationship is “division of labor,” not opposition.

Hakoniwa provides a clear solution where HLA struggles (performance-first, dynamic change). HLA remains the standard choice where Hakoniwa does not apply (full reproducibility).

**Q9. How is Hakoniwa different from FMI?**  
**A:** The main differences are:

FMI (especially FMI-CS):
- Focus: interface standard for model exchange and coupling.
- Master Algorithm (MA) is out of scope.
- Result: causality and responsibility in distributed execution are not guaranteed.

Hakoniwa:
- Focus: management of execution responsibility in distributed execution.
- Responsibility (Owner) is always explicit.
- Result: causality is semantically fixed at Commit Points.

Hakoniwa provides clear semantics in the area FMI explicitly chooses not to decide (execution responsibility and causality).
