import pandas as pd
from simulation import run_simulation, collect_events
from db_connect import get_engine
import matplotlib.pyplot as plt

def scenario_a():
    results = []
    all_events = []

    for i in range(1, 101):
        stages = run_simulation()
        all_events += collect_events(stages, i + 1)
        for stage in stages:
            results.append({
                "shift": i + 1,
                "stage": stage.name,
                "units_produced": stage.units_produced,
                "units_rejected": stage.units_rejected,
                "jams": stage.num_jams,
                "num_stops": stage.num_stops,
                "planned_downtime": stage.planned_downtime,
                "planned_num_stops": stage.num_planned_stops,
                "downtime": stage.downtime
            })

    df = pd.DataFrame(results)
    df["scenario"] = "Baseline"

    ## calculate averages across all shifts
    avg_units = df["units_produced"].mean()
    avg_downtime = df["downtime"].mean()
    avg_stops = df["num_stops"].mean()

    print(f"Baseline — Avg Units: {avg_units:.0f}, Avg Downtime: {avg_downtime:.1f}, Avg Stops: {avg_stops:.1f}")

    return df

def scenario_b():

    
    results = []
    all_events = []
    for i in range(1, 101):
        stages = run_simulation(jam_prob=0.005)  ## only change
        all_events += collect_events(stages, i + 1)
        for stage in stages:
            results.append({"shift": i + 1,
                            "stage": stage.name,
                            "units_produced": stage.units_produced,
                            "units_rejected": stage.units_rejected,
                            "jams": stage.num_jams,
                            "num_stops": stage.num_stops,
                            "planned_downtime": stage.planned_downtime,
                            "planned_num_stops": stage.num_planned_stops,
                            "downtime": stage.downtime})
    df = pd.DataFrame(results)
    df["scenario"] = "Reduced Jams"
    avg_units = df["units_produced"].mean()
    avg_downtime = df["downtime"].mean()
    print(f"Reduced Jams — Avg Units: {avg_units:.0f}, Avg Downtime: {avg_downtime:.1f}")
    return df


def scenario_c():

    
    results = []
    all_events = []
    for i in range(1, 101):
        stages = run_simulation(peak_only=True)  
        all_events += collect_events(stages, i + 1)
        for stage in stages:
            results.append({"shift": i + 1,
                            "stage": stage.name,
                            "units_produced": stage.units_produced,
                            "units_rejected": stage.units_rejected,
                            "jams": stage.num_jams,
                            "num_stops": stage.num_stops,
                            "planned_downtime": stage.planned_downtime,
                            "planned_num_stops": stage.num_planned_stops,
                            "downtime": stage.downtime})
    df = pd.DataFrame(results)
    df["scenario"] = "Off-Peak Scheduling"
    avg_units = df["units_produced"].mean()
    avg_downtime = df["downtime"].mean()
    print(f"Off-Peak Scheduling — Avg Units: {avg_units:.0f}, Avg Downtime: {avg_downtime:.1f}")
    return df

def compare_scenarios():
    df_a = scenario_a()
    print("Running Scenario A - Baseline...")
    df_b = scenario_b()
    print("Running Scenario B - Reduced Jams...")
    df_c = scenario_c()
    print("Running Scenario C - Off-Peak Scheduling...")

    df_all = pd.concat([df_a, df_b, df_c], ignore_index=True)

    engine = get_engine()
    df_all.to_sql("gold_scenarios", con=engine, if_exists="replace", index=False)
    print(f"Scenarios written to MySQL — {len(df_all)} rows")

    ## summarize by scenario
    summary = df_all.groupby("scenario")[["units_produced", "downtime"]].mean()
    print(summary)

    ## calculate minutes saved vs baseline
    summary["downtime_saved"] = summary.loc["Baseline", "downtime"] - summary["downtime"]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    ## left — avg units produced
    summary["units_produced"].plot(kind="bar", ax=axes[0], color=["blue", "green", "orange"])
    axes[0].set_title("Avg Units Produced by Scenario")
    axes[0].set_ylabel("Units")
    axes[0].tick_params(axis='x', rotation=45)

    ## right — minutes saved vs baseline
    summary["downtime_saved"].plot(kind="bar", ax=axes[1], color=["blue", "green", "orange"])
    axes[1].set_title("Minutes Saved vs Baseline")
    axes[1].set_ylabel("Minutes Saved")
    axes[1].tick_params(axis='x', rotation=45)

    plt.suptitle("Scenario Analysis — OEE Optimizer")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    compare_scenarios()