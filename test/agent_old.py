from instrumental import Agent
import time
from datetime import datetime, timedelta

a = Agent("4af0fb2451e9d873452d856579a74e7b", collector="localhost:8000", secure=False)
a.gauge("gauge_test", 1)
a.gauge("gauge_test", 2.5, 100, 2)
a.increment("increment_test", 1)
a.increment("increment_test", 2.5, 100, 2)
a.increment("increment_test", 2.5, time.time())
a.increment("increment_test", 2.5, datetime.now())
a.notice("z", 1, 2)
a.notice("z", time.time())
a.notice("z", datetime.now() - timedelta(minutes=5), timedelta(minutes=2))

def slowFunction(x):
    time.sleep(0.1)
    return x * 2

# should call function
# should return value
# should track metric
x = 5
print(" 5 * 2 = " + str(a.time("time_test", lambda: slowFunction(x))))

# should not be blocking
for i in range(Agent.max_buffer + 1):
  a.increment("z")
