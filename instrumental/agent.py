import os, sys, atexit
from logging import Logger
import logging
import socket, ssl
import time, datetime, re, string


import sys
if sys.version_info[0] < 3:
    from Queue import Queue, Full
else:
    from queue import Queue, Full

from threading import Thread

class Agent:
    """
    """
    # TODO: other variables
    backoff = 2
    connect_timeout = 20
    exit_flush_timeout = 5
    hostname = socket.gethostname()
    max_buffer = 5000
    max_reconnect_delay = 15
    exit_timeout = 1
    # reply_timeout = 10

    def __init__(self, api_key, collector="collector.instrumentalapp.com:8001", enabled = True, secure = True, verify_cert = True, synchronous = False):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

        ch = logging.StreamHandler(sys.stderr)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

        self.logger.debug("Initializing...")

        self.api_key = api_key
        self.host, self.port = collector.split(":")
        self.port = int(self.port)
        self.secure = secure
        self.verify_cert = verify_cert
        self.enabled = enabled
        self.synchronous = synchronous
        self.worker = False
        self.socket = False

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)



        if self.enabled:
            self.queue = Queue(Agent.max_buffer)
            self.setup_cleanup_at_exit()

    def setup_cleanup_at_exit(self):
        self.logger.debug("registering exit handler")
        atexit.register(self.cleanup)


    def cleanup(self):
        try:
            if self.worker and self.worker.is_alive:
                if self.queue.empty():
                    self.logger.debug("At Exit handler, join skiped, worker not running. Discarded %i metrics", self.queue.qsize())
                else:
                    self.logger.debug("At Exit handler, waiting up to %0.3f seconds (count: %i) " % (Agent.exit_timeout, self.queue.qsize()))
                    started = time.time()
                    while (time.time() - started) < Agent.exit_timeout and not self.queue.empty():
                        time.sleep(0.05)
                    if self.queue.empty():
                        self.logger.debug("All metrics pushed.")
                    else:
                        self.logger.info("Discarding %i metrics." % self.queue.qsize())
            else:
                self.logger.debug("At Exit handler, join skiped, worker not running.")
        except Exception as error:
            self.logger.error("At Exit ERROR: " + str(error))




    # TODO consider return values or at least follow Ruby patterns
    def gauge(self, metric, value, time = time.time(), count = 1):
        if self.is_valid(metric, value, time, count):
            self.send_command("gauge", metric, value, self.normalize_time(time), count)

    # TODO consider return values or at least follow Ruby patterns
    def increment(self, metric, value = 1, time = time.time(), count = 1):
        if self.is_valid(metric, value, time, count):
            self.send_command("increment", metric, value, self.normalize_time(time), count)

    def notice(self, note, time = time.time(), duration = 0):
      if self.is_valid_note(note):
        self.send_command("notice", self.normalize_time(time), self.normalize_time(duration), note)

    def is_running(self):
        return bool(self.worker) and bool(os.getpid() == self.pid)

    def start_connection_worker(self):
        if self.enabled:
            # TODO disconnect
            self.pid = os.getpid()
            self.failures = 0
            self.logger.debug("Starting thread...")

            self.worker = Thread(target=self.worker_loop)
            self.worker.setDaemon(True) # Must be set or exit handler will not be called if this thread is alive
            self.worker.start()


    def worker_loop(self):
        self.logger.debug("worker starting...")
        while True:
            bare_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            if self.secure:
                # No SSL options required as server enforces only secure protocol/ciphers
                self.socket = ssl.wrap_socket(bare_socket)
            else:
                self.socket = bare_socket

            self.socket.connect((self.host, self.port))
            self.socket.send("hello version=0.0.1 agent=python\nauthenticate %s\n" % self.api_key)

            data = ""
            ok_count = 0
            receiving = True
            connected = False
            while receiving:
                data += self.socket.recv(1024)
                while "\n" in data:
                    self.logger.debug("initial data: %s" % repr(data))
                    response, data = data.split("\n", 1)
                    self.logger.debug("  response: %s" % repr(response))
                    self.logger.debug("  data: %s" % repr(data))
                    if response == "ok":
                        ok_count += 1
                        if ok_count >= 2:
                            self.logger.debug("auth a-ok")
                            receiving = False
                            connected = True
                            break
                    else:
                        self.logger.debug("auth failed...")
                        break
            if connected:
                while True:
                    item = self.queue.get()
                    self.socket.send(item)
                    self.queue.task_done()



    def send_command(self, cmd, *args):
        if self.enabled:
            string_cmd = "%s %s\n" % (cmd, self.join_strings(map(lambda a: str(a), args), " "))
            if not self.is_running():
                self.start_connection_worker()
            try:
                self.queue.put(string_cmd, False)
            except Full:
                self.logger.debug("Queue full(limit %i), discarding metric" % Agent.max_buffer)



    def is_valid(self, metric, value, time, count):
        valid_metric = re.search("^([\d\w\-_]+\.)*[\d\w\-_]+$", metric, re.IGNORECASE)

        valid_value = re.search("^-?\d+(\.\d+)?(e-\d+)?$", str(value))

        if valid_metric and valid_value:
            return True

        # TODO
        # report_invalid_metric(metric) unless valid_metric
        # report_invalid_value(metric, value) unless valid_value
        return False



    def is_valid_note(self, note):
        return not bool(re.search("[\n\r]", note))

    def time(self, metric, fun, multiplier = 1):
        start = time.time()
        value = fun()
        finish = time.time()
        duration = finish - start
        self.gauge(metric, duration * multiplier, start)
        return value

    def time_ms(self, metric, fun):
        return self.time(fun, 1000)

    def join_strings(self, strings, joiner):
        if sys.version_info[0] < 3:
            return string.join(strings, joiner)
        else:
            return joiner.join(strings)

    # Returns unix timestamp integer for all common time/duration formats.
    def normalize_time(self, time_like):
        if isinstance(time_like, datetime.datetime):
            time_like = time.mktime(time_like.utctimetuple())
        if isinstance(time_like, datetime.timedelta):
            time_like = time_like.total_seconds()
        return int(time_like)



# TODO: error handling
# TODO: connection retrying
# TODO: threadsafe init?

