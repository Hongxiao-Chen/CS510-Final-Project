import faiss  # faiss-cpu
from src.loaders.object import read_embedded_objects, read_objects_csv
from src.embeddings.baai import BAAIEmbeddings


class FaissIdx:
    def __init__(self, model, dim=768):
        """
        model: Embedding Model
        """
        self.index = faiss.IndexFlatL2(dim)
        self.doc_map = dict()
        self.model = model
        self.ctr = 0

    def add_doc(self, document_text):
        """Add document and proceed embedding"""
        self.index.add(self.model.embed_query(document_text).reshape(1, -1))
        self.doc_map[self.ctr] = document_text  # store the original document text
        self.ctr += 1

    def add_emb_doc(self, embedding, text):
        """Add embedded documents"""
        self.index.add(embedding.reshape(1, -1))
        self.doc_map[self.ctr] = text
        self.ctr += 1

    def add_folder(self, original_file_path, embedded_file_path):
        """Import embeddings from specific knowledge base，search text directly，search tables by 'Date[SEP]Table Name[SEP]Tags'"""
        ori = read_objects_csv(original_file_path)
        emb = read_embedded_objects(embedded_file_path)

        for i in range(len(ori)):
            self.add_emb_doc(emb[i].search_index, ori[i].to_str())


    def search_doc(self, query, k=3):
        D, I = self.index.search(self.model.embed_query(query).reshape(1, -1), k)
        return [{self.doc_map[idx]: score} for idx, score in zip(I[0], D[0]) if idx in self.doc_map]


if __name__ == '__main__':
    model = BAAIEmbeddings()
    index = FaissIdx(model)
    index.add_folder("D:\\CS\\CS510\\final-project\\data\\outputdata\\Test",
                     "D:\\CS\\CS510\\final-project\\data\\embeddata\\Test")

    while True:
        query = input("Input query：")
        if query.lower() == "exit" or query.lower() == "quit":
            break
        result = index.search_doc(query, 5)
        print(result)
        print(next(iter(result[0])))

    # https://blog.csdn.net/weixin_40375871/article/details/119119975
    # https://zhuanlan.zhihu.com/p/701877192
