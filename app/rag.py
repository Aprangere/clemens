from typing import List, Optional

import chromadb
import requests
from llama_index.core import PromptTemplate, StorageContext, VectorStoreIndex
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.schema import NodeWithScore, QueryBundle
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai_like import OpenAILike
from llama_index.vector_stores.chroma import ChromaVectorStore

from config import (
    CHROMA_COLLECTION,
    CHROMA_PATH,
    EMBED_MODEL,
    MISTRAL_API_KEY,
    MISTRAL_MODEL,
    TOP_K,
)

_SYSTEM_PROMPT = (
    "Tu es ClemENS, le chatbot administratif de l'ENS (École Normale Supérieure – PSL, rue d'Ulm, Paris). "
    "Tu es sympathique, directe et accessible — pas de jargon administratif inutile, tu vas droit au but. "
    "Tu réponds à partir des documents fournis. "
    "Quand tu as une réponse partielle ou incomplète, complète-la toujours en indiquant : "
    "le contact ou service pertinent (secrétariat du département, DG, bibliothèque...) "
    "et/ou l'URL de la page web où l'étudiant trouvera l'information complète. "
    "Si tu n'as pas du tout l'information, dis-le clairement et redirige vers le bon contact ou site. "
    "Formate les liens en Markdown : [texte](url). "
    "Réponds de manière claire, fiable et professionnelle."
)

class _MistralRerank(BaseNodePostprocessor):
    api_key: str
    top_n: int = 4

    def _postprocess_nodes(
        self,
        nodes: List[NodeWithScore],
        query_bundle: Optional[QueryBundle] = None,
    ) -> List[NodeWithScore]:
        if not nodes or query_bundle is None:
            return nodes
        documents = [n.get_content() for n in nodes]
        try:
            r = requests.post(
                "https://api.mistral.ai/v1/rerank",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": "mistral-rerank-latest", "query": query_bundle.query_str,
                      "documents": documents, "top_n": self.top_n},
                timeout=15,
            )
            r.raise_for_status()
            results = r.json()["results"]
            return [
                NodeWithScore(node=nodes[res["index"]].node, score=res["relevance_score"])
                for res in sorted(results, key=lambda x: x["relevance_score"], reverse=True)
            ]
        except Exception:
            # Pas d'API de rerank publique chez Mistral — fallback sur l'ordre de similarité vectorielle
            return nodes[: self.top_n]


_QA_TEMPLATE = PromptTemplate(
    "Documents de référence :\n"
    "-----\n"
    "{context_str}\n"
    "-----\n"
    "Question : {query_str}\n\n"
    "Réponds en te basant uniquement sur les documents ci-dessus. "
    "Si tu ne trouves pas l'information, dis-le explicitement.\n\n"
    "Réponse :"
)


def get_query_engine():
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    chroma_collection = chroma_client.get_or_create_collection(CHROMA_COLLECTION)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL)
    llm = OpenAILike(
        model=MISTRAL_MODEL,
        api_base="https://api.mistral.ai/v1",
        api_key=MISTRAL_API_KEY,
        is_chat_model=True,
        system_prompt=_SYSTEM_PROMPT,
    )

    index = VectorStoreIndex.from_vector_store(
        vector_store,
        embed_model=embed_model,
    )

    reranker = _MistralRerank(api_key=MISTRAL_API_KEY, top_n=4)

    return index.as_query_engine(
        llm=llm,
        similarity_top_k=TOP_K,
        node_postprocessors=[reranker],
        text_qa_template=_QA_TEMPLATE,
    )
