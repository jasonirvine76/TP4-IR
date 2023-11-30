from bsbi import BSBIIndex
from compression import VBEPostings
import time
from Ranker import Ranker
import DocsFinder as finder
import numpy as np

BSBI_instance = BSBIIndex(data_dir='search_machine\searching_module\data\collections',
                              postings_encoding=VBEPostings,
                              output_dir='search_machine\searching_module\data\index')

queries = ["elegxo meaning"]

start_time = time.time()

for query in queries:
    print("Query  : ", query)
    print("Results:")
    result = BSBI_instance.retrieve_bm25(query, k=100)
    for (score, doc) in result:
        print(f"{doc:30} {score:>.3f}")
    print()

end_time = time.time()
basic_time = end_time - start_time
print(f"The loop ran for {end_time - start_time} seconds.\n")


# ------------------------

current_ranker = Ranker()
current_ranker.load()

start_time = time.time()
docs = []
for (score, doc) in result:
    docs.append((int(doc[:-4]), finder.open_file(int(doc[:-4]))))

X_unseen = []
for doc_id, doc in docs:
    X_unseen.append(current_ranker.lsi.features(query.split(), doc))

X_unseen = np.array(X_unseen)
scores = current_ranker.ranker.predict(X_unseen)

did_scores = [x for x in zip([did for (did, _) in docs], scores)]
sorted_did_scores = sorted(did_scores, key = lambda tup: tup[1], reverse = True)

for (doc, score) in sorted_did_scores:
        print(f"{doc:30} {score:>.3f}")

end_time = time.time()
basic_time = end_time - start_time