from .pdf_parser import PDFParser
from .docx_parser import DocxParser
from contextlib import contextmanager

@contextmanager
def get_parser(doc_bytes:bytes, ext:str):

    if ext in ["pdf", ".pdf"]:

        with PDFParser(doc_bytes=doc_bytes) as parser:
            yield parser
    
    elif ext in ["docx", "doc"]:
        with DocxParser(doc_byte=doc_bytes) as parser:
            yield parser

     