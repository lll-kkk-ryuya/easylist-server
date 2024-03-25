
from llama_index.llms import OpenAI
from llama_index.text_splitter import TokenTextSplitter
from llama_index.ingestion import IngestionPipeline
from llama_index.extractors import TitleExtractor, QuestionsAnsweredExtractor, EntityExtractor, SummaryExtractor
import os
from dotenv import load_dotenv
# .env ファイルを読み込む
load_dotenv()
# 環境変数 'OPENAI_API_KEY' を取得
openai_api_key = os.getenv('OPENAI_API_KEY')
import chromadb
from llama_index.llms import OpenAI
from llama_index.text_splitter import TokenTextSplitter
from llama_index.ingestion import IngestionPipeline
from llama_index.extractors import TitleExtractor, QuestionsAnsweredExtractor, EntityExtractor, SummaryExtractor
from llama_index import Document

class DocumentProcessor:
    def __init__(self, directory=None, model="gpt-3.5-turbo"):
        self.directory = directory
        self.model = model

    def load_documents_from_directory(self):
        documents = []
        # ディレクトリがNoneの場合は、処理をスキップ
        if self.directory is None:
            return documents

        for filename in os.listdir(self.directory):
            if filename.endswith(".txt"):
                file_path = os.path.join(self.directory, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read()
                    category = os.path.splitext(filename)[0]
                    doc = Document(text=text, metadata={"filename": filename, "category": category})
                    documents.append(doc)
        return documents

    def process_documents(self):
        documents = self.load_documents_from_directory()
        # ドキュメントが空の場合は、処理をスキップ
        if not documents:
            return []

        llm = OpenAI(temperature=0.1, model=self.model, max_tokens=512)
        text_splitter = TokenTextSplitter(separator=" ", chunk_size=512, chunk_overlap=128)
        extractors = [
            TitleExtractor(nodes=5, llm=llm),
            QuestionsAnsweredExtractor(questions=3, llm=llm),
            EntityExtractor(prediction_threshold=0.5, llm=llm),
            SummaryExtractor(summaries=["prev", "self"]),
        ]

        pipeline = IngestionPipeline(transformations=[text_splitter] + extractors)
        uber_nodes = pipeline.run(documents=documents)
        return uber_nodes






    

