#!/usr/bin/env python

__author__ = "Patrick Godwin (patrick.godwin@ligo.org)"
__description__ = "a module to store the application instance"

#-------------------------------------------------
### imports

import logging
import signal
import sys
import timeit
import threading

from confluent_kafka import Consumer, KafkaError

from . import utils


#-------------------------------------------------
### classes

class App(object):
    """Implements a Kafka application for event processing.

    Parameters
    ----------
    name : `str`
        the name of the application instance
    broker :  `str`
        the Kafka broker to connect to
    num_messages : `int`
        max number of messages to process at once, defaults to 10
    timeout : `float`
        timeout for requesting messages from a topic, defaults to 0.2s

    """
    def __init__(self, name, broker, num_messages=10, timeout=0.2):
        self.name = name
        self._lock = threading.Lock()

        ### processing settings
        self.timeout = timeout
        self.num_messages = num_messages
        self._is_running = False

        ### kafka settings
        uri = utils.uriparse(broker)
        self._kafka_settings = {
            'bootstrap.servers': uri.broker,
            'group.id': uri.groupid if uri.groupid else utils.generate_groupid(name)
        }
        self._consumer = Consumer(self._kafka_settings)

        ### processors
        self._processors = {}
        self._timers = {}

        ### signal handler
        for sig in [signal.SIGINT, signal.SIGTERM]:
            signal.signal(sig, self._catch)


    def start(self):
        """Starts the application instance.

        """
        logging.info('starting {}...'.format(self.name.replace('_', ' ')))
        self._consumer.subscribe([topic for topic in self._processors.keys()])
        self._is_running = True
        for timer in self._timers.values():
            timer()
        self._run()


    def stop(self):
        """Stops the application instance.

        """
        logging.info('shutting down {}...'.format(self.name.replace('_', ' ')))
        self._fetch()
        self._is_running = False


    def timer(self, interval, state=None):
        """Adds a timer for a given function. Does the same
        thing as :meth:`add_timer`, but is meant to be used
        as a decorator.

        Parameters
        ----------
        interval : `float`
            the interval of time to wait
        state : `object`
            if specified, initial value for state

        """
        def wrapper(func):
            self.add_timer(interval, func, state=state)
            return func
        return wrapper


    def add_timer(self, interval, func, state=None):
        """Adds a timer to call a function periodically.

        Parameters
        ----------
        interval : `float`
            the interval of time to wait
        func : `callable`
            the function to call
        state : `object`
            if specified, initial value for state

        """
        def start_timer():
            if self._is_running:
                start = timeit.default_timer()
                if state is None:
                    func()
                else:
                    with self._lock:
                        func(state)
                elapsed = timeit.default_timer() - start
                t = threading.Timer(max(interval - elapsed, 0), start_timer)
                t.start()

        self._timers[func.__name__] = start_timer


    def process(self, topics, state=None):
        """Adds a process for a given topic. Does the same
        thing as :meth:`add_process`, but is meant to be used as
        a decorator.

        Parameters
        ----------
        topics : `str` or `iterable`
            the name of the topic(s) to process
        state : `object`
            if specified, makes the processor stateful

        """
        def wrapper(func):
            self.add_process(topics, func, state=state)
            return func
        return wrapper


    def add_process(self, topics, func, state=None):
        """Adds a process for a given topic.

        Parameters
        ----------
        topics : `str` or `iterable`
            the name of the topic(s) to process
        func : `callable`
            the function to call when a message arrives
        state : `object`
            if specified, makes the processor stateful

        """
        if isinstance(topics, str):
            topics = [topics]
        for topic in topics:
            if topic in self._processors:
                raise KeyError('topic already has a process defined for it')
            else:
                self._processors[topic] = {
                    'func': func,
                    'stateful': state is not None,
                    'state': state,
                }


    def _fetch(self):
        """Fetch messages from Kafka.

        """
        messages = self._consumer.consume(
            num_messages=self.num_messages,
            timeout=self.timeout
        )

        for message in messages:
            if message and not message.error():
                processor = self._processors[message.topic()]
                if processor['stateful']:
                    with self._lock:
                        processor['func'](message, processor['state'])
                else:
                    processor['func'](message)


    def _run(self):
        """Processes events.

        """
        while self._is_running:
            self._fetch()


    def _catch(self, signum, frame):
        """Shuts down the application gracefully before exiting.

        """
        logging.info("SIG {:d} received, attempting graceful shutdown...".format(signum))
        self.stop()
        sys.exit(0)
