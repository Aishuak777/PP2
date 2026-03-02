from datetime import datetime, timedelta

# 1) Subtract five days from current date
now = datetime.now()
five_days_ago = now - timedelta(days=5)

print("Current date:", now)
print("Date minus 5 days:", five_days_ago)


# 2) Print yesterday, today, tomorrow
today = datetime.now()
print("Yesterday:", today - timedelta(days=1))
print("Today:", today)
print("Tomorrow:", today + timedelta(days=1))


# 3) Drop microseconds from datetime
ts = datetime.now()
ts_no_micro = ts.replace(microsecond=0)

print("Original:", ts)
print("Without microseconds:", ts_no_micro)


# 4) Calculate difference between two dates in seconds
start = datetime(2025, 2, 10, 12, 0, 0)
end = datetime(2025, 2, 15, 12, 0, 0)

diff_seconds = (end - start).total_seconds()
print("Difference in seconds:", diff_seconds)