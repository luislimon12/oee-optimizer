import simpy
import random
from stages import Stage, NUM_REPAIRMEN, NUM_OPERATORS, SHIFT_MINUTES
import pandas as pd
from db_connect import get_connection

def run_simulation():
    env = simpy.Environment()
    repairmen = simpy.Resource(env, capacity=NUM_REPAIRMEN)
    operators = simpy.Resource(env, capacity=NUM_OPERATORS)
    stage1 = Stage(env, repairmen, operators, "Filling")
    stage2 = Stage(env, repairmen, operators, "Sealing")
    stage3 = Stage(env, repairmen, operators, "Packaging")
    env.process(stage1.run())
    env.process(stage2.run())
    env.process(stage3.run())
    env.run(until=SHIFT_MINUTES)
    return [stage1, stage2, stage3]

def collect_events(stages, shift_nums):
    ## create a list to hold all events for this shift
    events = []
    for stage in stages:
        for event in stage.events:
            event["shift"] = shift_nums
            event["stage"] = stage.name
            events.append(event)
    return events

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

def insert_events_to_bronze(all_events, chunk_size=500):
    conn = get_connection()
    cursor = conn.cursor()
    columns = ["shift", "stage", "event_type",
               "start_time", "end_time",
               "duration", "severity", "resource_used"]
    query = """INSERT INTO bronze_events 
               (shift, stage, event_type, start_time, end_time, duration, severity, resource_used)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
    for i in range(0, len(all_events), chunk_size):
        chunk = all_events[i:i + chunk_size]
        values = [tuple(e[col] for col in columns) for e in chunk]
        cursor.executemany(query, values)
        conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    results = []
    all_events = []
    for i in range(100):
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

    print(f"Total records collected: {len(results)}")
    print(f"Total events collected: {len(all_events)}")
    print(results[0])
    df = pd.DataFrame(results)
    print(df.head())
    print(df.describe())
    insert_to_bronze(results)
    insert_events_to_bronze(all_events)
    print("Records inserted to MySQL bronze_shifts and bronze_events")