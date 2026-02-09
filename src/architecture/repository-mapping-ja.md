# Repository Mapping

(Informative/Appendix)

This chapter provides a reference mapping between implementation repositories and design roles, and is not authoritative for semantics. Normative definitions are in other chapters.

| Design Role | Repository | Notes |
| --- | --- | --- |
| Endpoint | https://github.com/hakoniwalab/hakoniwa-pdu-endpoint | Endpoint implementation for PDU send/receive. See `architecture/overview.md` for the design role. |
| Endpoint (RPC) | https://github.com/hakoniwalab/hakoniwa-pdu-rpc | RPC-enabled PDU endpoint implementation. See `architecture/overview.md` for the design role. |
| Remote API | https://github.com/hakoniwalab/hakoniwa-remote-api | External control API implementation. See `architecture/overview.md` for Control Plane positioning. |
| Bridge | https://github.com/hakoniwalab/hakoniwa-pdu-bridge-core | Core implementation of the PDU bridge. Boundary-crossing role is defined in `architecture/overview.md`. |
| PDU Registry (Hypothesis) | https://github.com/hakoniwalab/hakoniwa-pdu-registry | Hypothesis: (1) PDU schema/type registry, (2) PDU routing registry, (3) execution configuration metadata registry. Role is not fixed in this appendix; see `architecture/overview.md` for normative roles. |
| Core Execution (Pro) | https://github.com/hakoniwalab/hakoniwa-core-pro | Commercial implementation of the core execution platform. See `architecture/core-functions.md` for core semantics. |
| Core Execution (C++) | https://github.com/toppers/hakoniwa-core-cpp | Core execution platform implementation for C++/ROS 2. See `architecture/core-functions.md` for core semantics. |
