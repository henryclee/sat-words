from pydantic import BaseModel

class word_context(BaseModel):
    definition: str
    synonyms: list[str]
    sentences: list[str]