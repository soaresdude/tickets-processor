from logging import getLogger

from fastapi import APIRouter, status
from fastapi.responses import HTMLResponse

from tickets_processor.services.tickets import results_cache
import plotly.express as px


logger = getLogger(__name__)


router = APIRouter(
    prefix="/charts",
    tags=["charts"]
)


@router.get("/bar", status_code=status.HTTP_200_OK)
async def plot_bar_chart():
    print("results_cache: ", results_cache)
    dataset = {}
    current_date = None
    for entry in results_cache:
        print("entry: ", entry)
        if not current_date:
            current_date = entry
        else:
            if entry.diff(current_date).in_seconds() < 60:
                hour_minute = current_date.format("HH:mm")
                if not dataset.get(hour_minute):
                    dataset[hour_minute] = {"time": hour_minute, "tickets": 1}
                else:
                    dataset[hour_minute]["tickets"] = dataset[hour_minute] + 1
            else:
                current_date = entry

    print("dataset: ", dataset)
    dataframe = {
        "times": [],
        "tickets": []
    }
    for key, value in dataset.items():
        dataframe["times"].append(key)
        dataframe["tickets"].append(value)

    print("dataframe: ", dataframe)

    fig = px.bar(dataframe, x="times", y="tickets")

    return HTMLResponse(fig.to_html())
