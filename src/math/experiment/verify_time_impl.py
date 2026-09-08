#!/usr/bin/env python3
"""Check the single-level logical-clock model in hakoniwa-time-impl.md.

Standard library only. This checks an abstract integer transition system,
not the C++ binary, shared-memory atomicity, liveness, or simulator accuracy.
"""

from collections import deque
from itertools import product
from typing import Sequence, Tuple


def core_step(
    core: int, observed_assets: Sequence[int], delay: int, delta_core: int
) -> int:
    """Literal translation of the core's current-time stopping condition."""
    for asset_time in observed_assets:
        diff = asset_time - core
        if diff <= -delay:
            return core
    return core + delta_core


def asset_step(asset: int, observed_core: int, delta_asset: int) -> int:
    """Literal translation of the asset's next-time stopping condition."""
    next_time = asset + delta_asset
    if next_time > observed_core:
        return asset
    return next_time


def check_state(
    core: int, assets: Sequence[int], delay: int, delta_core: int
) -> None:
    assert assets
    assert max(assets) <= core
    assert core - min(assets) < delay + delta_core
    assert max(assets) - min(assets) < delay + delta_core


def check_boundaries_and_witness() -> None:
    # Equality in the NEXT gap is allowed; equality in the CURRENT gap stops.
    assert core_step(90, [0], 100, 10) == 100
    assert core_step(100, [0], 100, 10) == 100
    assert core_step(100, [1], 100, 10) == 110
    assert asset_step(90, 100, 10) == 100
    assert asset_step(100, 100, 10) == 100
    # Stale, truthful observations can suppress an otherwise permitted step.
    assert core_step(100, [0], 100, 10) == 100
    assert core_step(100, [1], 100, 10) == 110
    assert asset_step(100, 100, 10) == 100
    assert asset_step(100, 110, 10) == 110

    # Reachable from all-zero initialization, not just a hypothetical state.
    delay, delta_core = 100, 10
    core, assets = 0, [0, 0]
    check_state(core, assets, delay, delta_core)
    core = core_step(core, assets, delay, delta_core)
    check_state(core, assets, delay, delta_core)
    assets[0] = asset_step(assets[0], core, 1)
    check_state(core, assets, delay, delta_core)
    assets[1] = asset_step(assets[1], core, 10)
    check_state(core, assets, delay, delta_core)
    while core < 110:
        next_core = core_step(core, assets, delay, delta_core)
        assert next_core > core
        core = next_core
        check_state(core, assets, delay, delta_core)
    assert core_step(core, assets, delay, delta_core) == core
    while assets[1] < core:
        assets[1] = asset_step(assets[1], core, 10)
        check_state(core, assets, delay, delta_core)
    assert (core, *assets) == (110, 1, 110)
    assert max(assets) - min(assets) == delay + delta_core - 1 == 109


def explore(
    delay: int, delta_core: int, delta_assets: Sequence[int]
) -> Tuple[int, int]:
    """Explore every reachable relative-clock state for one parameter set.

    State is gaps[i] = core - asset[i]. All guards depend only on these
    differences, so quotienting out a common time shift preserves transitions.
    There is no step-count horizon or bound-based pruning. Blocked transitions
    and delayed-observation waits are self-loops and cannot alter an invariant.
    """
    if not delta_assets or min(delay, delta_core, *delta_assets) <= 0:
        raise ValueError("At least one asset and positive parameters are required")
    initial = (0,) * len(delta_assets)
    seen, pending = {initial}, deque([initial])
    transitions = 0
    while pending:
        gaps = pending.popleft()
        assert min(gaps) >= 0
        assert max(gaps) < delay + delta_core
        assert max(gaps) - min(gaps) < delay + delta_core
        successors = []
        if all(-gap > -delay for gap in gaps):
            successors.append(tuple(gap + delta_core for gap in gaps))
        for i, delta_asset in enumerate(delta_assets):
            if delta_asset <= gaps[i]:
                updated = list(gaps)
                updated[i] -= delta_asset
                successors.append(tuple(updated))
        for state in successors:
            transitions += 1
            if state not in seen:
                seen.add(state)
                pending.append(state)
    return len(seen), transitions


def main() -> None:
    check_boundaries_and_witness()
    configurations = states = transitions = 0
    for delay, delta_core, delta_a, delta_b in product(
        range(1, 9), range(1, 9), range(1, 5), range(1, 5)
    ):
        count, edges = explore(delay, delta_core, (delta_a, delta_b))
        configurations += 1
        states += count
        transitions += edges
    print("PASS: boundary, stale-observation, and reachable 109 us witness checks")
    print(f"PASS: {configurations} parameter sets; {states} relative states; "
          f"{transitions} progressing transitions")
    print("Abstract-model safety checks only; not a C++ integration test or liveness proof.")


if __name__ == "__main__":
    main()
