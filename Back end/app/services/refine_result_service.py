from app.services.chromadb_service import ChromaDBService

class RefineResultService:
    def __init__(self):
        self.chromadb_service = ChromaDBService()
    
    def format_result(self, result):
        results = []
        for id, (distance, embedding) in result.items():
            print('id:', id)
            base_name = id.split('.')[0]
            fields = base_name.split('_')
            results.append({
                "id": f'{fields[1]}_{fields[2]}_{fields[3]}',
                "distance": distance,
                # "embedding": embedding.tolist(),
                "manga": fields[1],
                "page_type": fields[2],
                "page_number": fields[3],
            })
        return {
            "results": results
        }

    def refine_result(self, user_id, selections, top_k):
        print('Service: Refining results')
        return self.format_result(self.chromadb_service.refine_result(user_id, selections, top_k))