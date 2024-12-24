from flask_restful import Api
from app.controllers.user import User, USER_ROUTE
from app.controllers.upload_image import UploadImage, UPLOAD_IMAGE_ROUTE
from app.controllers.get_image import GetImage, GET_IMAGE_ROUTE
from app.controllers.search_scene import SearchScene, SEARCH_SCENE_ROUTE
from app.controllers.search_dialogue import SearchDialogue, SEARCH_DIALOGUE_ROUTE
from app.controllers.refine_result import RefineResult, REFINE_ROUTE
from app.controllers.set_api_key import SetApiKey, SET_API_KEY_ROUTE
from app.main.errors import errors

# Flask API Configuration
api = Api(
    catch_all_404s=True,
    errors=errors,
    # prefix='/api'
)

# api.add_resource(UserList, '/users')
# api.add_resource(User, '/users/<int:id>/')

api.add_resource(UploadImage, UPLOAD_IMAGE_ROUTE)
api.add_resource(GetImage, GET_IMAGE_ROUTE)
api.add_resource(SearchScene, SEARCH_SCENE_ROUTE)
api.add_resource(SearchDialogue, SEARCH_DIALOGUE_ROUTE)
api.add_resource(User, USER_ROUTE)
api.add_resource(RefineResult, REFINE_ROUTE)
api.add_resource(SetApiKey, SET_API_KEY_ROUTE)