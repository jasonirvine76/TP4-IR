import random


class DatasetTrainer:
    def __init__(self, docs_location = r"qrels-folder\train_docs.txt", 
                 queries_location =r"qrels-folder\train_queries.txt", 
                 qrels_location = r"qrels-folder\train_qrels.txt"):
        self.documents = {}
        self.queries = {}
        self.q_docs_rel = {}
        self.group_qid_count = []
        self.dataset = []

        self.docs_location = docs_location
        self.queries_location = queries_location
        self.qrels_location = qrels_location
        self.pre_process()

    def pre_process(self):
        with open(self.docs_location, encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split(" ")
                doc_id = parts[0]
                self.documents[doc_id] = parts[1:]

        with open(self.queries_location, encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split(" ")
                q_id, content = parts[0], parts[1:]
                self.queries[q_id] = content


        NUM_NEGATIVES = 1

        with open(self.qrels_location, encoding="utf-8") as file:
            for line in file:
                q_id, doc_id, rel = line.strip().split(" ")
                if (q_id in self.queries) and (doc_id in self.documents):
                    if q_id not in self.q_docs_rel:
                        self.q_docs_rel[q_id] = []
                    self.q_docs_rel[q_id].append((doc_id, int(rel)))

        for q_id in self.q_docs_rel:
            docs_rels = self.q_docs_rel[q_id]
            self.group_qid_count.append(len(docs_rels) + NUM_NEGATIVES)
            for doc_id, rel in docs_rels:
                self.dataset.append((self.queries[q_id], self.documents[doc_id], rel))
            self.dataset.append((self.queries[q_id], random.choice(list(self.documents.values())), 0))


if __name__ == "__main__":
    trainer = DatasetTrainer()

    assert(" ".join(trainer.documents["19305"]) == "Apa itu kerja lembur? Semua jam kerja yang melebihi jam kerja normal karyawan akan dianggap sebagai jam lembur. Oleh karena itu, jika seorang karyawan dikontrak untuk bekerja 45 jam per minggu waktu normal, maka setiap jam lebih dari itu adalah kerja lembur. Demikian pula, jika seorang karyawan dikontrak untuk bekerja 40 jam per minggu waktu normal, maka setiap jam lebih dari 40 jam adalah kerja lembur. Batasan undang-undang 45 jam per minggu berarti bahwa karyawan tidak boleh bekerja lebih dari 45 jam per minggu waktu normal. Bagaimana dengan jam makan siang? Istirahat makan siang adalah waktu yang tidak dibayar dan merupakan waktu yang dimiliki oleh karyawan itu sendiri – ia dapat membaca buku, berbelanja, berolahraga dll karena mereka tidak dibayar untuk istirahat makan siang.")
    assert(" ".join(trainer.documents["38385"]) == "Tanpa jumlah lendir yang normal, organ-organ dalam tubuh kita tidak dapat berfungsi dengan baik; Oleh karena itu penting untuk menjaga produksi lendir yang normal dan tidak berlebihan untuk membantu menjaga tubuh Anda tetap sehat dan berfungsi secara optimal. Setiap perubahan warna lendir biasanya merupakan tanda adanya masalah kesehatan atau infeksi yang berkembang di dalam tubuh. Lendir Putih. Lendir yang jernih adalah tanda kesehatan yang baik. Ketika tubuh mulai memproduksi lendir berlebihan yang berwarna putih itu menandakan adanya masalah kesehatan.")


    assert(" ".join(trainer.queries["Q10"]) == "at$t nomor layanan pelanggan")
    assert(" ".join(trainer.queries["Q79"]) == "definisi indeterminisme")


    print("number of Q-D pairs:", len(trainer.dataset))
    print("group_qid_count:", trainer.group_qid_count)
    assert sum(trainer.group_qid_count) == len(trainer.dataset), "ada yang salah"
    print(trainer.dataset[:2])