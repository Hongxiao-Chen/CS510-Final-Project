from typing import Any, Dict, List, Optional
from langchain_core.embeddings import Embeddings
from langchain_core.pydantic_v1 import BaseModel
from sentence_transformers import SentenceTransformer


def test():
    model = SentenceTransformer("../models/bge-base-en-v1.5")
    sentences_1 = ["Test-1", "Test-2"]
    sentences_2 = ["Test-3", "Test-4"]
    embeddings_1 = model.encode(sentences_1, normalize_embeddings=True)
    embeddings_2 = model.encode(sentences_2, normalize_embeddings=True)
    similarity = embeddings_1 @ embeddings_2.T
    print(similarity)


class BAAIEmbeddings(Embeddings):
    """`BAAI Embeddings"""

    def __init__(self,
                 model_path="../models/bge-base-en-v1.5",
                 ):

        super().__init__()
        self._model = SentenceTransformer(model_path)

    def embed_query(self, text: str) -> List[float]:
        resp = self.embed_documents([text])
        return resp[0]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embeds a list of text documents.

        Args:
            texts (List[str]): A list of text documents to embed.

        Returns:
            List[List[float]]: A list of embeddings for each document in the input list.
                            Each embedding is represented as a list of float values.
        """
        return self._model.encode(texts)

if __name__ == '__main__':
    test()