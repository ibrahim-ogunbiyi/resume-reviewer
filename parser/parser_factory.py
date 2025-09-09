from contextlib import contextmanager
from typing import ContextManager, Generator

from .docx_parser import DocxParser
from .pdf_parser import PDFParser


@contextmanager
def get_parser(doc_bytes:bytes, ext:str) -> Generator[ContextManager]:

    if ext in [".pdf"]:

        with PDFParser(doc_bytes=doc_bytes) as parser:
            yield parser
    
    elif ext in [".docx", ".doc"]:
        with DocxParser(doc_byte=doc_bytes) as parser:
            yield parser

     