import simpy  # Imports the SimPy library for discrete-event simulation.
import random  # Imports Python's random module for generating random values.
from stages import Stage, NUM_REPAIRMEN, NUM_OPERATORS, SHIFT_MINUTES 
import pandas as pd # Imports the Stage class and simulation constants.
from db_connect import get_connection
def run_simulation():  # Defines the main function that runs the simulation.
    env = simpy.Environment()  # Creates the simulation environment that tracks simulated time.
    repairmen = simpy.Resource(env, capacity=NUM_REPAIRMEN)  # Creates a shared repairmen resource with a fixed capacity.
    operators = simpy.Resource(env, capacity=NUM_OPERATORS)  # Creates a shared operators resource with a fixed capacity.
    stage1 = Stage(env, repairmen, operators, "Filling")  # Creates the Filling stage.
    stage2 = Stage(env, repairmen, operators, "Sealing")  # Creates the Sealing stage.
    stage3 = Stage(env, repairmen, operators, "Packaging")  # Creates the Packaging stage.
    env.process(stage1.run())  # Registers the Filling stage process with the environment.
    env.process(stage2.run())  # Registers the Sealing stage process with the environment.
    env.process(stage3.run())  # Registers the Packaging stage process with the environment.
    env.run(until=SHIFT_MINUTES )  # Runs the simulation until the chosen end time.
    
    return [stage1, stage2, stage3] 

 # Prints planned stops for the stage.

def insert_to_bronze(results):
    conn = get_connection()
    cursor = conn.cursor()
    query = """INSERT INTO bronze_shifts 
               (shift, stage, units_produced, units_rejected, jams,
                num_stops, planned_downtime, planned_num_stops, downtime)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    values = [(r["shift"], r["stage"], r["units_produced"], r["units_rejected"],
               r["jams"], r["num_stops"], r["planned_downtime"], 
               r["planned_num_stops"], r["downtime"]) for r in results]
    cursor.executemany(query, values)
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":

    results = []
    for i in range(100):  ## loop 100 shifts
        stages = run_simulation()  ## run one shift, get 3 stages back
        for stage in stages:  ## loop through each stage
            results.append({
                "shift": i + 1,          ## shift number 1-100
                "stage": stage.name,     ## Filling, Sealing, or Packaging
                "units_produced": stage.units_produced,
                "units_rejected": stage.units_rejected,
                "jams": stage.num_jams,
                "num_stops": stage.num_stops,
                "planned_downtime": stage.planned_downtime,
                "planned_num_stops": stage.num_planned_stops,
                "downtime": stage.downtime
            })

    print(f"Total records collected: {len(results)}")
    print(results[0])  ## print first record to verify
    
    df = pd.DataFrame(results)
    print(df.head())
    print(df.describe())
    insert_to_bronze(results)
    print("Records inserted to MySQL bronze_shifts")