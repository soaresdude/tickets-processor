from fastapi import APIRouter


router = APIRouter(
    prefix="/tickets",
    tags=["tickets"]
)


@router.post("/generate")
async def generate_random_tickets(tickets_number: int = 100):
    pass