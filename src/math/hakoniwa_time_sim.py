

import matplotlib.pyplot as plt
import numpy as np
from abc import ABC, abstractmethod
import math

class TimeAwareComponent(ABC):
    """An abstract base class for components with simulation time."""
    def __init__(self, component_id: str, delta_t: int, delta_T: int):
        self.id = component_id
        self.delta_t = delta_t
        self.delta_T = delta_T
        self.T = 0

    @abstractmethod
    def count_up(self, *args, **kwargs) -> bool:
        pass

class Asset(TimeAwareComponent):
    """Represents a single asset (simulator)."""
    def __init__(self, asset_id: int, delta_t: int, delta_T: int):
        super().__init__(component_id=f"Asset-{asset_id}", delta_t=delta_t, delta_T=delta_T)

    def count_up(self, core_time: int) -> bool:
        T_i_prime = self.T + self.delta_T
        if T_i_prime <= core_time:
            self.T = T_i_prime
            return True
        return False

class Core(TimeAwareComponent):
    """Represents the Core, the central time coordinator."""
    def __init__(self, delta_t: int, delta_T: int, d_max: int):
        super().__init__(component_id="Core", delta_t=delta_t, delta_T=delta_T)
        self.d_max = d_max

    def count_up(self, asset_times: list[int]) -> bool:
        if not asset_times:
            return False
        T_c_prime = self.T + self.delta_T
        max_delay_prime = max(T_c_prime - t_i for t_i in asset_times)
        if max_delay_prime <= self.d_max:
            self.T = T_c_prime
            return True
        return False

class Driver:
    """Orchestrates the simulation and detects deadlocks."""
    def __init__(self, core: Core, assets: list[Asset], wall_time_duration: int):
        self.core = core
        self.assets = assets
        self.wall_time_duration = wall_time_duration
        self.history = []

    def run(self):
        """
        Runs the simulation loop.
        """
        stall_counter = 0
        all_delta_t = [self.core.delta_t] + [a.delta_t for a in self.assets]
        deadlock_threshold = 2 * max(all_delta_t) if all_delta_t else 1

        for t in range(self.wall_time_duration):
            total_T_before = self.core.T + sum(a.T for a in self.assets)
            
            for asset in self.assets:
                if t > 0 and t % asset.delta_t == 0:
                    asset.count_up(self.core.T)

            if t > 0 and t % self.core.delta_t == 0:
                asset_times = [asset.T for asset in self.assets]
                self.core.count_up(asset_times)

            total_T_after = self.core.T + sum(a.T for a in self.assets)
            if total_T_after <= total_T_before and t > 0:
                stall_counter += 1
            else:
                stall_counter = 0

            self.history.append({'t': t, 'T_c': self.core.T, 'T_i': {a.id: a.T for a in self.assets}})

            if stall_counter > deadlock_threshold:
                return "deadlocked"
        return "completed"

def plot_on_axes(ax, history, assets, title, params):
    """Plots simulation history and parameters on a given matplotlib Axes object."""
    if not history:
        ax.text(0.5, 0.5, "No history to plot.", ha='center', va='center')
        return

    t = [h['t'] for h in history]
    T_c = [h['T_c'] for h in history]
    
    T_i_data = {asset.id: [] for asset in assets}
    for h in history:
        for asset_id, asset_time in h['T_i'].items():
            if asset_id in T_i_data:
                T_i_data[asset_id].append(asset_time)

    core_label = fr'Core ($T_c$)  [$\Delta T_c={params["core_delta_T"]}$, $D_{{max}}={params["d_max"]}$]'
    ax.plot(t, T_c, label=core_label, color='red', linewidth=2, drawstyle='steps-post')

    for i, (asset_id, T_i) in enumerate(T_i_data.items()):
        asset_label = fr'Asset {i+1} ($T_{i+1}$)  [$\Delta T_i={params["asset_delta_Ts"][i]}$]'
        ax.plot(t, T_i, label=asset_label, linestyle='--', drawstyle='steps-post')

    ax.set_xlabel("Wall Time (t)")
    ax.set_ylabel("Simulation Time (T)")
    ax.set_title(title, fontsize=14)
    ax.legend(loc='best')
    ax.grid(True)
    ax.set_xlim(0, 200)
    ax.set_ylim(0, 3000)

def run_and_get_driver(params):
    """Sets up and runs a single simulation, returning the driver."""
    core = Core(delta_t=params['core_delta_t'], delta_T=params['core_delta_T'], d_max=params['d_max'])
    assets = [Asset(asset_id=i+1, delta_t=params['asset_delta_t_list'][i], delta_T=params['asset_delta_Ts'][i]) for i in range(len(params['asset_delta_Ts']))]
    driver = Driver(core=core, assets=assets, wall_time_duration=201)
    result = driver.run()
    return driver, assets, result


if __name__ == '__main__':
    cases = {
        "Case 1": {
            "title": "Case 1: Liveness Condition Met",
            "d_max": 200, "core_delta_T": 100, "asset_delta_Ts": [80, 70],
            "core_delta_t": 10, "asset_delta_t_list": [15, 16]
        },
        "Case 8": {
            "title": "Case 8: Liveness Condition Violated",
            "d_max": 120, "core_delta_T": 120, "asset_delta_Ts": [60, 41],
            "core_delta_t": 10, "asset_delta_t_list": [15, 16]
        },
        "Case 5": {
            "title": "Case 5: Divisibility Avoids Deadlock",
            "d_max": 170, "core_delta_T": 120, "asset_delta_Ts": [60, 40],
            "core_delta_t": 10, "asset_delta_t_list": [15, 16]
        }
    }

    fig, axes = plt.subplots(len(cases), 1, figsize=(12, 21))
    fig.suptitle('Comparison of Liveness Condition Scenarios', fontsize=16)

    for i, (case_name, params) in enumerate(cases.items()):
        print(f"--- Running {case_name} ---")
        driver, assets, result = run_and_get_driver(params)
        title_with_result = f"{params['title']} ({result.upper()})"
        plot_on_axes(axes[i], driver.history, assets, title_with_result, params)

    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    
    output_filename = "liveness_comparison_with_params.png"
    plt.savefig(output_filename)
    print(f"\nComparison plot saved to {output_filename}")
    plt.close()

