from typing import Self

import pymupdf


class PDFParser:
    def __init__(self, doc_bytes: bytes) -> None:
        self.doc_byte = doc_bytes
        self.extracted_doc = None
        self.doc = None

    def __enter__(self) -> Self:
        self.doc = pymupdf.open(stream=self.doc_byte, filetype="pdf")
        self.extracted_doc = self._extract_text_once()

        return self

    def _extract_text_once(self) -> list[str]:
        list_of_text = [self.doc[index].get_text() for index in range(self.doc.page_count)]

        return list_of_text

    def __exit__(
        self, exc_type: BaseException, exc_value: BaseException, traceback: object
    ) -> None:
        try:
            if self.doc:
                self.doc.close()
        except Exception:
            pass

    def extract_text(self) -> str:
        text = "\n".join(self.extracted_doc)

        return text

    def extract_text_by_page(self) -> dict[int, str]:
        extracted_doc = self.extracted_doc()

        result = dict(zip(list(range(len(extracted_doc))), extracted_doc))

        return result
