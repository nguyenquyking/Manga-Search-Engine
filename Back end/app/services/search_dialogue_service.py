from app.services.search import SearchEngine
from app.main.settings import Config

class SearchService():
    def __init__(self):
        self.search_engine = SearchEngine(index_path=Config.INDEX_SEARCH_PATH, stopwords_path=Config.STOPWORDS_PATH)

    def get_result(self, text, top_k):
        result = self.search_engine.search(query=text, top_k=top_k)
        results = []
        for item in result:
            post_id = item['postId']
            text = item['sentences']
            _, manga, page_type, page_number = post_id.split('\\')
            results.append({
                "id": f'{manga}_{page_type}_{page_number}',
                "manga": manga,
                "page_type": page_type,
                "page_number": page_number,
                "text": text
            })
        return results
        # return result