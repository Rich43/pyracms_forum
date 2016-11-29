from cornice import Service
from cornice.validators import colander_body_validator

from pyracms.lib.userlib import UserLib
from pyracms.web_service_views import (valid_token, valid_permission,
                                       APP_JSON, valid_qs_int)

from .deform_schemas.board import ThreadSchema, PostSchema
from .deform_schemas.board_admin import EditForum
from .lib.boardlib import BoardLib, ForumNotFound, ThreadNotFound, PostNotFound

bb = BoardLib()
u = UserLib()

category_list = Service(name='api_category_list', path='/api/board/list',
                        description="List forums")


@category_list.get()
def api_category_list(request):
    """Lists forums."""
    category_list = []
    for category in bb.list_categories():
        forum_list = []
        for forum in category.forums:
            forum_list.append({"forum_id": forum.id,
                               "forum_name": forum.name,
                               "forum_desc": forum.description,
                               "forum_total_threads": forum.total_threads(),
                               "forum_total_posts": forum.total_posts()})
        category_list.append({"category_id": category.id,
                              "category_name": category.name,
                              "forums": forum_list})
    return category_list


forum = Service(name='api_forum', path='/api/board/forum',
                description="Create, Read, Update, Delete forums")


def api_valid_forum_id(request, **kwargs):
    what = "forum_id"
    if valid_qs_int(request, what):
        try:
            bb.get_forum(int(request.params[what]))
        except ForumNotFound:
            request.errors.add('querystring', 'not_found',
                               '%s not found in database.' % what)


@forum.put(content_type=APP_JSON, schema=EditForum,
           validators=(valid_token, colander_body_validator))
def create_forum(request):
    """Create forum."""
    pass


@forum.get(validators=api_valid_forum_id)
def read_forum(request):
    """Read forum."""
    forum_list = []
    forum = bb.get_forum(request.params["forum_id"])
    thread_list = []
    for thread in forum.threads:
        user_name = ""
        if thread.posts.count():
            user_name = thread.posts[0].user.name
        thread_list.append({"thread_name": thread.name,
                            "thread_desc": thread.description,
                            "thread_view_count": thread.view_count,
                            "thread_username": user_name,
                            "thread_id": thread.id,
                            "thread_post_count": thread.total_posts()})
    forum_list.append({"forum_id": forum.id,
                       "forum_name": forum.name,
                       "forum_desc": forum.description,
                       "forum_total_threads": forum.total_threads(),
                       "forum_total_posts": forum.total_posts(),
                       "threads": thread_list})
    return forum_list


@forum.patch(content_type=APP_JSON, schema=EditForum,
             validators=(valid_token, colander_body_validator))
def update_forum(request):
    """Update forum."""
    pass


@forum.delete(validators=valid_token)
def delete_forum(request):
    """Delete forum."""
    pass


thread = Service(name='api_thread', path='/api/board/thread',
                 description="Create, Read, Update, Delete threads")


def api_valid_thread_id(request, **kwargs):
    what = "thread_id"
    if valid_qs_int(request, what):
        try:
            bb.get_thread(int(request.params[what]))
        except ThreadNotFound:
            request.errors.add('querystring', 'not_found',
                               '%s not found in database.' % what)


@thread.put(content_type=APP_JSON, schema=ThreadSchema,
            validators=(valid_token, colander_body_validator))
def create_thread(request):
    """Create thread."""
    pass


@thread.get(validators=api_valid_thread_id)
def read_thread(request):
    """Read thread."""
    thread_list = []
    thread = bb.get_thread(request.params["thread_id"])
    post_list = []
    for post in thread.posts:
        post_list.append({"post_name": post.name,
                          "post_content": post.article,
                          "post_time": str(post.time),
                          "post_username": post.user.name,
                          "post_id": post.id})
    thread_list.append({"thread_id": thread.id,
                        "thread_name": thread.name,
                        "thread_desc": thread.description,
                        "thread_total_posts": thread.total_posts(),
                        "posts": post_list})
    return thread_list


@thread.patch(content_type=APP_JSON, schema=ThreadSchema,
              validators=(valid_token, colander_body_validator))
def update_thread(request):
    """Update thread."""
    pass


@thread.delete(validators=valid_token)
def delete_thread(request):
    """Delete thread."""
    pass


post = Service(name='api_post', path='/api/board/post',
               description="Create, Read, Update, Delete posts")


def api_valid_post_id(request, **kwargs):
    what = "post_id"
    if valid_qs_int(request, what):
        try:
            bb.get_post(int(request.params[what]))
        except PostNotFound:
            request.errors.add('querystring', 'not_found',
                               '%s not found in database.' % what)


@post.put(content_type=APP_JSON, schema=PostSchema,
          validators=(valid_token, colander_body_validator))
def create_post(request):
    """Create post."""
    pass


@post.get(validators=api_valid_post_id)
def read_post(request):
    """Read post."""
    post = bb.get_post(request.params["post_id"])
    return {"post_name": post.name,
            "post_content": post.article,
            "post_time": str(post.time),
            "post_username": post.user.name,
            "post_id": post.id}


@post.patch(content_type=APP_JSON, schema=PostSchema,
            validators=(valid_token, colander_body_validator))
def update_post(request):
    """Update post."""
    pass


@post.delete(validators=valid_token)
def delete_post(request):
    """Delete post."""
    pass
