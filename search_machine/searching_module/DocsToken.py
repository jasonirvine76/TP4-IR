import pickle
import os
import math
from tqdm import tqdm
import re

class DocsTokens:
    """
    Class yang mengimplementasikan bagaimana caranya scan atau membaca secara
    efisien Inverted Index yang disimpan di sebuah file; dan juga menyediakan
    mekanisme untuk menulis Inverted Index ke file (storage) saat melakukan indexing.

    Attributes
    ----------
    postings_dict: Dictionary mapping:

            termID -> (start_position_in_index_file,
                       number_of_postings_in_list,
                       length_in_bytes_of_postings_list,
                       length_in_bytes_of_tf_list)

        postings_dict adalah konsep "Dictionary" yang merupakan bagian dari
        Inverted Index. postings_dict ini diasumsikan dapat dimuat semuanya
        di memori.

        Seperti namanya, "Dictionary" diimplementasikan sebagai python's Dictionary
        yang memetakan term ID (integer) ke 4-tuple:
           1. start_position_in_index_file : (dalam satuan bytes) posisi dimana
              postings yang bersesuaian berada di file (storage). Kita bisa
              menggunakan operasi "seek" untuk mencapainya.
           2. number_of_postings_in_list : berapa banyak docID yang ada pada
              postings (Document Frequency)
           3. length_in_bytes_of_postings_list : panjang postings list dalam
              satuan byte.
           4. length_in_bytes_of_tf_list : panjang list of term frequencies dari
              postings list terkait dalam satuan byte

    terms: List[int]
        List of terms IDs, untuk mengingat urutan terms yang dimasukan ke
        dalam Inverted Index.

    """

    def __init__(self, index_name, directory=''):
        """
        Parameters
        ----------
        index_name (str): Nama yang digunakan untuk menyimpan files yang berisi index
        postings_encoding : Lihat di compression.py, kandidatnya adalah StandardPostings,
                        GapBasedPostings, dsb.
        directory (str): directory dimana file index berada
        """

        self.metadata_file_path = os.path.join(directory, index_name+'.dict')
        self.doc_token = dict()


    def __enter__(self):
        try:
            with open(self.metadata_file_path, 'rb') as f:
                self.doc_token = pickle.load(f)
        except Exception as e:
            self.doc_token = dict()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        with open(self.metadata_file_path, 'wb') as f:
            pickle.dump(self.doc_token, f)

# def pre_processing_text(content):
#         """
#         Melakukan preprocessing pada text, yakni stemming dan removing stopwords
#         """
#         # https://github.com/ariaghora/mpstemmer/tree/master/mpstemmer

#         stemmer = MPStemmer()
#         stemmed = stemmer.stem_kalimat(content)
#         remover = StopWordRemoverFactory().create_stop_word_remover()
#         return remover.remove(stemmed)


if __name__ == "__main__":
    with DocsTokens('docs-token-list', directory='./docs-token/') as index:
        for block_dir_relative in tqdm(sorted(next(os.walk("collections"))[1])):
            for dirpath, dirnames, filenames in os.walk(f"collections/{block_dir_relative}"):
                for file_name in filenames:
                    file_path = os.path.join(dirpath, file_name)
                    with open(file_path, 'r', encoding="utf-8") as file:
                        content = file.read()
                        tokens = content
                        tokenizer_pattern = r'\w+'
                        tokens = re.findall(tokenizer_pattern, tokens)
                        index.doc_token[file_name] = tokens