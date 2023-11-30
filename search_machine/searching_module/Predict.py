import numpy as np
from Ranker import Ranker
from bsbi import BSBIIndex
from compression import VBEPostings
from DocsToken import DocsTokens
from experiment import eval_retrieval, load_qrels

test_queries_location = r"query\query_test.txt"
test_qrel_location = r"qrels\small_qrels.txt"


# load QRELS
qrels = load_qrels(test_qrel_location)

# lakukan evaluasi
eval_retrieval(qrels, test_queries_location, k=100)