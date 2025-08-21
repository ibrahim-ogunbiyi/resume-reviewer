from abstract_parser import Parser
import pymupdf

class PDFParser(Parser):

    def __init__(self, doc_bytes):
        self.doc_byte = doc_bytes
        self.extracted_doc = None
    
    def __enter__(self):
        self.doc = pymupdf.open(stream=self.doc_byte, filetype="pdf")
        self.extracted_doc = self._extract_text_once()

    
    def _extract_text_once(self) -> list[str]:
        
        list_of_text = [
                self.doc[index].get_text() 
                for index in range(self.doc.page_count)
            ]

        return list_of_text
    
    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if self.doc:
                self.doc.close()
        except Exception:
            pass
    def extract_text(self):
        text = "\n".join(self.extracted_doc())

        return text
    
    def extract_text_by_page(self):
        
        extracted_doc = self.extracted_doc()

        result = dict(zip(list(range(len(extracted_doc))), extracted_doc))
    
        return result

