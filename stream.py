import random
import uuid
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

NUM_USERS = 200
START_DATE = "2025-05-01"
END_DATE = "2025-07-31"
PLATFORMS = ["web", "ios", "android"]
EVENT_TYPES = ["login", "play_video", "like", "comment", "logout"]
EVENT_WEIGHTS = {"comment":5, "like":3, "play_video":1, "login":0, "logout":0}
EVENT_PROBS = [0.10, 0.60, 0.15, 0.10, 0.05]
NUM_VIDEOS = 80
MIN_DUR, MAX_DUR = 30, 900
MEAN_EVENTS_PER_DAY = 300

start = pd.to_datetime(START_DATE).date()
end = pd.to_datetime(END_DATE).date()
days = (end - start).days + 1
users = [f"user_{i+1}" for i in range(NUM_USERS)]
videos = [f"video_{i+1}" for i in range(NUM_VIDEOS)]
rows = []

for d in range(days):
    day = start + timedelta(days=d)
    n = np.random.poisson(MEAN_EVENTS_PER_DAY)
    if n < 5:
        n = 5
    for _ in range(n):
        event_id = str(uuid.uuid4())
        user_id = random.choice(users)
        sec = random.randint(0, 86399)
        ts = (datetime.combine(day, datetime.min.time()) + timedelta(seconds=sec)).isoformat()
        platform = random.choices(PLATFORMS, weights=[0.35,0.33,0.32])[0]
        event_type = random.choices(EVENT_TYPES, weights=EVENT_PROBS)[0]
        video_id = None
        watch_time_sec = None
        video_duration_sec = None
        if event_type == "play_video":
            video_id = random.choice(videos)
            dur = int(round(np.random.exponential(scale=180))) + MIN_DUR
            if dur < MIN_DUR:
                dur = MIN_DUR
            if dur > MAX_DUR:
                dur = MAX_DUR
            video_duration_sec = dur
            frac = np.random.beta(2,5)
            watch = int(round(frac * dur))
            if watch < 1:
                watch = 1
            if watch > dur:
                watch = dur
            watch_time_sec = watch
        elif event_type in ("like","comment"):
            if random.random() < 0.85:
                video_id = random.choice(videos)
        rows.append({
            "event_id": event_id,
            "user_id": user_id,
            "timestamp": ts,
            "platform": platform,
            "event_type": event_type,
            "video_id": video_id,
            "watch_time_sec": watch_time_sec,
            "video_duration_sec": video_duration_sec
        })

df = pd.DataFrame(rows).sample(frac=1).reset_index(drop=True)
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["engagement_score"] = df["event_type"].map(EVENT_WEIGHTS).fillna(0).astype(int)
df["watch_time_sec"] = pd.to_numeric(df["watch_time_sec"])
df["video_duration_sec"] = pd.to_numeric(df["video_duration_sec"])
df.to_csv("synthetic_events.csv", index=False)

df["date"] = df["timestamp"].dt.date
grouped = df.groupby(["date","platform"], as_index=False)["engagement_score"].sum().rename(columns={"engagement_score":"engagement_score_sum"})
grouped.to_csv("daily_platform_engagement.csv", index=False)

pivot = grouped.pivot(index="date", columns="platform", values="engagement_score_sum")
pivot = pivot.reindex(columns=["web","ios","android"]).fillna(0)
full_idx = pd.date_range(start=START_DATE, end=END_DATE, freq="D").date
pivot = pivot.reindex(full_idx, fill_value=0)
pivot.index.name = "date"
pivot.to_csv("daily_platform_engagement_wide.csv")

pivot_plot = pivot.copy()
pivot_plot.index = pd.to_datetime(pivot_plot.index)
plt.figure(figsize=(10, max(3, 0.18 * len(pivot_plot))))
sns.heatmap(pivot_plot, cmap="YlOrRd", linewidths=0.3, linecolor="gray", cbar_kws={"label":"Daily engagement score"})
plt.title("Daily Engagement Score by Platform")
plt.xlabel("Platform")
plt.ylabel("Date")
n = len(pivot_plot)
if n <= 15:
    plt.yticks(ticks=np.arange(n)+0.5, labels=[d.strftime("%Y-%m-%d") for d in pivot_plot.index], rotation=0)
else:
    step = max(1, n//12)
    ticks = np.arange(0, n, step) + 0.5
    labels = [pivot_plot.index[i].strftime("%Y-%m-%d") for i in range(0, n, step)]
    plt.yticks(ticks=ticks, labels=labels, rotation=0)
plt.tight_layout()
plt.savefig("engagement_heatmap.png", dpi=200)
plt.show()
