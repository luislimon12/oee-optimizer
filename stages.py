import simpy
import random

NUM_SHIFTS    = 100
SHIFT_MINUTES = 480
IDEAL_CYCLE   = 2.0
NUM_OPERATORS = 4
NUM_REPAIRMEN = 2

class Stage:
    def __init__(self, env, repairmen, operators, name):
        self.env = env
        self.name = name
        self.repairmen = repairmen
        self.operators = operators
        self.units_produced = 0
        self.units_rejected = 0
        self.num_repairs = 0
        self.num_stops = 0
        self.uptime = 0
        self.downtime = 0
        self.planned_downtime = 0
        self.num_planned_stops = 0
        self.num_jams = 0
        self.events = []  ## list to store all events with timestamps

    def run(self):
        while self.env.now < SHIFT_MINUTES:
            yield self.env.timeout(IDEAL_CYCLE)
            self.units_produced += 1
            if random.random() < 0.01:
                self.env.process(self.jam())
            if random.random() < 0.05:
                self.units_rejected += 1
            if random.random() < 0.02:
                self.env.process(self.minor_stop())
            if random.random() < 0.03:
                self.env.process(self.speed_loss())
            if random.random() < 0.002:
                self.env.process(self.cip())
            if random.random() < 0.002:
                self.env.process(self.changeover())

    def jam(self):
        with self.repairmen.request() as request:
            yield request
            start_time = self.env.now
            repair_time = random.randint(2, 60)
            yield self.env.timeout(repair_time)
            self.downtime += repair_time
            self.num_repairs += 1
            self.num_jams += 1
            self.events.append({
                "event_type": "jam",
                "start_time": start_time,
                "end_time": self.env.now,
                "duration": repair_time,
                "severity": "High",
                "resource_used": "repairman"
            })

    def minor_stop(self):
        with self.operators.request() as request:
            yield request
            start_time = self.env.now
            minor_stop = random.uniform(0.1, 2)
            yield self.env.timeout(minor_stop)
            self.downtime += minor_stop
            self.num_stops += 1
            self.events.append({
                "event_type": "minor_stop",
                "start_time": start_time,
                "end_time": self.env.now,
                "duration": minor_stop,
                "severity": "Medium",
                "resource_used": "operator"
            })

    def speed_loss(self):
        start_time = self.env.now
        speed_loss = random.uniform(3.0, 5.0)
        yield self.env.timeout(speed_loss)
        self.downtime += speed_loss
        self.events.append({
            "event_type": "speed_loss",
            "start_time": start_time,
            "end_time": self.env.now,
            "duration": speed_loss,
            "severity": "Low",
            "resource_used": "none"
        })

    def changeover(self):
        start_time = self.env.now
        with self.operators.request() as request:
            yield request
            with self.repairmen.request() as request2:
                yield request2
                changeover_time = random.uniform(15, 45)
                yield self.env.timeout(changeover_time)
                self.planned_downtime += changeover_time
                self.num_planned_stops += 1
                yield from self.speed_loss()
                for _ in range(random.randint(5, 10)):
                    if random.random() < 0.30:
                        self.units_rejected += 1
                self.events.append({
                    "event_type": "changeover",
                    "start_time": start_time,
                    "end_time": self.env.now,
                    "duration": changeover_time,
                    "severity": "Medium",
                    "resource_used": "both"
                })

    def cip(self):
        clean_time = 45
        start_time = self.env.now
        yield self.env.timeout(clean_time)
        self.planned_downtime += clean_time
        self.num_planned_stops += 1
        for _ in range(random.randint(0, 10)):
            if random.random() < 0.30:
                self.units_rejected += 1
        self.events.append({
            "event_type": "cip",
            "start_time": start_time,
            "end_time": self.env.now,
            "duration": 45,
            "severity": "High",
            "resource_used": "planned"
        })

if __name__ == "__main__":
    env = simpy.Environment()
    repairmen = simpy.Resource(env, capacity=NUM_REPAIRMEN)
    operators = simpy.Resource(env, capacity=NUM_OPERATORS)
    stage = Stage(env, repairmen, operators, "Filling")
    env.process(stage.run())
    env.run()
    print(f"{stage.name} - Units Produced: {stage.units_produced}")
    print(f"{stage.name} - Units Rejected: {stage.units_rejected}")
    print(f"{stage.name} - Jams: {stage.num_jams}")
    print(f"{stage.name} - Minor Stops: {stage.num_stops}")
    print(f"{stage.name} - Downtime (min): {stage.downtime}")
    print(f"{stage.name} - Planned Downtime (min): {stage.planned_downtime}")
    print(f"{stage.name} - Planned stops: {stage.num_planned_stops}")
    print(f"{stage.name} - Events logged: {len(stage.events)}")
    print(stage.events[0])