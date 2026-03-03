
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

def run_simulation(params):
    """Sets up and runs a single simulation, returning the history and result."""
    core = Core(delta_t=params['core_delta_t'], delta_T=params['core_delta_T'], d_max=params['d_max'])
    assets = [Asset(asset_id=i+1, delta_t=params['asset_delta_t_list'][i], delta_T=params['asset_delta_Ts'][i]) for i in range(len(params['asset_delta_Ts']))]
    driver = Driver(core=core, assets=assets, wall_time_duration=201)
    result = driver.run()
    final_Tc = driver.history[-1]['T_c'] if driver.history else 0
    print(f"  - Result: {result.upper()}, Final T_c: {final_Tc}")
    return driver.history, result

def plot_overlay(title, filename, settings_data):
    """Plots an overlay of multiple simulation histories."""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    colors = ['blue', 'red', 'green']
    
    param_texts = []
    for i, (setting_name, data) in enumerate(settings_data.items()):
        history = data['history']
        params = data['params']
        result = data['result']
        color = colors[i % len(colors)]
        
        t = [h['t'] for h in history]
        T_c = [h['T_c'] for h in history]
        
        # Plot Core line
        core_label = f'{setting_name} Core ({result.upper()})'
        ax.plot(t, T_c, label=core_label, color=color, linewidth=2, drawstyle='steps-post')
        
        # Plot Asset lines
        # Collect all asset IDs for this setting
        asset_ids_in_setting = sorted(list(data['history'][0]['T_i'].keys()))

        linestyles = [':', '-.', 'dashdot']  # Different linestyles for assets
        
        for asset_id in asset_ids_in_setting:
            T_i_values = [h['T_i'][asset_id] for h in history]
            asset_label = f'{setting_name} Asset {asset_id.split("-")[1]}'
            ax.plot(t, T_i_values, label=asset_label, color=color, linestyle=linestyles[(int(asset_id.split("-")[1]) + 1) % len(linestyles)], drawstyle='steps-post')
        
        param_text = r"%s: $D_{max}=%d, \Delta T_c=%d, \Delta T_i=%s$" % (
            setting_name,
            params["d_max"],
            params["core_delta_T"],
            str(params["asset_delta_Ts"])
        )
        param_texts.append(param_text)

    ax.set_xlabel("Wall Time (t)")
    ax.set_ylabel("Simulation Time (T)")
    ax.set_title(title, fontsize=14)
    ax.legend(loc='upper left', fontsize=8) # Reduced font size for legend
    ax.grid(True)
    ax.set_xlim(0, 200)
    ax.set_ylim(0, 2000)
    
    full_param_text = "\n".join(param_texts)
    ax.text(0.98, 0.98, full_param_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    plt.savefig(filename)
    print(f"\nPlot saved to {filename}")
    plt.close()


if __name__ == '__main__':
    safest_settings = {
        "Setting 1.1": {
            "d_max": 200, "core_delta_T": 100, "asset_delta_Ts": [80, 70], "core_delta_t": 10, "asset_delta_t_list": [15, 16]
        },
        "Setting 1.2": {
            "d_max": 150, "core_delta_T": 80, "asset_delta_Ts": [50, 40], "core_delta_t": 10, "asset_delta_t_list": [15, 16]
        },
        "Setting 1.3": {
            "d_max": 300, "core_delta_T": 150, "asset_delta_Ts": [100, 120], "core_delta_t": 10, "asset_delta_t_list": [15, 16]
        }
    }

    unstable_settings = {
        "Setting 2.1": {
            "d_max": 170, "core_delta_T": 120, "asset_delta_Ts": [60, 41], "core_delta_t": 10, "asset_delta_t_list": [15, 16]
        },
        "Setting 2.2": {
            "d_max": 185, "core_delta_T": 100, "asset_delta_Ts": [90, 85], "core_delta_t": 10, "asset_delta_t_list": [15, 16]
        },
        "Setting 2.3": {
            "d_max": 120, "core_delta_T": 120, "asset_delta_Ts": [60, 41], "core_delta_t": 10, "asset_delta_t_list": [15, 16]
        }
    }

    divisibility_settings = {
        "Setting 3.1": {
            "d_max": 170, "core_delta_T": 120, "asset_delta_Ts": [60, 40], "core_delta_t": 10, "asset_delta_t_list": [15, 16]
        },
        "Setting 3.2": {
            "d_max": 140, "core_delta_T": 100, "asset_delta_Ts": [50, 25], "core_delta_t": 10, "asset_delta_t_list": [15, 16]
        },
        "Setting 3.3": {
            "d_max": 200, "core_delta_T": 150, "asset_delta_Ts": [75, 50], "core_delta_t": 10, "asset_delta_t_list": [15, 16]
        }
    }

    all_categories = {
        "safest_cases": {"title": "Safest Cases (General Liveness Condition Met)", "settings": safest_settings},
        "unstable_cases": {"title": "Unstable Cases (Violates Liveness Conditions)", "settings": unstable_settings},
        "divisibility_cases": {"title": "Divisibility Rule Cases (Violates General, Meets Divisibility)", "settings": divisibility_settings}
    }

    for category_name, category_data in all_categories.items():
        print(f"\n--- Generating plot for: {category_data['title']} ---")
        results_data = {}
        for setting_name, params in category_data['settings'].items():
            print(f" Running {setting_name}...")
            history, result = run_simulation(params)
            results_data[setting_name] = {"history": history, "params": params, "result": result}
        
        plot_overlay(
            title=category_data['title'],
            filename=f"{category_name}.png",
            settings_data=results_data
        )
