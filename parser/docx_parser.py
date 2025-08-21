from .abstract_parser import Parser
from io import BytesIO
from docx import Document

class DocxParser(Parser):

    def __init__(self, doc_byte):
        self.doc_byte = doc_byte
        self.document = None
        self.extracted_text = None


    def __enter__(self):
        source_stream = BytesIO(self.doc_byte)

        self.document = Document(source_stream)
        self.extracted_text = self.extract_text_once()

        return self

    def extract_text_once(self):
        
        full_text = "\n".join(
            [paragraph.text for paragraph in self.document.paragraphs])
        
        return full_text


    def extract_text(self):
        return self.extracted_text
    

    def __exit__(self, exc_type, exc_value, traceback):
        pass


        