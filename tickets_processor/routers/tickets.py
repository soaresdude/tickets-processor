from fastapi import APIRouter, Body, status

from ..services.tickets import TicketsManager


tickets_manager = TicketsManager()
router = APIRouter(
    prefix="/tickets",
    tags=["tickets"]
)


@router.post("/generate", status_code=status.HTTP_202_ACCEPTED)
async def generate_random_tickets(tickets_number: int = Body(150)):
    enqueued_tickets = tickets_manager.generate_tickets(tickets_number)

    return {
               "enqueued_tickets": enqueued_tickets,
               "total_enqueued_tickets": len(enqueued_tickets)
           }
