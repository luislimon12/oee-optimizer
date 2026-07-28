import simpy  # Imports the SimPy library for discrete-event simulation.
import random  # Imports Python's random module for generating random values.
from stages import Stage, NUM_REPAIRMEN, NUM_OPERATORS, SHIFT_MINUTES  # Imports the Stage class and simulation constants.

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
    for stage in [stage1, stage2, stage3]:  # Loops through each stage to print its results.
        print(f"{stage.name} - Units Produced: {stage.units_produced}")  # Prints units produced for the stage.
        print(f"{stage.name} - Units Rejected: {stage.units_rejected}")  # Prints units rejected for the stage.
        print(f"{stage.name} - Jams: {stage.num_jams}")  # Prints the number of jams for the stage.
        print(f"{stage.name} - Minor Stops: {stage.num_stops}")  # Prints the number of minor stops for the stage.
        print(f"{stage.name} - Downtime (min): {stage.downtime}")  # Prints total downtime in minutes.
        print(f"{stage.name} - Planned Downtime (min): {stage.planned_downtime}")  # Prints planned downtime in minutes.
        print(f"{stage.name} - Planned stops: {stage.num_planned_stops}")  # Prints planned stops for the stage.

if __name__ == "__main__":
    run_simulation()
