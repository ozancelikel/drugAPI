from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import yaml

with open('config.yaml', 'r') as file:
    conf = yaml.safe_load(file)

from handlers.es_aggregator import EsAggregator
from handlers.interaction_api import InteractionAPI
from handlers.graph_handler import GraphHandler

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
es_agg = EsAggregator(conf["ES_INDEX"], conf["ES_PORT"])
interaction_api = InteractionAPI(conf["INTERACTION_API_IP"], conf["INTERACTION_API_PORT"])
graph_handler = GraphHandler(conf["NEO4J_URI"], (conf["NEO4J_USER"], conf["NEO4J_PSW"]))


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
        interaction = graph_handler.read_relation(val, stored_atc)
        if interaction is not None:
            interaction_list.append({"drug": key, "atc": val, "interaction_level": [
                  {
                    "ingredient1": val,
                    "ingredient2": stored_atc,
                    "interactionLevel": interaction["level"]
                  }
                ]})
        else:
            interaction = interaction_api.get_interactions(val, stored_atc)
            interaction_list.append({"drug": key, "atc": val, "interaction_level": interaction})
            # TODO: Check if interaction level is parsed correctly
            graph_handler.write_relation(val, stored_atc, interaction)
    return interaction_list


if __name__ == '__main__':
    uvicorn.run(app, host=conf["MAIN_IP"], port=conf["MAIN_PORT"])
