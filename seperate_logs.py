import pandas as pd
import os


df = pd.read_csv("log1.csv", header=None, names=range(8))
df_events = df[df[0] == "event_log"]
df_stats = df[df[0]=="stats_log"]
print(df_events.head())
print(df_stats.head())
df_events.to_csv("event_log.csv", mode='a', header=False)
df_stats.to_csv("stats_log.csv", mode='a', header=False)



