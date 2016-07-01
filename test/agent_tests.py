from instrumental_agent import Agent
import re
import timeit
import time
import datetime
import calendar

def test_should_increment():
    a = Agent("56c08a1a5b25ed2425b6dce7700edae5", collector="localhost:8000", secure=False)
    a.increment("python.increment")
    assert(a.queue.qsize()) == 1
    expected_message = re.compile('.*(increment python.increment 1 \d{10} 1).*')
    match = expected_message.match(str(a.queue.queue))
    assert match, "expected increment to be in queue, instead have {0}".format(a.queue.queue)

def test_should_increment_with_integer_time():
    a = Agent("56c08a1a5b25ed2425b6dce7700edae5", collector="localhost:8000", secure=False)
    a.increment("python.increment")
    assert(a.queue.qsize()) == 1
    expected_message = re.compile('.*(increment python.increment 1 \d{10} 1).*')
    match = expected_message.match(str(a.queue.queue))
    assert match, "expected increment to be in queue, instead have {0}".format(a.queue.queue)

def test_should_increment_with_time():
    a = Agent("56c08a1a5b25ed2425b6dce7700edae5", collector="localhost:8000", secure=False)
    now = time.time()
    a.increment("python.increment", 1, now)
    assert(a.queue.qsize()) == 1
    expected_message = re.compile('.*(increment python.increment 1 %i 1).*' % int(now))
    match = expected_message.match(str(a.queue.queue))
    assert match, "expected increment to be in queue, instead have {0}".format(a.queue.queue)

def test_should_increment_with_datetime():
    a = Agent("56c08a1a5b25ed2425b6dce7700edae5", collector="localhost:8000", secure=False)
    now = datetime.datetime.utcnow()
    expected_timestamp = calendar.timegm(now.utctimetuple())
    a.increment("python.increment", 1, now)
    assert(a.queue.qsize()) == 1
    expected_message = re.compile('.*(increment python.increment 1 %i 1).*' % expected_timestamp)
    match = expected_message.match(str(a.queue.queue))
    assert match, "expected increment to be in queue, instead have {0}".format(a.queue.queue)

def test_should_increment_with_struct_time():
    a = Agent("56c08a1a5b25ed2425b6dce7700edae5", collector="localhost:8000", secure=False)
    a.increment("python.increment", 1, time.localtime(123))
    assert(a.queue.qsize()) == 1
    expected_message = re.compile('.*(increment python.increment 1 %i 1).*' % 123)
    match = expected_message.match(str(a.queue.queue))
    assert match, "expected increment to be in queue, instead have {0}".format(a.queue.queue)

def test_not_should_increment_with_invalid_metric():
    a = Agent("56c08a1a5b25ed2425b6dce7700edae5", collector="localhost:8000", secure=False)
    a.increment("bad metric")
    a.increment(" badmetric")
    a.increment("badmetric ")
    a.increment("bad(metric")
    assert(a.queue.qsize()) == 0

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
    assert match, "expected notice to be in queue, instead have {0}".format(a.queue.queue)

def test_should_send_notice_with_integer_time_and_duration():
    a = Agent("56c08a1a5b25ed2425b6dce7700edae5", collector="localhost:8000", secure=False)
    a.notice("Python Agent Test Is Running", 5, 10)
    assert(a.queue.qsize()) == 1
    expected_message = re.compile('.*(notice 5 10 Python Agent Test Is Running).*')
    match = expected_message.match(str(a.queue.queue))
    assert match, "expected gauge to be in queue, instead have {0}".format(a.queue.queue)

def test_should_send_notice_with_time_time():
    a = Agent("56c08a1a5b25ed2425b6dce7700edae5", collector="localhost:8000", secure=False)
    now = time.time()
    a.notice("Python Agent Test Is Running", now, 10)
    assert(a.queue.qsize()) == 1
    expected_message = re.compile('.*(notice %i 10 Python Agent Test Is Running).*' % int(now))
    match = expected_message.match(str(a.queue.queue))
    assert match, "expected gauge to be in queue, instead have {0}".format(a.queue.queue)

def test_should_send_notice_with_struct_time():
    a = Agent("56c08a1a5b25ed2425b6dce7700edae5", collector="localhost:8000", secure=False)
    a.notice("Python Agent Test Is Running", time.localtime(1), 10)
    assert(a.queue.qsize()) == 1
    expected_message = re.compile('.*(notice %i 10 Python Agent Test Is Running).*' % 1)
    match = expected_message.match(str(a.queue.queue))
    assert match, "expected gauge to be in queue, instead have {0}".format(a.queue.queue)

def test_should_send_notice_with_datetime():
    a = Agent("56c08a1a5b25ed2425b6dce7700edae5", collector="localhost:8000", secure=False)
    now = datetime.datetime.utcnow()
    expected_timestamp = calendar.timegm(now.utctimetuple())
    a.notice("Python Agent Test Is Running", now, 10)
    assert(a.queue.qsize()) == 1
    expected_message = re.compile('.*(notice %i 10 Python Agent Test Is Running).*' % expected_timestamp)
    match = expected_message.match(str(a.queue.queue))
    assert match, "expected gauge to be in queue, instead have {0}".format(a.queue.queue)

def test_should_send_notice_with_integer_time_and_timedelta_duration():
    a = Agent("56c08a1a5b25ed2425b6dce7700edae5", collector="localhost:8000", secure=False)
    a.notice("Python Agent Test Is Running", 123, datetime.timedelta(minutes=10))
    assert(a.queue.qsize()) == 1
    expected_message = re.compile('.*(notice 123 600 Python Agent Test Is Running).*')
    match = expected_message.match(str(a.queue.queue))
    assert match, "expected gauge to be in queue, instead have {0}".format(a.queue.queue)

def test_should_not_send_notice_with_invalid_message():
    a = Agent("56c08a1a5b25ed2425b6dce7700edae5", collector="localhost:8000", secure=False)
    a.notice("Bad\nNotice")
    a.notice("Bad\rNotice")
    assert(a.queue.qsize()) == 0

def test_should_not_block():
    a = Agent("56c08a1a5b25ed2425b6dce7700edae5", collector="localhost:8000", secure=False)
    for i in range(Agent.max_buffer + 1):
        assert timeit.timeit(lambda: a.increment("z"), number=1) < 0.01

def test_time_should_return_original_return_value():
    a = Agent("56c08a1a5b25ed2425b6dce7700edae5", collector="localhost:8000", secure=False)
    assert a.time("timer", lambda: 1 + 2) == 3

def test_time_should_record_time():
    a = Agent("56c08a1a5b25ed2425b6dce7700edae5", collector="localhost:8000", secure=False)
    a.time("timer", lambda: time.sleep(0.1))
    expected_message = re.compile('.*(gauge timer 0.1\d+ ).*')
    match = expected_message.match(str(a.queue.queue))
    assert match, "expected gauge to be in queue, instead have {0}".format(a.queue.queue)
