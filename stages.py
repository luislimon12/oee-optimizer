#lets begin doing our simulation for the filler machine
#the 
import simpy
import random
#global constants
NUM_SHIFTS    = 100
SHIFT_MINUTES = 480
IDEAL_CYCLE   = 2.0
NUM_OPERATORS = 4
NUM_REPAIRMEN = 2

"""CLASS Stage:
    INIT takes: env, name, repairmen, operators
        
        store env as self.env
        store name as self.name
        store repairmen as self.repairmen
        store operators as self.operators
        
        set units_produced to 0
        set units_rejected to 0
        set num_repairs to 0
        set num_stops to 0
        set uptime to 0
        set downtime to 0"""

class Stage:
    def __init__(self, env,repairmen,operators,name):
      
      
      self.env=env
      self.name=name
      
      self.repairmen=repairmen
      self.operators=operators
      self.units_produced=0
      self.units_rejected=0
      self.num_repairs=0
      self.num_stops=0
      self.uptime=0
      self.downtime=0

    def run(self):
       
       while self.env.now<SHIFT_MINUTES:
         
         
         #simulate the time to prduce unit
         yield self.env.timeout(IDEAL_CYCLE)
         self.units_produced+=1
         if random.random()<0.02:
           
                   
            self.env.process(self.jam())
         if random.random()<0.05:

            self.units_rejected+=1
         if random.random()<0.02:

            self.env.process(self.minor_stop())

        
          
    def jam(self):
       with self.repairmen.request() as request:
          #wait till resource is available
          yield request
          #create a random repair time
          repair_time=random.randint(2,60) #2-60 minutes
          yield self.env.timeout(repair_time)
          self.downtime+=repair_time
          self.num_stops+=1
          self.num_repairs+=1

    def minor_stop(self):
           with self.operators.request() as request:
              #wait till resource is available
              yield request
              #create a random repair time
              minor_stop=random.uniform(0.1,2) #2-60 minutes
              yield self.env.timeout(minor_stop)
              self.downtime+=minor_stop
              
              self.num_stops+=1

          

        


if __name__ == "__main__":
    ## Only runs this block if we execute the file directly (not when imported)
    
    env = simpy.Environment()
    ## Create the SimPy clock that controls simulation time
    
    repairmen = simpy.Resource(env, capacity=NUM_REPAIRMEN)
    ## Shared repairmen pool — max 2 working at once across all stages
    
    operators = simpy.Resource(env, capacity=NUM_OPERATORS)
    ## Shared operators pool — max 4 working at once across all stages
    
    stage = Stage(env, repairmen, operators, "Filling")
    ## Create one Stage instance named Filling, passing in the clock and resources
    
    env.process(stage.run())
    ## Register the run() method as a SimPy process so the clock can drive it
    
    env.run()
    ## Start the simulation — runs until no more events are left
    
    print(f"{stage.name} - Units Produced: {stage.units_produced}")
    ## Print how many units the Filling stage produced this shift
    
    print(f"{stage.name} - Units Rejected: {stage.units_rejected}")
    print(f"{stage.name} - Units Produced: {stage.units_produced}")

    print(f"{stage.name} - Jams: {stage.num_stops}")
    print(f"{stage.name} - Downtime (min): {stage.downtime}")
    ## Print how many units were rejected
        


      
  

    
      