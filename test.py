import asyncio

from faker import Faker

from tickets_processor.clients.jira import JiraClient
from tickets_processor.dtos.tickets import TicketInfo

faker = Faker()
ticket = TicketInfo(
                summary=faker.text(max_nb_chars=20),
                description=faker.text(max_nb_chars=100),
                issue_type="Bug",
                project="TP"
)
jira_client = JiraClient()

asyncio.run(jira_client.create_ticket(ticket))
