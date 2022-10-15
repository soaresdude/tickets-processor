import asyncio
import functools
from dataclasses import asdict
from logging import Logger, getLogger
from random import randint
from typing import List

from faker import Faker

from tickets_processor.clients.jira import JiraClient
from tickets_processor.dtos.tickets import TicketInfo
from worker.main import celery


faker = Faker()
logger = getLogger(__name__)


class TicketsManager:
    tickets_type: List = ["Story", "Bug", "Task"]
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
                project="TP"
            )
            enqueued_tickets.append(asdict(ticket))
            time_to_run = randint(1, 30)
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
            }
        }
    }
    logger.info("TICKET_INFO", extra={**data})

    await jira_client.post(data, "/rest/api/2/issue/")
