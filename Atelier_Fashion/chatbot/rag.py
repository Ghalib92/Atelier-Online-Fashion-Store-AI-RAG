"""
RAG pipeline for the fashion assistant chatbot.

The chain (HuggingFace embeddings -> Pinecone retrieval -> OpenAI generation)
is built lazily and cached on first use, so the Django app boots even when the
heavy ML dependencies or API keys are absent. Any configuration/import problem
surfaces as ChatbotUnavailable, which the view turns into a clean 503.
"""

from functools import lru_cache

from django.conf import settings


class ChatbotUnavailable(Exception):
    """Raised when the RAG chain cannot be built (missing keys or deps)."""


@lru_cache(maxsize=1)
def get_rag_chain():
    if not settings.OPENAI_API_KEY or not settings.PINECONE_API_KEY:
        raise ChatbotUnavailable(
            "Chatbot is not configured. Set OPENAI_API_KEY and PINECONE_API_KEY, "
            "and build the Pinecone index with `python store_index.py`."
        )

    try:
        import os

        from langchain.chains import create_retrieval_chain
        from langchain.chains.combine_documents import create_stuff_documents_chain
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_openai import OpenAI
        from langchain_pinecone import PineconeVectorStore

        from src.helper import download_hugging_face_embeddings
        from src.prompt import system_prompt
    except ImportError as exc:  # pragma: no cover - depends on optional ML deps
        raise ChatbotUnavailable(f"Chatbot dependencies are not installed: {exc}") from exc

    # LangChain reads these from the environment.
    os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
    os.environ["PINECONE_API_KEY"] = settings.PINECONE_API_KEY

    embeddings = download_hugging_face_embeddings()
    docsearch = PineconeVectorStore.from_existing_index(
        index_name=settings.PINECONE_INDEX_NAME,
        embedding=embeddings,
    )
    retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})

    llm = OpenAI(temperature=0.4, max_tokens=500)
    prompt = ChatPromptTemplate.from_messages(
        [("system", system_prompt), ("human", "{input}")]
    )
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever, question_answer_chain)


def answer_question(message: str) -> str:
    chain = get_rag_chain()
    result = chain.invoke({"input": message})
    return result["answer"]
