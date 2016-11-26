from cornice import Service
from cornice.validators import colander_body_validator

from pyracms.lib.userlib import UserLib
from pyracms.web_service_views import valid_token, valid_permission, APP_JSON

from .deform_schemas.board import ThreadSchema, PostSchema
from .lib.boardlib import BoardLib

bb = BoardLib()
u = UserLib()

category_list = Service(name='api_category_list', path='/api/board/list',
                        description="List forums")


@category_list.get()
def api_category_list(request):
    """Lists forums."""
    pass


thread = Service(name='api_thread', path='/api/board/thread',
                 description="Create, Read, Update, Delete threads")


@thread.put()
def create_thread(request):
    """Create thread."""
    pass


@thread.get()
def read_thread(request):
    """Read thread."""
    pass


@thread.patch()
def update_thread(request):
    """Update thread."""
    pass


@thread.delete()
def delete_thread(request):
    """Delete thread."""
    pass

post = Service(name='api_post', path='/api/board/post',
                 description="Create, Read, Update, Delete posts")


@post.put()
def create_post(request):
    """Create post."""
    pass


@post.get()
def read_post(request):
    """Read post."""
    pass


@post.patch()
def update_post(request):
    """Update post."""
    pass


@post.delete()
def delete_post(request):
    """Delete post."""
    pass