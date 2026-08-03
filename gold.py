import pandas as pd
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.model_selection import train_test_split
from db_connect import get_engine
import matplotlib.pyplot as plt

def build_gold():
    engine = get_engine()
    ## read silver layer from MySQL
    df = pd.read_sql("SELECT shift, stage, oee, jams, downtime, num_stops, planned_downtime FROM silver_shifts", engine)
    ## create binary target - 1 if OEE below 65%, 0 if acceptable
    df["low_oee_flag"] = (df["oee"] < 0.65).astype(int)
    ## Step 1 - define features and target
    features = ["jams", "num_stops", "planned_downtime"]
    X = df[features]
    y = df["low_oee_flag"]
    ## Step 2 - split data into train and test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    ## Step 3 - train the model
    dt = DecisionTreeClassifier(max_depth=4, random_state=42)
    dt.fit(X_train, y_train)
    ## Step 4 - add predictions to df
    df["predicted_flag"] = dt.predict(X)
    df["correct"] = (df["predicted_flag"] == df["low_oee_flag"]).astype(int)
    ## return model and test data for evaluation
    ## Step 5 - write predictions to gold table
    ## to_sql creates the table automatically if it doesn't exist
    ## if_exists="replace" drops and recreates it each time we run
    ## index=False means don't write the pandas row numbers as a column
    df.to_sql("gold_dt_predictions", con=engine, if_exists="replace", index=False)

    ## Step 6 - build feature importance table
    ## feature_importances_ is a sklearn attribute — array of scores summing to 1.0
    ## higher score = that feature had more influence on the Decision Tree splits
    importance_df = pd.DataFrame({
        "feature": features,                          ## column names we trained on
        "importance_score": dt.feature_importances_   ## sklearn scores for each feature
    })

    ## sort so the most important feature appears first
    importance_df = importance_df.sort_values("importance_score", ascending=False)

    ## add a rank column — rank 1 = most important feature for predicting low OEE
    importance_df["rank"] = range(1, len(importance_df) + 1)

    ## write feature importance table to MySQL gold layer
    ## Power BI will use this to show which factors drive low OEE
    importance_df.to_sql("gold_dt_feature_importance", con=engine, if_exists="replace", index=False)
    return dt, X_test, y_test, features

if __name__ == "__main__":
    dt, X_test, y_test, features = build_gold()
    print("Gold layer built successfully")
    ## print model accuracy
    print(f"Accuracy: {dt.score(X_test, y_test):.2f}")
    ## print feature importance
    print(pd.DataFrame({
        "feature": features,
        "importance": dt.feature_importances_
    }).sort_values("importance", ascending=False))
    ## visualize the decision tree
    plt.figure(figsize=(20, 10))
    plot_tree(dt, feature_names=features, class_names=["Good", "Low OEE"], filled=True)
    plt.title("Decision Tree - OEE Below 65%")
    plt.show()