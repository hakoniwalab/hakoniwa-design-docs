#!/usr/bin/env python3
"""Finite model checks for hakoniwa-time-impl.md; not a C++ runtime test.

Run with Python 3.10+ (standard library only):
    python3 src/math/experiment/check_time_impl_bound.py

The model permits stuttering. Conservative stale observations can disable an
update but cannot enable one that is disabled by a fresh observation. Therefore
exploring all fresh-observation interleavings also covers committed-clock traces
with conservative observation delays, up to the chosen core-time limit.
"""

from collections import deque
from dataclasses import dataclass
from itertools import product
import unittest


@dataclass(frozen=True)
class State:
    core: int
    assets: tuple[int, ...]


def core_step(
    state: State,
    threshold: int,
    increment: int,
    observed_assets: tuple[int, ...] | None = None,
) -> State:
    """Mirror the current-time guard, retaining the strict equality boundary."""
    if threshold <= 0 or increment <= 0 or not state.assets:
        raise ValueError("Positive parameters and at least one asset are required")
    observed = state.assets if observed_assets is None else observed_assets
    if len(observed) != len(state.assets):
        raise ValueError("Every synchronized asset must be observed")
    if any(not 0 <= old <= now for old, now in zip(observed, state.assets)):
        raise ValueError("Observations must be conservative nonnegative times")
    # Equivalent to the C++ blocking condition: asset_time - core <= -Dmax.
    if any(state.core - old >= threshold for old in observed):
        return state
    return State(state.core + increment, state.assets)


def asset_step(
    state: State,
    index: int,
    increment: int,
    observed_core: int | None = None,
) -> State:
    """Mirror the next-time guard; equality with the core permits progress."""
    if increment <= 0 or not 0 <= index < len(state.assets):
        raise ValueError("A positive increment and valid asset index are required")
    observed = state.core if observed_core is None else observed_core
    if not 0 <= observed <= state.core:
        raise ValueError("The observed core time must be conservative")
    next_time = state.assets[index] + increment
    if next_time > observed:
        return state
    times = list(state.assets)
    times[index] = next_time
    return State(state.core, tuple(times))


def invariant(state: State, threshold: int, core_increment: int) -> bool:
    """Integer clocks (q=1) admit the strengthened inclusive bound B-1."""
    upper = threshold + core_increment - 1
    return (
        all(0 <= state.core - time <= upper for time in state.assets)
        and max(state.assets) - min(state.assets) <= upper
    )


def explore(threshold: int, core_increment: int,
            asset_increments: tuple[int, ...], limit: int) -> int:
    """Check every reachable committed-clock state whose core time <= limit."""
    initial = State(0, (0,) * len(asset_increments))
    seen = {initial}
    pending = deque([initial])
    while pending:
        state = pending.popleft()
        if not invariant(state, threshold, core_increment):
            raise AssertionError((threshold, core_increment, asset_increments, state))
        candidates = [core_step(state, threshold, core_increment)]
        candidates.extend(
            asset_step(state, i, step)
            for i, step in enumerate(asset_increments)
        )
        for candidate in candidates:
            if candidate.core <= limit and candidate not in seen:
                seen.add(candidate)
                pending.append(candidate)
    return len(seen)


class ImplementationBoundTest(unittest.TestCase):
    def test_core_equality_stops(self) -> None:
        state = State(100, (0, 100))
        self.assertEqual(core_step(state, 100, 10), state)

    def test_core_can_reach_threshold_exactly(self) -> None:
        self.assertEqual(core_step(State(90, (0,)), 100, 10), State(100, (0,)))

    def test_asset_next_time_equality_advances(self) -> None:
        self.assertEqual(asset_step(State(100, (90,)), 0, 10), State(100, (100,)))
        self.assertEqual(asset_step(State(100, (91,)), 0, 10), State(100, (91,)))

    def test_reachable_integer_upper_bound(self) -> None:
        state = State(0, (0, 0))
        for _ in range(10):
            state = core_step(state, 100, 10)
            self.assertTrue(invariant(state, 100, 10))
        self.assertEqual(state, State(100, (0, 0)))
        for _ in range(10):
            state = asset_step(state, 1, 10)
        state = asset_step(state, 0, 1)
        self.assertEqual(state, State(100, (1, 100)))
        # The normative next-time guard would refuse this transition.
        self.assertGreater(state.core + 10 - min(state.assets), 100)
        state = core_step(state, 100, 10)
        state = asset_step(state, 1, 10)
        self.assertEqual(state, State(110, (1, 110)))
        self.assertEqual(max(state.assets) - min(state.assets), 109)
        self.assertTrue(invariant(state, 100, 10))
        for _ in range(100):
            # Retrying while the slow asset is unchanged cannot accumulate skew.
            self.assertEqual(core_step(state, 100, 10), state)

    def test_stale_observations_only_restrict_progress(self) -> None:
        state = State(100, (1, 100))
        self.assertEqual(core_step(state, 100, 10).core, 110)
        self.assertEqual(core_step(state, 100, 10, (0, 100)), state)
        self.assertEqual(asset_step(State(110, (100,)), 0, 10).assets, (110,))
        self.assertEqual(
            asset_step(State(110, (100,)), 0, 10, observed_core=100),
            State(110, (100,)),
        )
        with self.assertRaises(ValueError):
            core_step(state, 100, 10, (2, 100))
        with self.assertRaises(ValueError):
            asset_step(state, 0, 1, observed_core=101)

    def test_conservative_guards_for_all_small_observations(self) -> None:
        # Stronger than historical-value sampling: include all integer values
        # between zero and the current time, even those never actually published.
        for core in range(7):
            for a, b in product(range(core + 1), repeat=2):
                state = State(core, (a, b))
                for threshold in range(1, 5):
                    fresh = core_step(state, threshold, 2)
                    for old_a, old_b in product(range(a + 1), range(b + 1)):
                        delayed = core_step(state, threshold, 2, (old_a, old_b))
                        self.assertIn(delayed, (state, fresh))
                for index in range(2):
                    fresh_asset = asset_step(state, index, 2)
                    for old_core in range(core + 1):
                        delayed_asset = asset_step(state, index, 2, old_core)
                        self.assertIn(delayed_asset, (state, fresh_asset))

    def test_exhaustive_small_reachable_states(self) -> None:
        configurations = states = 0
        for n in (1, 2):
            for threshold in range(1, 7):
                for core_increment in range(1, 5):
                    for asset_increments in product(range(1, 5), repeat=n):
                        states += explore(threshold, core_increment,
                                          asset_increments, limit=24)
                        configurations += 1
        self.assertEqual(configurations, 480)
        print(f"\nChecked {configurations} configurations and {states} reachable "
              "states (core time <= 24, fresh-observation over-approximation).",
              flush=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
