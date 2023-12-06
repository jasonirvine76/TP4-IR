from search_machine.searching_module.bsbi import BSBIIndex
from search_machine.searching_module.compression import VBEPostings
import time
from search_machine.searching_module.Ranker import Ranker
import search_machine.searching_module.DocsFinder as finder
import numpy as np


def ask(request):
    query = request
    BSBI_instance = BSBIIndex(data_dir='search_machine/searching_module/data/collections',
                              postings_encoding=VBEPostings,
                              output_dir='search_machine/searching_module/data/index')
    current_ranker = Ranker()
    current_ranker.load()
    
    result = BSBI_instance.retrieve_bm25(query, k=100)
    
    docs_content = {}
    docs = []
    for (score, doc) in result:
        content, tokens = finder.open_file(int(doc[:-4]))
        docs_content[int(doc[:-4])] = content
        docs.append((int(doc[:-4]), tokens))

    X_unseen = []
    for doc_id, doc in docs:
        X_unseen.append(current_ranker.lsi.features(query.split(), doc))
 
    X_unseen = np.array(X_unseen)
    scores = current_ranker.ranker.predict(X_unseen)

    did_scores = [x for x in zip([did for (did, _) in docs], scores)]
    sorted_did_scores = sorted(did_scores, key = lambda tup: tup[1], reverse = True)

    result_docs = []
    for (doc, score) in sorted_did_scores:
        result_docs.append(doc)
    result_with_content = []
    for docs_id in result_docs:
        content = docs_content[docs_id]
        preview_length = 150
        preview = content[:preview_length] + "..." if len(content) > preview_length else content
        title = content.split()
        title = " ".join(title[:6])
        result_with_content.append(
            {
                'id':docs_id,
                'title':title,
                'preview':preview
            }
        )
    return result_with_content

def get_doc_by_id(id):
    return finder.get_content(id)


if __name__ == "__main__":
    pass