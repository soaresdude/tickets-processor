from dataclasses import asdict
from random import randint
from typing import List

from faker import Faker

from tickets_processor.clients.jira import JiraClient
from tickets_processor.dtos.tickets import TicketInfo
from worker.main import celery


class TicketsManager:
    tickets_type: List = ["Story", "Bug", "Feature", "Task", "Epic"]
    generator: Faker = Faker()
    jira_client: JiraClient = JiraClient()

    def generate_tickets(self, tickets_number: int) -> List:
        enqueued_tickets = []

        for _ in range(tickets_number):
            ticket = TicketInfo(
                summary=self.generator.text(max_nb_chars=20),
                description=self.generator.text(max_nb_chars=100),
                issue_type=self.tickets_type[randint(0, 4)],
                project="TP"
            )
            enqueued_tickets.append(asdict(ticket))
            celery.add_periodic_task(float(randint(1, 3600)), self.jira_client.create_ticket(ticket), name="create ticket in due time")

        return enqueued_tickets
