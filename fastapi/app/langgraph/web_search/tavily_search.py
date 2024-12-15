from app.services.web_search.base import WebSearchBase

class TavilySearch(WebSearchBase):
    query: str
    max_results: int = 10



