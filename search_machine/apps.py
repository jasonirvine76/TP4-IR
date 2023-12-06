from django.apps import AppConfig
import os
import pickle

class SearchMachineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'search_machine'

    def ready(self):
        global lsi
        global ranker

        try:
            filepath = os.path.join("/src/search_machine/searching_module/data/model_letor", "ranker")
            with open(filepath, 'rb') as file:
                ranker = pickle.load(file)
            
            filepath = os.path.join("/src/search_machine/searching_module/data/model_letor", "lsi")
            with open(filepath, 'rb') as file:
                lsi = pickle.load(file)
        except:
            lsi = None
            ranker = None
