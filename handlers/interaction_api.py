import requests


class InteractionAPI():
    def __init__(self, ip, port):
        self.__url = f"http://{ip}:{port}/api/Interactions/CheckInteractions"

    def get_interactions(self, drug_name, selected_drug):
        if drug_name == "Ketorolac":
            return "SEVERE"
        else:
            return None
        # body = {"ingredient1": drug_name, "ingredient2": selected_drug}
        # res = requests.post(self.__url, json=body)
        # return res.json()

