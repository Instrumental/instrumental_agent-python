import os
import sys
import atexit
import logging
import socket
import ssl
import time
import datetime
import re
import string
if sys.version_info[0] < 3:
    from Queue import Queue, Full
else:
    from queue import Queue, Full

from threading import Thread
import pkg_resources


def normalize_time(time_like):
    """Returns unix timestamp integer for all common time/duration formats."""
    if isinstance(time_like, time.struct_time):
        time_like = time.mktime(time_like)
    if isinstance(time_like, datetime.datetime):
        time_like = time.mktime(time_like.utctimetuple())
    if isinstance(time_like, datetime.timedelta):
        time_like = time_like.total_seconds()
    return int(time_like)


def is_valid(metric, value, time, count):
    """Returns True/False if a metric/value/time/count is valid"""
    valid_metric = re.search(r"^([\d\w\-_]+\.)*[\d\w\-_]+$", metric)

    valid_value = re.search(r"^-?\d+(\.\d+)?(e-\d+)?$", str(value))

    if valid_metric and valid_value:
        return True

    # TODO
    # report_invalid_metric(metric) unless valid_metric
    # report_invalid_value(metric, value) unless valid_value
    return False


def is_valid_note(message):
    """Returns True/False if a notice message is valid."""
    return not bool(re.search("[\n\r]", message))


def join(strings, joiner):
    """
    Joins a list of strings together with an interleaved joiner string.
    This is a compatibility function for Python 2/3.
    """
    if sys.version_info[0] < 3:
        return string.join(strings, joiner)
    else:
        return joiner.join(strings)


class Agent(object):
    """
    Used to connect to Instrumental and send metric data.
    """
    backoff = 2
    connect_timeout = 20
    exit_flush_timeout = 5
    hostname = socket.gethostname()
    max_buffer = 5000
    max_reconnect_delay = 15
    exit_timeout = 1
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    version = pkg_resources.get_distribution("instrumental").version
    # reply_timeout = 10

    def __init__(self, api_key, collector="collector.instrumentalapp.com:8001", enabled=True, secure=True, verify_cert=True, synchronous=False):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(Agent.log_format)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

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

        self.pid = None
        self.failures = 0

        if self.enabled:
            self.queue = Queue(Agent.max_buffer)
            self._setup_cleanup_at_exit()

    def gauge(self, metric, value, time=time.time(), count=1):
        """
        Store a gauge for a metric, optionally at a specific time.
        """
        if is_valid(metric, value, time, count):
            self._send_command("gauge", metric, value, normalize_time(time), count)
        # TODO consider return values or at least follow Ruby patterns

    def increment(self, metric, value=1, time=time.time(), count=1):
        """
        Increment a metric, optionally more than one or at a specific time.
        """
        if is_valid(metric, value, time, count):
            self._send_command("increment", metric, value, normalize_time(time), count)
        # TODO consider return values or at least follow Ruby patterns

    def notice(self, note, time=time.time(), duration=0):
        """
        Records a note at a specific time and duration. Useful for things like
        deploys or other significant changes.
        """
        if is_valid_note(note):
            self._send_command("notice", normalize_time(time), normalize_time(duration), note)

    def time(self, metric, fun, multiplier=1):
        """
        Store the execution duration of a function in a metric. Multiplier can
        be used to scale the duration to desired unit or change the duration
        in some meaningful way. Default is in seconds.
        """
        start = time.time()
        value = fun()
        finish = time.time()
        duration = finish - start
        self.gauge(metric, duration * multiplier, start)
        return value

    def time_ms(self, metric, fun):
        """
        Store the execution duration of a function in a metric. Execution time
        is measured in milliseconds.
        """
        return self.time(metric, fun, 1000)

    def is_running(self):
        """Returns True/False if the worker is running"""
        return self._same_pid() and self._worker_alive()

    def _same_pid(self):
        return bool(os.getpid() == self.pid)

    def _worker_alive(self):
        return bool(self.worker) and self.worker.is_alive()

    def _setup_cleanup_at_exit(self):
        self.logger.debug("registering exit handler")
        atexit.register(self._cleanup)

    def _cleanup(self):
        try:
            if self.is_running:
                if self.queue.empty():
                    self.logger.debug("At Exit handler, join skipped, queue empty.")
                else:
                    self.logger.debug("At Exit handler, waiting up to %0.3f seconds (count: %i) ", Agent.exit_timeout, self.queue.qsize())
                    started = time.time()
                    while (time.time() - started) < Agent.exit_timeout and not self.queue.empty():
                        time.sleep(0.05)
                    if self.queue.empty():
                        self.logger.debug("All metrics pushed.")
                    else:
                        self.logger.info("Discarding %i metrics.", self.queue.qsize())
            else:
                self.logger.debug("At Exit handler, join skipped, worker not running.")
        except Exception as error:
            self.logger.error("At Exit ERROR: " + str(error))

    def _start_connection_worker(self):
        if self.enabled:
            # TODO disconnect
            self.pid = os.getpid()
            self.failures = 0
            self.logger.debug("Starting thread...")

            self.worker = Thread(target=self._worker_loop)
            self.worker.setDaemon(True)  # So exit handler won't wait on this
            self.worker.start()

    def _worker_loop(self):
        self.logger.debug("worker starting...")
        while True:
            bare_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            if self.secure:
                # Rely on server to enforce secure protocol/ciphers
                self.socket = ssl.wrap_socket(bare_socket)
            else:
                self.socket = bare_socket

            self.socket.connect((self.host, self.port))
            self.socket.send("hello version=%s agent=python\n" % Agent.version)
            self.socket.send("authenticate %s\n" % self.api_key)

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

    def _send_command(self, cmd, *args):
        if self.enabled:
            args = [str(arg) for arg in args]
            string_cmd = "%s %s\n" % (cmd, join(args, " "))
            if not self.is_running():
                self._start_connection_worker()
            try:
                self.queue.put(string_cmd, False)
            except Full:
                self.logger.debug("Queue full(limit %i), discarding metric", Agent.max_buffer)





# TODO: error handling
# TODO: connection retrying
# TODO: threadsafe init?
