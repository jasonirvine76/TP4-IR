import re
import os
from bsbi import BSBIIndex
from compression import VBEPostings
from tqdm import tqdm
import math
from Ranker import Ranker
from DocsToken import DocsTokens
import DocsFinder as finder
import numpy as np
np.seterr(divide='ignore', invalid='ignore')

from collections import defaultdict

# >>>>> 3 IR metrics: RBP p = 0.8, DCG, dan AP


def rbp(ranking, p=0.8):
    """ menghitung search effectiveness metric score dengan 
        Rank Biased Precision (RBP)

        Parameters
        ----------
        ranking: List[int]
           vektor biner seperti [1, 0, 1, 1, 1, 0]
           gold standard relevansi dari dokumen di rank 1, 2, 3, dst.
           Contoh: [1, 0, 1, 1, 1, 0] berarti dokumen di rank-1 relevan,
                   di rank-2 tidak relevan, di rank-3,4,5 relevan, dan
                   di rank-6 tidak relevan

        Returns
        -------
        Float
          score RBP
    """
    score = 0.
    for i in range(1, len(ranking) + 1):
        pos = i - 1
        score += ranking[pos] * (p ** (i - 1))
    return (1 - p) * score


def dcg(ranking):
    """ menghitung search effectiveness metric score dengan 
        Discounted Cumulative Gain

        Parameters
        ----------
        ranking: List[int]
           vektor biner seperti [1, 0, 1, 1, 1, 0]
           gold standard relevansi dari dokumen di rank 1, 2, 3, dst.
           Contoh: [1, 0, 1, 1, 1, 0] berarti dokumen di rank-1 relevan,
                   di rank-2 tidak relevan, di rank-3,4,5 relevan, dan
                   di rank-6 tidak relevan

        Returns
        -------
        Float
          score DCG
    """
    # TODO
    score = 0.
    for i in range(1, len(ranking) + 1):
        pos = i - 1
        score += ranking[pos] *  1 / math.log2(i + 1)
    return score


def prec(ranking, k):
    """ menghitung search effectiveness metric score dengan 
        Precision at K

        Parameters
        ----------
        ranking: List[int]
           vektor biner seperti [1, 0, 1, 1, 1, 0]
           gold standard relevansi dari dokumen di rank 1, 2, 3, dst.
           Contoh: [1, 0, 1, 1, 1, 0] berarti dokumen di rank-1 relevan,
                   di rank-2 tidak relevan, di rank-3,4,5 relevan, dan
                   di rank-6 tidak relevan

        k: int
          banyak dokumen yang dipertimbangkan atau diperoleh

        Returns
        -------
        Float
          score Prec@K
    """
    # TODO
    score = 0
    minimum_k = min(k, len(ranking))
    for i in range(0, minimum_k):
        score += ranking[i] / minimum_k
    return score


def ap(ranking):
    """ menghitung search effectiveness metric score dengan 
        Average Precision

        Parameters
        ----------
        ranking: List[int]
           vektor biner seperti [1, 0, 1, 1, 1, 0]
           gold standard relevansi dari dokumen di rank 1, 2, 3, dst.
           Contoh: [1, 0, 1, 1, 1, 0] berarti dokumen di rank-1 relevan,
                   di rank-2 tidak relevan, di rank-3,4,5 relevan, dan
                   di rank-6 tidak relevan

        Returns
        -------
        Float
          score AP
    """
    # TODO
    R = 0
    for ri in ranking:
        R += ri

    if(R == 0):
        return 0
    
    score = 0
    for i in range(len(ranking)):
        if(ranking[i] == 0):
            continue

        score += prec(ranking[:i], i)
    return score / R

# >>>>> memuat qrels


def load_qrels(qrel_file = "test_qrels.txt"):
  qrels = defaultdict(lambda: defaultdict(lambda: 0)) 
  with open(qrel_file) as file:
    for line in file:
      parts = line.strip().split()
      qid = parts[0]
      did = int(parts[1])
      qrels[qid][did] = 1
  return qrels


# >>>>> EVALUASI !


def eval_retrieval(qrels, query_file="queries.txt", k=1000):
    """ 
      loop ke semua query, hitung score di setiap query,
      lalu hitung MEAN SCORE-nya.
      untuk setiap query, kembalikan top-1000 documents
    """
    BSBI_instance = BSBIIndex(data_dir='collections',
                              postings_encoding=VBEPostings,
                              output_dir='index')

    current_ranker = Ranker()
    current_ranker.load()

    with open(query_file) as file:
        rbp_scores_tfidf = []
        dcg_scores_tfidf = []
        ap_scores_tfidf = []

        rbp_scores_bm25 = []
        dcg_scores_bm25 = []
        ap_scores_bm25 = []

        rbp_scores_tfidf_letor = []
        dcg_scores_tfidf_letor = []
        ap_scores_tfidf_letor = []

        rbp_scores_bm25_letor = []
        dcg_scores_bm25_letor = []
        ap_scores_bm25_letor = []

        for qline in tqdm(file):
            parts = qline.strip().split()
            qid = parts[0]
            query = " ".join(parts[1:])

            """
            Evaluasi TF-IDF
            """
            ranking_tfidf = []
            for (score, doc) in BSBI_instance.retrieve_tfidf(query, k=k):
                did = int(os.path.splitext(os.path.basename(doc))[0])
                # Alternatif lain:
                # 1. did = int(doc.split("\\")[-1].split(".")[0])
                # 2. did = int(re.search(r'\/.*\/.*\/(.*)\.txt', doc).group(1))
                # 3. disesuaikan dengan path Anda
                # if (did in qrels[qid]):
                #     ranking_tfidf.append(1)
                # else:
                #     ranking_tfidf.append(0)
                ranking_tfidf.append(qrels[qid][did])
            rbp_scores_tfidf.append(rbp(ranking_tfidf))
            dcg_scores_tfidf.append(dcg(ranking_tfidf))
            ap_scores_tfidf.append(ap(ranking_tfidf))

            """
            Evaluasi BM25
            """
            ranking_bm25 = []
            # nilai k1 dan b dapat diganti-ganti
            for (score, doc) in BSBI_instance.retrieve_bm25(query, k1=1, b=0.8, k=k):
                did = int(os.path.splitext(os.path.basename(doc))[0])
                # Alternatif lain:
                # 1. did = int(doc.split("\\")[-1].split(".")[0])
                # 2. did = int(re.search(r'\/.*\/.*\/(.*)\.txt', doc).group(1))
                # 3. disesuaikan dengan path Anda
                # if (did in qrels[qid]):
                #     ranking_bm25.append(1)
                # else:
                #     ranking_bm25.append(0)
                ranking_bm25.append(qrels[qid][did])
            rbp_scores_bm25.append(rbp(ranking_bm25))
            dcg_scores_bm25.append(dcg(ranking_bm25))
            ap_scores_bm25.append(ap(ranking_bm25))

            """
            Evaluasi TFIDF LETOR
            """
            docs = []
            for (score, doc) in BSBI_instance.retrieve_tfidf(query, k=k):
                # did = int(os.path.splitext(os.path.basename(doc))[0])
                # print(doc, did, "atasw")
                docs.append((int(doc[:-4]), finder.open_file(int(doc[:-4]))))

            X_unseen = []
            for doc_id, doc in docs:
                X_unseen.append(current_ranker.lsi.features(query.split(), doc))

            if(len(X_unseen) == 0):
                continue

                # print(X_unseen, " HAHAHA", docs, query, " docs")
            X_unseen = np.array(X_unseen)

            scores = current_ranker.ranker.predict(X_unseen)

            did_scores = [x for x in zip([did for (did, _) in docs], scores)]
            sorted_did_scores = sorted(did_scores, key = lambda tup: tup[1], reverse = True)
                
            ranking_tfidf_letor = []
            for (did, score) in sorted_did_scores:
                ranking_tfidf_letor.append(qrels[qid][did])
                    
            rbp_scores_tfidf_letor.append(rbp(ranking_tfidf_letor))
            dcg_scores_tfidf_letor.append(dcg(ranking_tfidf_letor))
            ap_scores_tfidf_letor.append(ap(ranking_tfidf_letor))
            """
            Evaluasi BM25 LETOR
            """
            docs = []
            for (score, doc) in BSBI_instance.retrieve_bm25(query, k=k):
                docs.append((int(doc[:-4]), finder.open_file(int(doc[:-4]))))

            X_unseen = []
            for doc_id, doc in docs:
                X_unseen.append(current_ranker.lsi.features(query.split(), doc))

            if(len(X_unseen) == 0):
                continue

            X_unseen = np.array(X_unseen)

            scores = current_ranker.ranker.predict(X_unseen)

            did_scores = [x for x in zip([did for (did, _) in docs], scores)]
            sorted_did_scores = sorted(did_scores, key = lambda tup: tup[1], reverse = True)
                
            ranking_bm25_letor = []
            for (did, score) in sorted_did_scores:
                ranking_bm25_letor.append(qrels[qid][did])
            rbp_scores_bm25_letor.append(rbp(ranking_bm25_letor))
            dcg_scores_bm25_letor.append(dcg(ranking_bm25_letor))
            ap_scores_bm25_letor.append(ap(ranking_bm25_letor))

        print("Hasil evaluasi TF-IDF terhadap queries")
        print("RBP score =", sum(rbp_scores_tfidf) / len(rbp_scores_tfidf))
        print("DCG score =", sum(dcg_scores_tfidf) / len(dcg_scores_tfidf))
        print("AP score  =", sum(ap_scores_tfidf) / len(ap_scores_tfidf))

        print("Hasil evaluasi BM25 terhadap queries")
        print("RBP score =", sum(rbp_scores_bm25) / len(rbp_scores_bm25))
        print("DCG score =", sum(dcg_scores_bm25) / len(dcg_scores_bm25))
        print("AP score  =", sum(ap_scores_bm25) / len(ap_scores_bm25))

        print("Hasil evaluasi TF-IDF Letor terhadap queries")
        print("RBP score =", sum(rbp_scores_tfidf_letor) / len(rbp_scores_tfidf_letor))
        print("DCG score =", sum(dcg_scores_tfidf_letor) / len(dcg_scores_tfidf_letor))
        print("AP score  =", sum(ap_scores_tfidf_letor) / len(ap_scores_tfidf_letor))

        print("Hasil evaluasi BM25 Letor terhadap queries")
        print("RBP score =", sum(rbp_scores_bm25_letor) / len(rbp_scores_bm25_letor))
        print("DCG score =", sum(dcg_scores_bm25_letor) / len(dcg_scores_bm25_letor))
        print("AP score  =", sum(ap_scores_bm25_letor) / len(ap_scores_bm25_letor))



if __name__ == '__main__':
    qrels = load_qrels()

    assert qrels["Q1002252"][5599474] == 1, "qrels salah"
    assert not (6998091 in qrels["Q1007972"]), "qrels salah"

    eval_retrieval(qrels)
