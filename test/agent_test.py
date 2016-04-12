from instrumental import Agent
import re

def test_should_increment():
    a = Agent("56c08a1a5b25ed2425b6dce7700edae5", collector="localhost:8000", secure=False)
    a.increment("python.increment")
    assert(a.queue.qsize()) == 1
    expected_message = re.compile('.*(increment python.increment 1 \d{10} 1).*')
    match = expected_message.match(str(a.queue.queue))
    assert match, "expected increment to be in queue, instead have {0}".format(a.queue.queue)

def test_should_gauge():
    a = Agent("56c08a1a5b25ed2425b6dce7700edae5", collector="localhost:8000", secure=False)
    a.gauge("python.gauge", 5)
    assert(a.queue.qsize()) == 1
    expected_message = re.compile('.*(gauge python.gauge 5 \d{10} 1).*')
    match = expected_message.match(str(a.queue.queue))
    assert match, "expected gauge to be in queue, instead have {0}".format(a.queue.queue)

def test_should_send_notice():
    a = Agent("56c08a1a5b25ed2425b6dce7700edae5", collector="localhost:8000", secure=False)
    a.notice("Python Agent Test Is Running")
    assert(a.queue.qsize()) == 1
    expected_message = re.compile('.*(notice \d{10} 0 Python Agent Test Is Running).*')
    match = expected_message.match(str(a.queue.queue))
    assert match, "expected gauge to be in queue, instead have {0}".format(a.queue.queue)
