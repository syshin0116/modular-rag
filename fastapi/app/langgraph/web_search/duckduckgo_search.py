from app.services.web_search.base import WebSearchBase


class DuckduckgoSearch(WebSearchBase):
    query: str
    max_results: int = 10