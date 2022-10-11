from dataclasses import dataclass


@dataclass
class TicketInfo:
    summary: str
    description: str
    issue_type: str
    project: str
