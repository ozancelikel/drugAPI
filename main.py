from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from handlers.es_aggregator import EsAggregator
from handlers.interaction_api import InteractionAPI
from handlers.graph_handler import GraphHandler

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
es_agg = EsAggregator("drugs", 9201)
interaction_api = InteractionAPI("localhost", 5163)
URI = "neo4j+s://e7958ee4.databases.neo4j.io:7687"
AUTH = ("neo4j", "PefqeKG_6KZPCGLC-VYFuEH4RTr_HzgDX6aNWPnKQa8")
graph_handler = GraphHandler(URI, AUTH)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/autocomplete", response_class=JSONResponse)
async def autocomplete(data: str = Form(...)):
    res = es_agg.get_autocomplete_results(data)
    return res["aggregations"]["auto_complete"]["buckets"]


@app.post("/recursive_autocomplete", response_class=JSONResponse)
async def search_endpoint(data: str = Form(...), stored: str = Form(...)):
    results = es_agg.get_autocomplete_results(data)
    autocomplete_list = {}
    for res in results["aggregations"]["auto_complete"]["buckets"]:
        atc_name = es_agg.get_atc_from_brand(res["key"])
        autocomplete_list[res["key"]] = atc_name

    interaction_list = []
    stored_atc = es_agg.get_atc_from_brand(stored)
    for key, val in autocomplete_list.items():
        interaction = graph_handler.get_relationship(val, stored_atc)
        if interaction is not None:
            interaction_list.append({"drug": key, "atc": val, "interaction_level": interaction})
        else:
            interaction = interaction_api.get_interactions(val, stored_atc)
            interaction_list.append({"drug": key, "atc": val, "interaction_level": interaction})
            # TODO: Check if interaction level is parsed correctly
            graph_handler.add_new_relation(val, stored_atc, interaction)
    return interaction_list


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8002)
