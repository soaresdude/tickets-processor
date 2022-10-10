import json
from dataclasses import dataclass
from logging import Logger, getLogger
from random import randint
from typing import Any

import boto3
from botocore.exceptions import ClientError


@dataclass
class SqsClient:
    queue_url: str
    queue: Any
    sqs: Any = boto3.resource("sqs", endpoint_url="http://0.0.0.0:4566")
    logger: Logger = getLogger(__name__)

    def _create_queue(self, queue_name: str):
        queue = self.sqs.create_queue(QueueName=queue_name)
        self.queue_url = queue.url
        self.queue = queue
        return queue

    def _get_or_create_queue(self, queue_name: str = "enqueued_tickets"):
        try:
            queue = self.sqs.get_queue_by_name(QueueName=queue_name)
            return queue
        except ClientError as e:
            if e.response["Error"]["Code"] == "AWS.SimpleQueueService.NonExistentQueue":
                return self._create_queue(queue_name)

    def enqueue_message(
        self,
        message_body: dict,
        delay_seconds: int = randint(1, 900)
    ):
        if not self.queue:
            self._get_or_create_queue()

        message = self.queue.send_message(
            MessageBody=json.dumps(message_body),
            DelaySeconds=delay_seconds
        )
        return message
