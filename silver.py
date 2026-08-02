import pandas as pd

from db_connect import get_connection, get_engine

def build_silver():
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM bronze_shifts", engine)
    
    df["availability"] = (480 - df["downtime"]) / 480
    df["performance"] = df["units_produced"] / 240
    df["quality"] = (df["units_produced"] - df["units_rejected"]) / df["units_produced"]
    df["oee"] = df["availability"] * df["performance"] * df["quality"]
    
    df.to_sql("silver_shifts", con=engine, if_exists="replace", index=False)
if __name__ == "__main__":
    build_silver()
    print("Silver layer built successfully")
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM silver_shifts LIMIT 5", engine)
   

    print(df[["shift", "stage", "availability", "performance", "quality", "oee"]])