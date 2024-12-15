
from app.services.web_search.tavily_search import TavilySearch


a = TavilySearch(query="test")
a.search_web()