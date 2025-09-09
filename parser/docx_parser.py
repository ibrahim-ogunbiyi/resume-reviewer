from io import BytesIO
from types import TracebackType
from typing import Type

from docx import Document

from .abstract_parser import Parser


class DocxParser(Parser):

    def __init__(self, doc_byte:bytes) -> None:
        self.doc_byte = doc_byte
        self.document = None
        self.extracted_text = None


    def __enter__(self) -> None:
        source_stream = BytesIO(self.doc_byte)

        self.document = Document(source_stream)
        self.extracted_text = self.extract_text_once()

        return self

    def extract_text_once(self) -> str:
        
        full_text = "\n".join(
            [paragraph.text for paragraph in self.document.paragraphs])
        
        return full_text


    def extract_text(self) -> str:
        return self.extracted_text
    

    def __exit__(self, exc_type:Type, exc_value:BaseException, traceback: TracebackType) -> None:
        pass


        