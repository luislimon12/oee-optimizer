# Production Line OEE Optimization Simulator

## Overview
A discrete-event simulation of a food production line built with Python and SimPy. 
Simulates 100 shifts across 3 parallel stages (Filling, Sealing, Packaging), generates 
realistic production events, and stores results in a MySQL medallion architecture 
(Bronze → Silver → Gold). Machine learning and data structures are applied to answer 
5 business questions relevant to food manufacturing operations.

## Business Context
tracks OEE-style metrics and runs 
a Fuel for Growth initiative around capacity utilization. This project demonstrates 
how data science can translate simulation data into actionable maintenance decisions.

## 5 Business Questions
1. What conditions drive OEE below 65%? — Decision Tree Classifier
2. Are there distinct shift performance patterns? — K-Means Clustering
3. Which downtime events hurt peak production most? — IntervalTree
4. How many units are lost to poor maintenance timing? — Scenario Analysis
5. When should preventive maintenance be triggered? — Min-Heap Priority Queue

## Tech Stack
Python | SimPy | MySQL | pandas | PySpark | Scikit-learn | NetworkX | Power BI

## Project Structure
