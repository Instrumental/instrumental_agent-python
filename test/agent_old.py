from instrumental import Agent

a = Agent("4af0fb2451e9d873452d856579a74e7b", collector="localhost:8000", secure=False)
a.gauge("gauge_test", 1)
a.gauge("gauge_test", 2.5, 100, 2)
a.increment("increment_test", 1)
a.increment("increment_test", 2.5, 100, 2)
