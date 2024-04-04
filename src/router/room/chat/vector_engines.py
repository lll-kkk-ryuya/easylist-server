import os
import chromadb
from llama_index import (
    VectorStoreIndex, 
    ServiceContext,
)
from llama_index.llms import OpenAI
from llama_index.storage.storage_context import StorageContext
from llama_index.response_synthesizers import get_response_synthesizer
from llama_index.embeddings import resolve_embed_model
from llama_index.embeddings import OpenAIEmbedding
from llama_index.query_engine import RetrieverQueryEngine
from llama_index.retrievers import VectorIndexRetriever
from src.router.room.chat.nodes import DocumentProcessor
from llama_index.vector_stores import ChromaVectorStore
from dotenv import load_dotenv
load_dotenv()
# 環境変数 'OPENAI_API_KEY' を取得
openai_api_key = os.getenv('OPENAI_API_KEY')

class VectorStoreAndQueryEngine:
    def __init__(self, path="chroma_db",document_directory=None):
        self.document_directory = document_directory
        self.vector_query_engines = {}

    def initialize_vector_store_index(self, collection_name, nodes=None, embed_batch_size=64):
        embed_model = OpenAIEmbedding(embed_batch_size=embed_batch_size ,api_key=openai_api_key )
        db = chromadb.PersistentClient(path="chroma_db")
        for node in nodes:
            if 'entities' in node.metadata and isinstance(node.metadata['entities'], list):
                entities_str = ', '.join(node.metadata['entities'])
                node.metadata['entities'] = entities_str
        try:
            chroma_collection = db.get_collection(collection_name)
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            service_context = ServiceContext.from_defaults(embed_model=embed_model)
            index = VectorStoreIndex.from_vector_store(vector_store, service_context=service_context, storage_context=storage_context)
            return collection_name, index
        except ValueError as e:
            print("エンべディング開始")
            chroma_collection = db.get_or_create_collection(collection_name)# Initialize vector store and storage context
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            service_context = ServiceContext.from_defaults(embed_model=embed_model)
            index = VectorStoreIndex(nodes=nodes, storage_context=storage_context, service_context=service_context)


    def initialize_vector_query_engine(self, index, model="gpt-4", temperature=0.1, similarity_top_k=5):
        llm = OpenAI(model=model, temperature=temperature,api_key=openai_api_key )
        service_context = ServiceContext.from_defaults(llm=llm)
        vector_retriever = VectorIndexRetriever(index=index, similarity_top_k=similarity_top_k)

        response_synthesizer = get_response_synthesizer(service_context=service_context, streaming=True)
        vector_query_engine = RetrieverQueryEngine(retriever=vector_retriever, response_synthesizer=response_synthesizer)
        return vector_query_engine

    def add_vector_query_engine(self, collection_name, model="gpt-4", temperature=0.4, similarity_top_k=5):
        document_processor = DocumentProcessor(directory=self.document_directory, model=model)
        nodes = document_processor.process_documents()
        _,index = self.initialize_vector_store_index(collection_name,nodes)
        vector_query_engine = self.initialize_vector_query_engine(index, model, temperature, similarity_top_k)
        #return vector_query_engine
        self.vector_query_engines[collection_name] = vector_query_engine


#directory = "path/to/your/documents"
# collection_name = "your_collection_name"

# VectorQueryEngineManager インスタンスの作成
# vector_query_engine_manager = VectorQueryEngineManager(directory)

# 特定のコレクションに対するベクタークエリエンジンの初期化と追加
# vector_query_engine_manager.add_vector_query_engine(collection_name, model="gpt-4", temperature=0.4, similarity_top_k=5)

# 必要に応じて、追加のコレクションや異なる設定でベクタークエリエンジンを追加できます
