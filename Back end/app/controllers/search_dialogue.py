from flask_restful import Resource, reqparse
from app.services.search_dialogue_service import SearchService

SEARCH_DIALOGUE_ROUTE = '/search-dialouge'

class SearchDialogue(Resource):
    def __init__(self):
        self.service = SearchService()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('text', type=str, location='json', required=True, help='Text is required')
        self.parser.add_argument('top_k', type=int, location='json', required=True, help='Top k is required')
    def get(self):
        pass
    def post(self):
        args = self.parser.parse_args()
        text = args['text']
        top_k = args['top_k']
        result = self.service.get_result(text, top_k)
        print(f'Result: {result}')
        print(f'Length: {len(result)}')
        return result