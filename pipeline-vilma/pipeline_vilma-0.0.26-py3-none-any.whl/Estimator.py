from loguru import logger
from pipelinevilma.Messager import Messager
from pipelinevilma.EstimatorActor import EstimatorActor
import os
import time


class Estimator:
    def __init__(self, queue_server, input_queue, output_queue, input_evaluator_queue, actor):
        self.input_queue = Messager(queue_server, input_queue)
        self.output_queue = Messager(queue_server, output_queue)
        self.input_evaluator_queue = Messager(queue_server, input_evaluator_queue)
        self.actor = actor

    def get_estimator_model(self):
        raise NotImplementedError("Should have implemented this")

    def set_estimator_model(self, message):
        raise NotImplementedError("Should have implemented this")

    def estimate(self, message):
        raise NotImplementedError("Should have implemented this")

    def run(self):
        while True:
            # Check for model
            logger.info("Checking for new model")
            message = self.get_estimator_model()
            if message:
                logger.info("New model")
                self.set_estimator_model(message)

            # Consume queue
            logger.info("Checking for new message from pipeline")
            message = self.input_queue.get_message()
            if message:
                estimations = self.estimate(message)
                if estimations:
                    self.forward(estimations)
                else:
                    logger.error("No estimations done")
            time.sleep(1 / 60)

    def forward(self, message):
        logger.info("Forwarding message to " + str(self.output_queue.queue_name))
        self.output_queue.publish(message=message, validate=False)
