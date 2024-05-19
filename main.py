from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from handlers.es_aggregator import EsAggregator
from handlers.interaction_api import InteractionAPI

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
es_agg = EsAggregator("drugs", 9201)
interaction_api = InteractionAPI("localhost", "port")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/autocomplete", response_class=JSONResponse)
async def autocomplete(data: str = Form(...)):
    res = es_agg.get_autocomplete_results(data)
    return res


@app.post("/recursive_autocomplete", response_class=JSONResponse)
async def search_endpoint(data: str = Form(...)):
    print(data)
    results = es_agg.get_autocomplete_results(data)
    print(results)
    for res in results["aggregations"]["auto_complete"]["buckets"]:
        atc_name = es_agg.get_atc_from_brand(res["key"])
        print(atc_name)


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
