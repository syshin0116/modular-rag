from pydantic import BaseModel


class WebSearchBase(BaseModel):
    query: str
    max_results: int = 10

    def search_web(self):
        pass

