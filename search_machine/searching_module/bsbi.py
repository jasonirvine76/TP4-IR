import os
import pickle
import contextlib
import heapq
import math
import re
import random


from search_machine.searching_module.index import InvertedIndexReader, InvertedIndexWriter
from search_machine.searching_module.util import IdMap, merge_and_sort_posts_and_tfs
from search_machine.searching_module.compression import VBEPostings
from tqdm import tqdm

import nltk

from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords



from operator import itemgetter


class BSBIIndex:
    """
    Attributes
    ----------
    term_id_map(IdMap): Untuk mapping terms ke termIDs
    doc_id_map(IdMap): Untuk mapping relative paths dari dokumen (misal,
                    /collection/0/gamma.txt) to docIDs
    data_dir(str): Path ke data
    output_dir(str): Path ke output index files
    postings_encoding: Lihat di compression.py, kandidatnya adalah StandardPostings,
                    VBEPostings, dsb.
    index_name(str): Nama dari file yang berisi inverted index
    """

    def __init__(self, data_dir, output_dir, postings_encoding, index_name="main_index"):
        self.term_id_map = IdMap()
        self.doc_id_map = IdMap()
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.index_name = index_name
        self.postings_encoding = postings_encoding

        # Untuk menyimpan nama-nama file dari semua intermediate inverted index
        self.intermediate_indices = []

    def save(self):
        """Menyimpan doc_id_map and term_id_map ke output directory via pickle"""

        with open(os.path.join(self.output_dir, 'terms.dict'), 'wb') as f:
            pickle.dump(self.term_id_map, f)
        with open(os.path.join(self.output_dir, 'docs.dict'), 'wb') as f:
            pickle.dump(self.doc_id_map, f)

    def load(self):
        """Memuat doc_id_map and term_id_map dari output directory"""

        with open(os.path.join(self.output_dir, 'terms.dict'), 'rb') as f:
            self.term_id_map = pickle.load(f)
        with open(os.path.join(self.output_dir, 'docs.dict'), 'rb') as f:
            self.doc_id_map = pickle.load(f)

    def pre_processing_text(self, content):
        """
        Melakukan preprocessing pada text, yakni stemming dan removing stopwords
        """
        # https://github.com/ariaghora/mpstemmer/tree/master/mpstemmer

        stemmer = PorterStemmer()
        stop_words = set(stopwords.words('english'))
        words = word_tokenize(content)
        filtered_sentence = [stemmer.stem(word) for word in words if word.lower() not in stop_words]
        return filtered_sentence

    def parsing_block(self, block_path):
        """
        Lakukan parsing terhadap text file sehingga menjadi sequence of
        <termID, docID> pairs.

        Gunakan tools available untuk stemming bahasa Indonesia, seperti
        MpStemmer: https://github.com/ariaghora/mpstemmer 
        Jangan gunakan PySastrawi untuk stemming karena kode yang tidak efisien dan lambat.

        JANGAN LUPA BUANG STOPWORDS! Kalian dapat menggunakan PySastrawi 
        untuk menghapus stopword atau menggunakan sumber lain seperti:
        - Satya (https://github.com/datascienceid/stopwords-bahasa-indonesia)
        - Tala (https://github.com/masdevid/ID-Stopwords)

        Untuk "sentence segmentation" dan "tokenization", bisa menggunakan
        regex atau boleh juga menggunakan tools lain yang berbasis machine
        learning.

        Parameters
        ----------
        block_path : str
            Relative Path ke directory yang mengandung text files untuk sebuah block.

            CATAT bahwa satu folder di collection dianggap merepresentasikan satu block.
            Konsep block di soal tugas ini berbeda dengan konsep block yang terkait
            dengan operating systems.

        Returns
        -------
        List[Tuple[Int, Int]]
            Returns all the td_pairs extracted from the block
            Mengembalikan semua pasangan <termID, docID> dari sebuah block (dalam hal
            ini sebuah sub-direktori di dalam folder collection)

        Harus menggunakan self.term_id_map dan self.doc_id_map untuk mendapatkan
        termIDs dan docIDs. Dua variable ini harus 'persist' untuk semua pemanggilan
        parsing_block(...).
        """
        # TODO
        td_pairs = []
        for dirpath, dirnames, filenames in os.walk(f"{self.data_dir}/{block_path}"):
            for file_name in filenames:
                    file_path = os.path.join(dirpath, file_name)
                    with open(file_path, 'r', encoding="utf-8") as file:

                        content = file.read()
                        tokens = self.pre_processing_text(content)
                        # tokenizer_pattern = r'\w+'
                        # tokens = re.findall(tokenizer_pattern, tokens)
                        for token in tokens:
                            td_pairs.append((self.term_id_map[token], self.doc_id_map[file_name]))
        return td_pairs

    def write_to_index(self, td_pairs, index):
        """
        Melakukan inversion td_pairs (list of <termID, docID> pairs) dan
        menyimpan mereka ke index. Disini diterapkan konsep BSBI dimana 
        hanya di-maintain satu dictionary besar untuk keseluruhan block.
        Namun dalam teknik penyimpanannya digunakan strategi dari SPIMI
        yaitu penggunaan struktur data hashtable (dalam Python bisa
        berupa Dictionary)

        ASUMSI: td_pairs CUKUP di memori

        Di Tugas Pemrograman 1, kita hanya menambahkan term dan
        juga list of sorted Doc IDs. Sekarang di Tugas Pemrograman 2,
        kita juga perlu tambahkan list of TF.

        Parameters
        ----------
        td_pairs: List[Tuple[Int, Int]]
            List of termID-docID pairs
        index: InvertedIndexWriter
            Inverted index pada disk (file) yang terkait dengan suatu "block"
        """
        # TODO
        term_dict = {}
        for term_id, doc_id in td_pairs:
            if term_id not in term_dict:
                term_dict[term_id] = dict()
            if(term_dict[term_id].get(doc_id) == None):
                term_dict[term_id][doc_id] = 0
            term_dict[term_id][doc_id] += 1
        for term_id in sorted(term_dict.keys()):

            sorted_terms = sorted(term_dict[term_id].items(), key=lambda x: x[0])

            postings_list = [item[0] for item in sorted_terms]
            tf_list = [item[1] for item in sorted_terms]
            
            index.append(term_id, postings_list, tf_list)

    def merge_index(self, indices, merged_index):
        """
        Lakukan merging ke semua intermediate inverted indices menjadi
        sebuah single index.

        Ini adalah bagian yang melakukan EXTERNAL MERGE SORT

        Gunakan fungsi merge_and_sort_posts_and_tfs(..) di modul util

        Parameters
        ----------
        indices: List[InvertedIndexReader]
            A list of intermediate InvertedIndexReader objects, masing-masing
            merepresentasikan sebuah intermediate inveted index yang iterable
            di sebuah block.

        merged_index: InvertedIndexWriter
            Instance InvertedIndexWriter object yang merupakan hasil merging dari
            semua intermediate InvertedIndexWriter objects.
        """
        # kode berikut mengasumsikan minimal ada 1 term
        merged_iter = heapq.merge(*indices, key=lambda x: x[0])
        curr, postings, tf_list = next(merged_iter)  # first item
        for t, postings_, tf_list_ in merged_iter:  # from the second item
            if t == curr:
                zip_p_tf = merge_and_sort_posts_and_tfs(list(zip(postings, tf_list)),
                                                        list(zip(postings_, tf_list_)))
                postings = [doc_id for (doc_id, _) in zip_p_tf]
                tf_list = [tf for (_, tf) in zip_p_tf]
            else:
                merged_index.append(curr, postings, tf_list)
                curr, postings, tf_list = t, postings_, tf_list_
        merged_index.append(curr, postings, tf_list)

    def retrieve_tfidf(self, query, k=10):
        """
        Melakukan Ranked Retrieval dengan skema TaaT (Term-at-a-Time).
        Method akan mengembalikan top-K retrieval results.

        w(t, D) = (1 + log tf(t, D))       jika tf(t, D) > 0
                = 0                        jika sebaliknya

        w(t, Q) = IDF = log (N / df(t))

        Score = untuk setiap term di query, akumulasikan w(t, Q) * w(t, D).
                (tidak perlu dinormalisasi dengan panjang dokumen)

        catatan: 
            1. informasi DF(t) ada di dictionary postings_dict pada merged index
            2. informasi TF(t, D) ada di tf_li
            3. informasi N bisa didapat dari doc_length pada merged index, len(doc_length)

        Parameters
        ----------
        query: str
            Query tokens yang dipisahkan oleh spasi

            contoh: Query "universitas indonesia depok" artinya ada
            tiga terms: universitas, indonesia, dan depok

        Result
        ------
        List[(int, str)]
            List of tuple: elemen pertama adalah score similarity, dan yang
            kedua adalah nama dokumen.
            Daftar Top-K dokumen terurut mengecil BERDASARKAN SKOR.

        JANGAN LEMPAR ERROR/EXCEPTION untuk terms yang TIDAK ADA di collection.

        """
        # TODO
        self.load()
        tokens = self.pre_processing_text(query)
        # tokenizer_pattern = r'\w+'
        # tokens = re.findall(tokenizer_pattern, tokens)
        doc_score = {}
        with InvertedIndexReader(self.index_name, self.postings_encoding, self.output_dir) as index:
            for token in tokens:
                if self.term_id_map.str_to_id.get(token) == None:
                    continue
                token_id = self.term_id_map[token]
                posting_list, tf_list = index.get_postings_list(token_id)

                if(len(posting_list) == 0):
                    continue
                
                idf = math.log10(len(index.doc_length) / len(posting_list))
                for i, doc in enumerate(posting_list):
                    doc_id = self.doc_id_map[doc]
                    if doc_score.get(doc_id) == None:
                        doc_score[doc_id] = 0
                    if tf_list[i] > 0:
                        doc_score[doc_id] += idf * (1 + math.log10(tf_list[i]))
        top_K_docs = sorted(doc_score.items(), key=lambda x: x[1], reverse=True)[:k]
        top_K_docs = [(value, key) for key, value in top_K_docs]
        return top_K_docs


    def retrieve_bm25(self, query, k=10, k1=1.2, b=0.75):
        """
        Melakukan Ranked Retrieval dengan skema scoring BM25 dan framework TaaT (Term-at-a-Time).
        Method akan mengembalikan top-K retrieval results.

        Parameters
        ----------
        query: str
            Query tokens yang dipisahkan oleh spasi

            contoh: Query "universitas indonesia depok" artinya ada
            tiga terms: universitas, indonesia, dan depok

        Result
        ------
        List[(int, str)]
            List of tuple: elemen pertama adalah score similarity, dan yang
            kedua adalah nama dokumen.
            Daftar Top-K dokumen terurut mengecil BERDASARKAN SKOR.

        """
        # TODO
        self.load()
        tokens = self.pre_processing_text(query)
        # tokenizer_pattern = r'\w+'mn
        # tokens = re.findall(tokenizer_pattern, tokens)
        doc_score = {}
        with InvertedIndexReader(self.index_name, self.postings_encoding, self.output_dir) as index:
            avdl = index.avdl
            for token in tokens:
                if self.term_id_map.str_to_id.get(token) == None:
                    continue

                token_id = self.term_id_map[token]
                posting_list, tf_list = index.get_postings_list(token_id)

                if(len(posting_list) == 0):
                    continue

                idf = math.log10(len(index.doc_length) / len(posting_list))
                for i, doc in enumerate(posting_list):
                    doc_id = self.doc_id_map[doc]
                    if doc_score.get(doc_id) == None:
                        doc_score[doc_id] = 0
                    tf = tf_list[i]
                    dl = index.doc_length[doc]
                    bm25 = idf * ((k1 + 1) * tf) / (k1 * ((1 - b) + b * dl / avdl) + tf)
                    doc_score[doc_id] += bm25

        top_K_docs = sorted(doc_score.items(), key=lambda x: x[1], reverse=True)[:k]
        top_K_docs = [(value, key) for key, value in top_K_docs]

        if(top_K_docs == []):
            range_list = list(range(0, 1000000))
            score_list = [0] * 1000000
            random_sample_with_suffix = [str(num) + '.txt' for num in random.sample(range_list, k)]

            top_K_docs = list(zip(score_list, random_sample_with_suffix))
        return top_K_docs
    
    def retrieve_wand(self, query, k=10, is_tfidf=True):
        """
        Melakukan operasi wand. Apabila is_tfidf = True, menggunakan tfidf dan apabila is_tfidf = false
        menggunakan BM25 dengan k1 = 1.2 dan b = 0.75
        """
        # TODO

        self.load()
        tokens = self.pre_processing_text(query)
        # tokenizer_pattern = r'\w+'
        # tokens = re.findall(tokenizer_pattern, tokens)

        k1 = 1.2
        b = 0.75

        top_k = []
        with InvertedIndexReader(self.index_name, self.postings_encoding, self.output_dir) as index:
            index:InvertedIndexReader
            index.load_score()

            token_lst = []
            document_term = []
            avdl = index.avdl
            
            for token in tokens:
                if self.term_id_map.str_to_id.get(token) == None:
                    continue
                token_id = self.term_id_map[token]
                posting_list, tf_list = index.get_postings_list(token_id)
                
                if(len(posting_list) == 0):
                    continue

                idf = math.log10(len(index.doc_length) / len(posting_list))

                token_lst.append(token_id)

                document_term.append([])
                for i in range(len(posting_list)):
                    score = 0
                    doc = posting_list[i]
                    if(is_tfidf):
                        score = idf * (1 + math.log10(tf_list[i]))
                    else:
                        tf = tf_list[i]
                        dl = index.doc_length[doc]
                        score = idf * ((k1 + 1) * tf) / (k1 * ((1 - b) + b * dl / avdl) + tf)
                    document_term[-1].append((doc, score))
                document_term[-1].reverse()
            upper_bounds_term = index.term_upper_bound

            threshold = 0
            curDoc = 0
            
            sorted_terms_id = [i for i in range(len(token_lst))]
            while True:
                if(len(sorted_terms_id) == 0):
                    break
                sorted_terms_id = sorted(sorted_terms_id, key=lambda term: document_term[term][-1][0])

                sum_bounds = 0
                pivot = None
                for term_index in sorted_terms_id:
                    term = token_lst[term_index]
                    if(is_tfidf):
                        sum_bounds += upper_bounds_term[term][0]
                    else:
                        sum_bounds += upper_bounds_term[term][1]
                    if sum_bounds > threshold:
                        pivot = document_term[term_index][-1][0]
                        break

                if pivot is None:
                    break

                if(pivot <= curDoc):
                    first_token = sorted_terms_id[0]
                    document_term[first_token].pop()

                    if(len(document_term[first_token]) == 0):
                        sorted_terms_id.remove(first_token)
                else:
                    first_token = sorted_terms_id[0]
                    if document_term[first_token][-1][0] == pivot:
                        curDoc = pivot
                        total_score = 0
                        for term_id in sorted_terms_id:
                            if document_term[term_id][-1][0] != pivot:
                                break
                            total_score += document_term[term_id][-1][1]
                        
                        if len(top_k) < k:
                            heapq.heappush(top_k, (total_score, pivot))
                        elif total_score > threshold:
                            heapq.heappop(top_k)
                            heapq.heappush(top_k, (total_score, pivot))

                            minimum_dummy = heapq.heappop(top_k)
                            threshold = minimum_dummy[0]
                            heapq.heappush(top_k, minimum_dummy)

                            
                    else:
                        first_token = sorted_terms_id[0]
                        while len(document_term[first_token]) > 0 and document_term[first_token][-1][0] < pivot:
                            document_term[first_token].pop()
                        
                        if len(document_term[first_token]) == 0:
                            sorted_terms_id = [x for x in sorted_terms_id if x != first_token]
        top_k_docs = []
        len_top_k = len(top_k)
        for i in range(len_top_k):
            minimum = heapq.heappop(top_k)
            top_k_docs.append((minimum[0], self.doc_id_map[minimum[1]]))
        top_k_docs.reverse()
        return top_k_docs

            

    def do_indexing(self):
        """
        Base indexing code
        BAGIAN UTAMA untuk melakukan Indexing dengan skema BSBI (blocked-sort
        based indexing)

        Method ini scan terhadap semua data di collection, memanggil parsing_block
        untuk parsing dokumen dan memanggil write_to_index yang melakukan inversion
        di setiap block dan menyimpannya ke index yang baru.
        """
        # loop untuk setiap sub-directory di dalam folder collection (setiap block)
        for block_dir_relative in tqdm(sorted(next(os.walk(self.data_dir))[1])):
            td_pairs = self.parsing_block(block_dir_relative)
            index_id = 'intermediate_index_'+block_dir_relative
            self.intermediate_indices.append(index_id)
            with InvertedIndexWriter(index_id, self.postings_encoding, directory=self.output_dir) as index:
                self.write_to_index(td_pairs, index)
                td_pairs = None

        self.save()

        with InvertedIndexWriter(self.index_name, self.postings_encoding, directory=self.output_dir) as merged_index:
            with contextlib.ExitStack() as stack:
                indices = [stack.enter_context(InvertedIndexReader(index_id, self.postings_encoding, directory=self.output_dir))
                           for index_id in self.intermediate_indices]
                self.merge_index(indices, merged_index)


if __name__ == "__main__":

    BSBI_instance = BSBIIndex(data_dir='search_machine\searching_module\data\collections',
                              postings_encoding=VBEPostings,
                              output_dir='search_machine\searching_module\data\index')
    BSBI_instance.do_indexing()  # memulai indexing!
