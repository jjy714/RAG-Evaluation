# krag/document.py 

from langchain_core.documents import Document

class KragDocument(Document):
    def __init__(self, page_content: str, metadata: dict = {}):
        super().__init__(page_content=page_content, metadata=metadata)
    
    def get_summary(self) -> str:
        return self.page_content[:100] + "..." if len(self.page_content) > 100 else self.page_content
    
    