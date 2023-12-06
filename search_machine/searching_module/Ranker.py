import lightgbm
from search_machine.searching_module.LSI import LSI
import pickle
import os
from ..apps import lsi, ranker

class Ranker:
    def __init__(self, docs_location = r"search_machine\searching_module\data\docs-train\docs_train.txt", 
                 queries_location =r"search_machine\searching_module\data\query\query.txt", 
                 qrels_location = r"search_machine\searching_module\data\qrels\qrels_extra_irelevant.txt",
                 folder_path = "/src/search_machine/searching_module/data/model_letor") :
        self.docs_location = docs_location
        self.queries_location = queries_location
        self.qrels_location = qrels_location
        self.folder_path = folder_path
        self.ranker = None
        self.lsi = None
    
    def do_ranking(self):
        self.ranker = lightgbm.LGBMRanker(
                            objective="lambdarank",
                            boosting_type = "gbdt",
                            n_estimators = 100,
                            importance_type = "gain",
                            metric = "ndcg",
                            num_leaves = 40,
                            learning_rate = 0.02,
                            max_depth = -1)
        print("Ranker Created")
        print("--------------")
        self.lsi = LSI(self.docs_location, self.queries_location, self.qrels_location)
        print("LSI Created")
        print("--------------")
        self.ranker.fit(self.lsi.X, self.lsi.Y,
           group = self.lsi.trainer.group_qid_count)
        print("Ranker FIT")
        print("--------------")
        self.save()

    def save(self):
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)

        filepath = os.path.join(self.folder_path, "ranker")
        with open(filepath, 'wb') as file:
            pickle.dump(self.ranker, file)
        
        filepath = os.path.join(self.folder_path, "lsi")
        with open(filepath, 'wb') as file:
            pickle.dump(self.lsi, file)

    def load(self):

        if lsi and ranker:
            self.ranker = ranker
            self.lsi = lsi
            return None

        filepath = os.path.join(self.folder_path, "ranker")
        with open(filepath, 'rb') as file:
            self.ranker = pickle.load(file)
        
        filepath = os.path.join(self.folder_path, "lsi")
        with open(filepath, 'rb') as file:
            self.lsi = pickle.load(file)

            
        

# di contoh kali ini, kita tidak menggunakan validation set
# jika ada yang ingin menggunakan validation set, silakan saja
if __name__ == "__main__":
    ranker = Ranker()
    ranker.do_ranking()
    scores = ranker.ranker.predict(ranker.lsi.X)
    print(scores)