import pandas as pd
from db_connect import get_engine

def find_min_max_average():
    engine = get_engine()
    df = pd.read_sql("SELECT oee FROM silver_shifts", engine)
    oee_values = df["oee"].tolist()  ## lowercase oee
    
    min = oee_values[0]
    for i in range(1, len(oee_values)):
        if oee_values[i] < min:
            min = oee_values[i]

    max = oee_values[0]
    for i in range(1, len(oee_values)):
        if oee_values[i] > max:
            max = oee_values[i]

    total = 0
    for i in range(len(oee_values)):
        total = total + oee_values[i]
    average = total / len(oee_values)

    print(f"Min OEE: {min:.2f}")
    print(f"Max OEE: {max:.2f}")
    print(f"Average OEE: {average:.2f}")

if __name__ == "__main__":
    find_min_max_average()