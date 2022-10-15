from logging import getLogger

import pendulum
from fastapi import APIRouter, status
from fastapi.responses import HTMLResponse

import plotly.express as px

from tickets_processor.clients.redis import RedisClient

logger = getLogger(__name__)
redis = RedisClient()


router = APIRouter(
    prefix="/charts",
    tags=["charts"]
)


@router.get("/bar", status_code=status.HTTP_200_OK)
async def plot_bar_chart():
    results_cache = redis.retrieve_list("results_cache")
    dataset = {}
    current_date = None
    for entry in results_cache:
        entry_dt = pendulum.from_format(entry, "YYYY-MM-DD HH:mm:ss")
        try:
            if not current_date:
                current_date = entry_dt
            else:
                if entry_dt.diff(current_date).in_seconds() < 60:
                    hour_minute = current_date.format("HH:mm")
                    if not dataset.get(hour_minute):
                        dataset[hour_minute] = 1
                    else:
                        dataset[hour_minute] = dataset[hour_minute] + 1
                else:
                    current_date = entry_dt
        except Exception as e:
            logger.exception(e)

    dataframe = {
        "times": [],
        "tickets": []
    }
    for key, value in dataset.items():
        dataframe["times"].append(key)
        dataframe["tickets"].append(value)

    fig = px.bar(dataframe, x="times", y="tickets")

    return HTMLResponse(fig.to_html())
