# Repository Mapping

(Informative/Appendix)

This chapter provides a reference mapping between implementation repositories and design roles, and is not authoritative for semantics. Normative definitions are in other chapters.

| Design Role | Repository | Notes |
| --- | --- | --- |
| Endpoint | https://github.com/hakoniwalab/hakoniwa-pdu-endpoint | Endpoint implementation for PDU send/receive. |
| Endpoint (RPC) | https://github.com/hakoniwalab/hakoniwa-pdu-rpc | RPC-enabled PDU endpoint implementation. |
| Remote API | https://github.com/hakoniwalab/hakoniwa-remote-api | External control API implementation. |
| Bridge | https://github.com/hakoniwalab/hakoniwa-pdu-bridge-core | Core implementation of the PDU bridge. |
| PDU Registry | https://github.com/hakoniwalab/hakoniwa-pdu-registry | Hypothesis: (1) PDU schema/type registry, (2) PDU routing registry, (3) execution configuration metadata registry. |
| Core Execution (Pro) | https://github.com/hakoniwalab/hakoniwa-core-pro | Commercial implementation of the core execution platform. |
| Core Execution (C++) | https://github.com/toppers/hakoniwa-core-cpp | Core execution platform implementation for C++/ROS 2. |
