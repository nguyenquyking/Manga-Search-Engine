from flask_restful import Resource, reqparse
from app.services.refine_result_service import RefineResultService
import os
from app.main.settings import Config

REFINE_ROUTE = '/refine-result'

class RefineResult(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('user_id', type=int, required=True, help='User ID is required')
        self.parser.add_argument('selections', type=list, location='json', required=True, help='Selections (array of True/False) are required')
        self.parser.add_argument('top_k', type=int, location='json', required=True, help='Top k is required')
        self.service = RefineResultService()

    def post(self):
        # Parse the incoming arguments
        args = self.parser.parse_args()
        user_id = args['user_id']
        selections = args['selections']
        top_k = args['top_k']

        try:
            # Call the service to process the refinement
            refined_results = self.service.refine_result(user_id, selections, top_k)
            return refined_results
        except Exception as e:
            return {'message': f'Error refining results: {str(e)}'}, 500