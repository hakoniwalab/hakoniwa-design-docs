
import matplotlib.pyplot as plt
import numpy as np
import time

# We will import the necessary components from the existing simulation script.
# This avoids code duplication and keeps the experiment self-contained.
from hakoniwa_time_sim import Core, Asset, Driver

def run_single_experiment(params):
    """
    A wrapper for the existing run_simulation function to extract the final T_c.
    This keeps the original script unmodified.
    If a deadlock occurs, it returns -1.
    """
    core = Core(delta_t=params['core_delta_t'], delta_T=params['core_delta_T'], d_max=params['d_max'])
    # For this experiment, we assume two assets with identical delta_T values
    asset_delta_Ts = [params['asset_delta_T']] * 2
    assets = [Asset(asset_id=i+1, delta_t=params['asset_delta_t_list'][i], delta_T=asset_delta_Ts[i]) for i in range(len(asset_delta_Ts))]
    
    # The wall_time_duration is kept consistent for all runs to ensure comparability
    driver = Driver(core=core, assets=assets, wall_time_duration=1001)
    
    result = driver.run()
    
    # The "effectiveness" is the final simulation time of the core.
    final_Tc = driver.history[-1]['T_c'] if driver.history else 0
    
    print(f"  - Params: (d_max={params['d_max']}, dT_c={params['core_delta_T']}, dT_i={params['asset_delta_T']}) -> Result: {result.upper()}, Final T_c: {final_Tc})")
    
    if result == "deadlocked":
        return -1  # Return sentinel value for deadlock
    return final_Tc

import matplotlib.patches as mpatches

def create_effectiveness_heatmap(delta_tc_values, delta_ti_values, results_grid):
    """
    Generates and saves a heatmap of simulation effectiveness, coloring deadlocks gray
    and highlighting theoretical boundaries.
    """
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Create a masked array to handle deadlocks separately
    masked_grid = np.ma.masked_where(results_grid == -1, results_grid)
    
    # Use a copy of the viridis colormap
    cmap = plt.cm.viridis
    # Set the color for masked values (deadlocks) to gray
    cmap.set_bad(color='gray')
    
    im = ax.imshow(masked_grid, cmap=cmap, origin='lower', interpolation='nearest')

    # Add a color bar to show the effectiveness scale for non-deadlocked cells
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel(r"Simulation Progress (Final $T_c$)", rotation=-90, va="bottom")

    # Set up the axes
    ax.set_xticks(np.arange(len(delta_tc_values)))
    ax.set_yticks(np.arange(len(delta_ti_values)))
    ax.set_xticklabels(delta_tc_values)
    ax.set_yticklabels(delta_ti_values)
    
    ax.set_xlabel(r"Core Time Step ($\Delta T_c$)")
    ax.set_ylabel(r"Asset Time Step ($\Delta T_i$)")
    ax.set_title(r"Simulation Effectiveness Heatmap ($D_{max}=100$) with Liveness Boundaries", fontsize=14)

    # Rotate the tick labels for better readability
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # --- Highlight theoretical boundaries ---
    for i, dt_i in enumerate(delta_ti_values):
        for j, dt_c in enumerate(delta_tc_values):
            # Highlight Divisibility Condition (outer box) - Symmetric
            is_divisible = (dt_i != 0 and dt_c % dt_i == 0) or \
                           (dt_c != 0 and dt_i % dt_c == 0)
            if is_divisible:
                 ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, 
                                           fill=False, edgecolor='cyan', lw=2, linestyle='--'))

            # Highlight General Liveness Boundary: ΔTc + ΔTi = 100 (inner box)
            if dt_c + dt_i == 100:
                ax.add_patch(plt.Rectangle((j - 0.4, i - 0.4), 0.8, 0.8, 
                                           fill=False, edgecolor='orange', lw=2))

    # Add text annotations for the effectiveness values in each cell
    font_size = 4 if len(delta_tc_values) > 15 else 8
    for i in range(len(delta_ti_values)):
        for j, dt_c in enumerate(delta_tc_values):
            value = results_grid[i, j]
            if value == -1:
                text_label = "D"
                text_color = "black"
            else:
                text_label = int(value)
                text_color = "w" if value < 1500 else "black"
            
            text = ax.text(j, i, text_label,
                           ha="center", va="center", color=text_color, fontsize=font_size)

    # --- Add Legend for boundaries ---
    general_proxy = mpatches.Patch(edgecolor='orange', facecolor='none', lw=2, 
                                   label=r'General Liveness Boundary ($\Delta T_c + \Delta T_i = 100$)')
    divisibility_proxy = mpatches.Patch(edgecolor='cyan', facecolor='none', lw=2, linestyle='--', 
                                        label=r'Divisibility Condition ($\Delta T_c \% \Delta T_i = 0$ or $\Delta T_i \% \Delta T_c = 0$)')
    deadlock_proxy = mpatches.Patch(color='gray', label='Deadlock')
    
    ax.legend(handles=[general_proxy, divisibility_proxy, deadlock_proxy], loc='upper center', 
              bbox_to_anchor=(0.5, -0.1), fancybox=True, shadow=True, ncol=3, fontsize='small')

    # Adjust layout to make room for the legend
    fig.subplots_adjust(bottom=0.18)
    
    filename = "effectiveness_heatmap.png"
    plt.savefig(filename)
    print(f"\nHeatmap saved to {filename}")
    plt.close()



def create_asymmetry_heatmap(delta_tc_values, delta_ti_values, asymmetry_grid):
    """
    Generates and saves a heatmap of the asymmetry in simulation effectiveness.
    """
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Use a diverging colormap. Find the max absolute value for symmetric scaling.
    max_abs_val = np.max(np.abs(asymmetry_grid))
    cmap = plt.cm.coolwarm
    
    im = ax.imshow(asymmetry_grid, cmap=cmap, origin='lower', interpolation='nearest',
                   vmin=-max_abs_val, vmax=max_abs_val)

    # Add a color bar
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel("Effectiveness Difference (Row - Column)", rotation=-90, va="bottom")

    # Set up the axes
    ax.set_xticks(np.arange(len(delta_tc_values)))
    ax.set_yticks(np.arange(len(delta_ti_values)))
    ax.set_xticklabels(delta_tc_values)
    ax.set_yticklabels(delta_ti_values)
    
    ax.set_xlabel("Core Time Step (ΔTc)")
    ax.set_ylabel("Asset Time Step (ΔTi)")
    ax.set_title("Asymmetry of Effectiveness\n(Value at (x,y) = Effectiveness(x,y) - Effectiveness(y,x))", fontsize=14)

    # Rotate the tick labels
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Add text annotations
    font_size = 4 if len(delta_tc_values) > 15 else 8
    for i in range(len(delta_ti_values)):
        for j in range(len(delta_tc_values)):
            value = asymmetry_grid[i, j]
            text_color = "black" 
            ax.text(j, i, int(value), ha="center", va="center", color=text_color, fontsize=font_size)

    fig.tight_layout()
    filename = "asymmetry_heatmap.png"
    plt.savefig(filename)
    print(f"\nAsymmetry heatmap saved to {filename}")
    plt.close()


if __name__ == '__main__':
    D_MAX = 100
    # Define the grid of parameters to test
    delta_tc_values = np.arange(5, 101, 5).tolist()
    delta_ti_values = np.arange(5, 101, 5).tolist()
    
    # Initialize a grid to store the results (final T_c)
    effectiveness_grid = np.zeros((len(delta_ti_values), len(delta_tc_values)))

    print("--- Starting Grid Search Experiment ---")
    start_time = time.time()

    for i, dt_i in enumerate(delta_ti_values):
        for j, dt_c in enumerate(delta_tc_values):
            params = {
                "d_max": D_MAX,
                "core_delta_T": dt_c,
                "asset_delta_T": dt_i,
                # These delta_t values are for how often the components check for updates.
                # We keep them small and constant for this experiment.
                "core_delta_t": 10,
                "asset_delta_t_list": [15, 16]
            }
            
            final_tc = run_single_experiment(params)
            effectiveness_grid[i, j] = final_tc
            
    end_time = time.time()
    print(f"\nGrid search completed in {end_time - start_time:.2f} seconds.")

    # Generate and save the main heatmap
    create_effectiveness_heatmap(delta_tc_values, delta_ti_values, effectiveness_grid)

    # --- Create and plot the asymmetry grid ---
    print("\n--- Calculating Asymmetry ---")
    asymmetry_grid = np.zeros_like(effectiveness_grid)
    for i in range(len(delta_ti_values)):
        for j in range(len(delta_tc_values)):
            # Asymmetry = Value(row, col) - Value(col, row)
            # Note: effectiveness_grid is indexed (row, col) which is (i, j)
            # The symmetric point is (j, i)
            asymmetry_grid[i, j] = effectiveness_grid[i, j] - effectiveness_grid[j, i]
    
    create_asymmetry_heatmap(delta_tc_values, delta_ti_values, asymmetry_grid)
