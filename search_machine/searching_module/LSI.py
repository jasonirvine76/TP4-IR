import lightgbm as lgb
import numpy as np

from gensim.models import TfidfModel
from gensim.models import LsiModel
from gensim.corpora import Dictionary

from search_machine.searching_module.TrainingDataset import DatasetTrainer
from scipy.spatial.distance import cosine

import nltk
from nltk.util import ngrams
from Levenshtein import distance as levenshtein_distance




# bentuk dictionary, bag-of-words corpus, dan kemudian Latent Semantic Indexing

class LSI:

  NUM_LATENT_TOPICS = 200

  def __init__(self, docs_location = r"qrels-folder\train_docs.txt", 
                 queries_location =r"qrels-folder\train_queries.txt", 
                 qrels_location = r"qrels-folder\train_qrels.txt"):
    
    print("Creating DatasetTrainer")
    self.trainer = DatasetTrainer(docs_location, queries_location, qrels_location)
    print("DatasetTrainer Created")
    print("=======================")
    self.dictionary = Dictionary()
    self.bow_corpus = [self.dictionary.doc2bow(doc, allow_update = True) for doc in self.trainer.documents.values()]

    print("CREATING LSI MODEL")
    self.model = LsiModel(self.bow_corpus, num_topics = LSI.NUM_LATENT_TOPICS) # 200 latent topics
    print("LSI MODEL CREATED")
    print("=======================")

    self.pre_process()
    
  # test melihat representasi vector dari sebuah dokumen & query
  def vector_rep(self, text):
    rep = [topic_value for (_, topic_value) in self.model[self.dictionary.doc2bow(text)]]
    return rep if len(rep) == LSI.NUM_LATENT_TOPICS else [0.] * LSI.NUM_LATENT_TOPICS

  def ngram_overlap(self, words1, words2, n=2):
    """Calculate the overlap of n-grams between two lists of words."""
    ngrams1 = set(ngrams(words1, n))
    ngrams2 = set(ngrams(words2, n))
    return len(ngrams1 & ngrams2) / len(ngrams1 | ngrams2) if len(ngrams1 | ngrams2) > 0 else 0
  
  def query_coverage(self, query, doc):
        """Calculate the coverage of query terms in the document."""
        return len(set(query) & set(doc)) / len(set(query)) if query else 0

  def features(self, query, doc):
        v_q = self.vector_rep(query)
        v_d = self.vector_rep(doc)
        q = set(query)  
        d = set(doc)
        cosine_dist = cosine(v_q, v_d)
        jaccard = len(q & d) / len(q | d)

        # Bonus : Memberikan tambahan fitur untuk meninggkatkan score LETOR
        length_ratio = len(query) / len(doc) if len(doc) > 0 else 0
        ngram_similarity = self.ngram_overlap(query, doc, n=2)

        lev_distance = levenshtein_distance(' '.join(query), ' '.join(doc))
        normalized_lev_distance = lev_distance / max(len(query), len(doc))

        query_cov = self.query_coverage(query, doc)

        features = v_q + v_d + [jaccard] + [cosine_dist] + [length_ratio] + [ngram_similarity] + [normalized_lev_distance] + [query_cov]

        return features
  
  def pre_process(self, ):
    # kita ubah dataset menjadi terpisah X dan Y
    # dimana X adalah representasi gabungan query+document,
    # dan Y adalah label relevance untuk query dan document tersebut.
    # 
    # Bagaimana cara membuat representasi vector dari gabungan query+document?
    # cara simple = concat(vector(query), vector(document)) + informasi lain
    # informasi lain -> cosine distance & jaccard similarity antara query & doc

    self.X = []
    self.Y = []
    counter = 0
    size = len(self.trainer.dataset)
    for (query, doc, rel) in self.trainer.dataset:
      self.X.append(self.features(query, doc))
      self.Y.append(rel)
      counter += 1
      print(f"Progress {counter} / {size}")

    # ubah X dan Y ke format numpy array
    self.X = np.array(self.X)
    self.Y = np.array(self.Y)

if __name__ == "__main__":
  lsi_model = LSI()
  print(lsi_model.vector_rep(lsi_model.trainer.documents["19305"]))
  print(lsi_model.vector_rep(lsi_model.trainer.queries["Q79"]))


  print(lsi_model.X.shape)
  print(lsi_model.Y.shape)