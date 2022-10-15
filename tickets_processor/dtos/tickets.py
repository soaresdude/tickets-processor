from dataclasses import dataclass
from typing import Optional


@dataclass
class TicketInfo:
    priority: str
    summary: str
    description: str
    issue_type: str
    project: str
    id: Optional[int] = 0
    key: Optional[str] = ""
    link: Optional[str] = ""
