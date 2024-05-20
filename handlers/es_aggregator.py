from elasticsearch import Elasticsearch
from fastapi import HTTPException


class EsAggregator:
    def __init__(self, index: str, port: int):
        self.__es = Elasticsearch(f"http://localhost:{port}")
        self.__index = index

    def get_atc_from_brand(self, brand):
        resp = self.__es.search(
            index=self.__index,
            pretty=True,
            body={"query": {"match": {"brand": brand}}},
        )
        return resp["hits"]["hits"][0]["_source"]["atc"]

    def get_autocomplete_results(self, data: str):
        base_query = {
            "_source": [],
            "size": 0,
            "min_score": 0.5,
            "query": {
                "bool": {
                    "must": [
                        {
                            "match_phrase_prefix": {
                                "brand": {
                                    "query": data
                                }
                            }
                        }
                    ],
                    "filter": [],
                    "should": [],
                    "must_not": []
                }
            },
            "aggs": {
                "auto_complete": {
                    "terms": {
                        "field": "brand.keyword",
                        "order": {
                            "_count": "desc"
                        },
                        "size": 5
                    }
                }
            }
        }
        try:
            res = self.__es.search(index=self.__index, body=base_query)
            print("Successfully retrieved documents!")
            return res
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=str(e))
