import pandas as pd
from db_connect import get_engine

class Maintenance_min_heap:
    def __init__(self):  ## Initialize a new Maintenance_min_heap object
        self.heap = []          ## empty list to store (ema_score, stage_name) tuples
        self.ema_scores = {}    ## key: stage name, value: ema score
        self.alpha = 0.3        ## smoothing factor for EMA

    def calculate_risk(self, jams, planned_downtime, num_stops):  ## Calculate a weighted maintenance risk score
        jam_norms = jams / 9                             ## normalize jams using max value from bronze_shifts
        planned_downtime_norms = planned_downtime / 177  ## normalize planned downtime using max value
        num_stops_norms = num_stops / 14                 ## normalize num stops using max value
        risk_score = (jam_norms * 0.84) + (planned_downtime_norms * 0.1) + (num_stops_norms * 0.05)  ## apply Decision Tree importance weights
        return risk_score  ## return the calculated risk score

    def update_ema(self, stage, risk_score):  ## Update and return the EMA risk score for a stage
        if stage not in self.ema_scores:  ## check whether this stage has a previous EMA score
            self.ema_scores[stage] = risk_score  ## use current risk as first EMA value — no history yet
        else:  ## stage already has an EMA score
            self.ema_scores[stage] = risk_score * self.alpha + self.ema_scores[stage] * (1 - self.alpha)  ## weighted average of current risk and previous EMA
        return self.ema_scores[stage]  ## return updated EMA so add_stage() can push to heap

    def add_stage(self, stage, jams, planned_downtime, num_stops):  ## tie calculate_risk, update_ema and push together
        risk = self.calculate_risk(jams, planned_downtime, num_stops)  ## Step 1 - calculate risk score from raw metrics
        ema = self.update_ema(stage, risk)                             ## Step 2 - smooth with EMA to account for history
        self.push((ema, stage))                                        ## Step 3 - push (ema_score, stage_name) tuple to heap

    def make_heap(self, values):  ## build heap by inserting each value one at a time — textbook Chapter 6
        for i in range(len(values)):  ## loop through every item in input list
            self.heap.append(values[i])  ## add current item to end of heap
            index = len(self.heap) - 1  ## store index of newly added item
            while index != 0:  ## continue moving item upward until it reaches root
                parent = (index - 1) // 2  ## calculate index of parent node
                if self.heap[index][0] >= self.heap[parent][0]:  ## stop if child score not smaller than parent score
                    break  ## exit bubble-up loop — heap property satisfied
                temp = self.heap[index]          ## temporarily save child item
                self.heap[index] = self.heap[parent]  ## move parent down to child position
                self.heap[parent] = temp         ## move child up to parent position
                index = parent                   ## continue bubbling up from parent position

    def push(self, value):  ## add one value to the min-heap
        self.heap.append(value)  ## add value to end of heap
        index = len(self.heap) - 1  ## store index of newly added value
        while index != 0:  ## continue moving value upward until correctly positioned
            parent = (index - 1) // 2  ## calculate parent index
            if self.heap[index][0] >= self.heap[parent][0]:  ## check if child score >= parent score
                break  ## stop — min-heap property satisfied
            temp = self.heap[index]          ## temporarily save child value
            self.heap[index] = self.heap[parent]  ## move parent value down
            self.heap[parent] = temp         ## move child value up
            index = parent                   ## continue from value's new position

    def pop(self):  ## remove and return the minimum item from the heap
        if not self.heap:  ## check whether heap is empty
            raise IndexError("pop from empty heap")  ## raise error — nothing to remove
        min_value = self.heap[0]  ## save root item — minimum in a valid min-heap
        last = self.heap.pop()    ## remove and save last item in heap
        if self.heap:             ## continue only if items remain after removing last
            self.heap[0] = last   ## move last item to root position
            index = 0             ## start bubbling down from root
            n = len(self.heap)    ## store current number of items
            while True:           ## keep checking children until heap property restored
                smallest = index  ## assume current item is smallest initially
                left = 2 * index + 1   ## calculate left child index
                right = 2 * index + 2  ## calculate right child index
                if left < n and self.heap[left][0] < self.heap[smallest][0]:  ## check if left child smaller
                    smallest = left   ## record left child as smallest position
                if right < n and self.heap[right][0] < self.heap[smallest][0]:  ## check if right child smaller
                    smallest = right  ## record right child as smallest position
                if smallest == index:  ## neither child is smaller
                    break              ## stop — heap property restored
                temp = self.heap[index]               ## temporarily save current item
                self.heap[index] = self.heap[smallest]  ## move smaller child up
                self.heap[smallest] = temp            ## move current item down
                index = smallest                      ## continue bubbling down from new position
        return min_value  ## return the minimum item that was removed

    def peek(self):  ## return minimum item without removing it
        if not self.heap:  ## check whether heap is empty
            raise IndexError("peek from empty heap")  ## raise error — nothing to view
        return self.heap[0]  ## return root item — the minimum

    def __len__(self):  ## define how len() works for this class
        return len(self.heap)  ## return number of items in heap

    def __repr__(self):  ## define printable representation of object
        return f"Maintenance_min_heap({self.heap})"  ## return class name and heap contents

if __name__ == "__main__":
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM bronze_shifts", engine)
    maintenance_heap = Maintenance_min_heap()
    
    ## Step 1 - process all shifts to build EMA history only
    for shift, stage, jams, planned_downtime, num_stops in zip(
        df["shift"], df["stage"], df["jams"],
        df["planned_downtime"], df["num_stops"]):
        risk = maintenance_heap.calculate_risk(jams, planned_downtime, num_stops)
        maintenance_heap.update_ema(stage, risk)  ## update EMA but don't push yet

    ## Step 2 - push final EMA score for each stage once
    for stage, ema_score in maintenance_heap.ema_scores.items():
        maintenance_heap.push((-ema_score, stage))

    ## Step 3 - print top 3 priority stages
    print("Top 3 priority stages for maintenance:")
    for i in range(3):
        ema_score, stage = maintenance_heap.pop()
        print(f"  {i+1}. {stage} — EMA risk score: {-ema_score:.4f}")

    ##step 4- wrtite to results in gold table
    results=[]
    for stage,ema_score in maintenance_heap.ema_scores.items():
        results.append({
            "stage":stage,
            "ema_risk_score":ema_score
        
        })

    results_df=pd.DataFrame(results)
    results_df.to_sql("gold_maintenace_queue",con=engine,if_exists="replace",index=False)
    print(f"Maintenance queue written to my MYSQL - {len(results)} stages")