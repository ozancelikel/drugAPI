import requests


class InteractionAPI():
    def __init__(self, ip, port):
        self.__url = f"http://{ip}:{port}"

    def get_interactions(self, drug_names, selected_drug):
        for name in drug_names:
            requests.post(self.__url, data=[name, selected_drug])
