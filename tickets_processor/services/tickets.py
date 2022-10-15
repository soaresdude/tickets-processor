import asyncio
import functools
from dataclasses import asdict
from logging import Logger, getLogger
from random import randint
from typing import List

import pendulum
from faker import Faker

from tickets_processor.clients.dynamodb import DynamoDBClient
from tickets_processor.clients.jira import JiraClient
from tickets_processor.clients.redis import RedisClient
from tickets_processor.dtos.tickets import TicketInfo
from worker.main import celery


faker = Faker()
logger = getLogger(__name__)
dynamodb = DynamoDBClient()
redis = RedisClient()


class TicketsManager:
    tickets_type: List = ["Story", "Bug", "Task"]
    priorities_type: List = ["Lowest", "Low", "Medium", "High", "Highest"]
    generator: Faker = faker
    jira_client: JiraClient = JiraClient()
    logger: Logger = logger

    def generate_tickets(self, tickets_number: int) -> List:
        enqueued_tickets = []

        for _ in range(tickets_number):
            ticket = TicketInfo(
                summary=self.generator.text(max_nb_chars=20),
                description=self.generator.text(max_nb_chars=100),
                issue_type=self.tickets_type[randint(0, 2)],
                project="TP",
                priority=self.priorities_type[randint(0, 4)]
            )
            enqueued_tickets.append(asdict(ticket))
            time_to_run = randint(1, 3600)
            try:
                task = create_ticket.apply_async(kwargs={"ticket": asdict(ticket)}, countdown=time_to_run)
                self.logger.info("TASK_CREATED", extra={
                    **asdict(ticket),
                    "task.id": task.id,
                    "delay": time_to_run,
                })
            except Exception as e:
                self.logger.exception(e)
                raise e

        return enqueued_tickets


def async_to_sync(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()

        asyncio.set_event_loop(loop)
        loop.run_until_complete(func(*args, **kwargs))

    return wrapped


@celery.task(name="create_ticket_in_due_time")
@async_to_sync
async def create_ticket(ticket: dict, jira_client: JiraClient = JiraClient()):
    data = {
        "fields": {
            "project":
                {
                    "key": ticket.get("project", "TP")
                },
            "summary": ticket.get("summary", faker.text(max_nb_chars=20)),
            "description": ticket.get("description", faker.text(max_nb_chars=100)),
            "issuetype": {
                "name": ticket.get("issue_type", "Task")
            },
            "priority": {
                "name": ticket.get("priority", "Medium")
            }
        }
    }
    logger.info("TICKET_INFO", extra={**data})

    try:
        response = await jira_client.post(data, "/rest/api/2/issue/")
        redis.append_to_key("results_cache", pendulum.now().format("YYYY-MM-DD HH:mm:ss"))
        if ticket["priority"] == "High" or ticket["priority"] == "Highest":
            ticket_info = TicketInfo(
                id=int(response["id"]),
                key=response["key"],
                link=response["self"],
                summary=ticket["summary"],
                description=ticket["description"],
                issue_type=ticket["issue_type"],
                project=ticket["project"],
                priority=ticket["priority"],
            )
            logger.info("SAVING_PRIORITY_TICKET", extra=asdict(ticket_info))
            dynamodb.save_ticket(ticket_info)
    except Exception as e:
        time_to_run = randint(1, 3600)
        create_ticket.apply_async(kwargs={"ticket": ticket}, countdown=time_to_run)
        logger.exception(e)
