from cornice import Service
from cornice.validators import colander_body_validator
from pyracms.lib.userlib import UserLib
from pyracms.web_service_views import (valid_token, valid_permission,
                                       APP_JSON, valid_qs_int, valid_qs)

from .deform_schemas.board import ThreadSchema, PostSchema, ThreadSchemaAPI
from .deform_schemas.board_admin import (EditForum, UpdateForumCategory,
                                         ForumCategoryItemAPI, EditForumAPI)
from .lib.boardlib import (BoardLib, ForumNotFound, ThreadNotFound,
                           PostNotFound, CategoryNotFound, CategoryFound,
                           ForumFound)

bb = BoardLib()
u = UserLib()


def edit_board_permission(request, **kwargs):
    if not valid_permission(request, 'edit_board'):
        request.errors.add('body', 'access_denied', 'Access denied')
        return


category_list = Service(name='api_category_list', path='/api/board/list',
                        description="List categories")


@category_list.get()
def api_category_list(request):
    """Lists forums."""
    category_list = []
    for category_obj in bb.list_categories():
        forum_list = []
        for forum in category_obj.forums:
            forum_list.append({"forum_id": forum.id,
                               "forum_name": forum.name,
                               "forum_desc": forum.description,
                               "forum_total_threads": forum.total_threads(),
                               "forum_total_posts": forum.total_posts()})
        category_list.append({"category_id": category_obj.id,
                              "category_name": category_obj.name,
                              "forums": forum_list})
    return category_list


category = Service(name='api_category', path='/api/board/category',
                   description="Create, Update, Delete Categories")


def api_valid_name(request, **kwargs):
    what = "name"
    if valid_qs(request, what):
        try:
            bb.get_category(request.params[what])
        except CategoryNotFound:
            request.errors.add('querystring', 'not_found',
                               '%s not found in database.' % what)
            return


@category.get(validators=api_valid_name)
def read_category(request):
    name = request.params.get('name')
    category_obj = bb.get_category(name)
    forum_list = []
    for forum in category_obj.forums:
        forum_list.append({"forum_id": forum.id,
                           "forum_name": forum.name,
                           "forum_desc": forum.description,
                           "forum_total_threads": forum.total_threads(),
                           "forum_total_posts": forum.total_posts()})
    return {"category_id": category_obj.id,
            "category_name": category_obj.name,
            "forums": forum_list}


@category.put(content_type=APP_JSON, schema=ForumCategoryItemAPI,
              validators=(valid_token, colander_body_validator,
                          edit_board_permission))
def create_category(request):
    """Create category."""
    name = request.json_body.get('name')
    try:
        bb.add_category(name)
    except CategoryFound:
        request.errors.add('body', 'found',
                           '%s already exists in database.' % "name")
    return {"status": "created"}


@category.patch(content_type=APP_JSON, schema=UpdateForumCategory,
                validators=(valid_token, colander_body_validator,
                            edit_board_permission))
def update_category(request):
    """Update category."""
    try:
        category = bb.get_category(request.json_body["old_name"])
    except CategoryNotFound:
        request.errors.add('body', 'not_found',
                           '%s not found in database.' % "old_name")
        return
    try:
        category = bb.get_category(request.json_body["new_name"])
        request.errors.add('body', 'found',
                           '%s already exists in database.' % "new_name")
        return
    except CategoryNotFound:
        pass
    category.name = request.json_body["new_name"]
    return {"status": "updated"}


@category.delete(validators=(valid_token, edit_board_permission,
                             api_valid_name))
def delete_category(request):
    """Delete category."""
    bb.delete_category(request.params['name'])
    return {"status": "deleted"}


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
            return


@forum.put(content_type=APP_JSON, schema=EditForumAPI,
           validators=(valid_token, colander_body_validator,
                       edit_board_permission))
def create_forum(request):
    """Create forum."""
    name = request.json_body['name']
    description = request.json_body['description']
    category_name = request.json_body['category']
    try:
        category_obj = bb.get_category(category_name)
    except CategoryNotFound:
        request.errors.add('body', 'not_found',
                           '%s not found in database.' % "category")
        return
    try:
        bb.add_forum(name, description, category_obj)
    except ForumFound:
        request.errors.add('body', 'found',
                           '%s already exists in database.' % "name")
        return
    return {"status": "created"}


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
             validators=(valid_token, colander_body_validator,
                         edit_board_permission, api_valid_forum_id))
def update_forum(request):
    """Update forum."""
    forum_id = request.params["forum_id"]
    name = request.json_body['name']
    description = request.json_body['description']
    try:
        forum = bb.get_forum(forum_id)
    except ForumNotFound:
        request.errors.add('body', 'not_found',
                           '%s not found in database.' % "category")
        return
    if name != forum.name:
        try:
            bb.get_forum_by_name(name)
            request.errors.add('body', 'found',
                               '%s already exists in database.' % "name")
            return
        except ForumNotFound:
            pass
    forum.name = name
    forum.description = description
    return {"status": "updated"}


@forum.delete(validators=(valid_token, edit_board_permission,
                          api_valid_forum_id))
def delete_forum(request):
    """Delete forum."""
    forum_id = request.params["forum_id"]
    try:
        forum = bb.get_forum(forum_id)
    except ForumNotFound:
        request.errors.add('body', 'not_found',
                           '%s not found in database.' % "category")
        return
    bb.delete_forum(forum)


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
            validators=(valid_token, colander_body_validator,
                        api_valid_forum_id))
def create_thread(request):
    """Create thread."""
    if not valid_permission(request, 'forum_reply'):
        request.errors.add('body', 'access_denied', 'Access denied')
        return
    user = request.validated['user_db']
    forum = bb.get_forum(request.params.get('forum_id'))
    thread = bb.add_thread(request.json_body.get("title"),
                           request.json_body.get("description"),
                           request.json_body.get("body"), user, forum)
    return {"status": "success", "thread_id": thread.id,
            "thread_name": thread.name,
            "thread_desc": thread.description,
            "thread_total_posts": thread.total_posts()}


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


@thread.patch(content_type=APP_JSON, schema=ThreadSchemaAPI,
              validators=(valid_token, colander_body_validator,
                          api_valid_thread_id))
def update_thread(request):
    """Update thread."""
    user = request.validated['user_db']
    thread = bb.get_thread(request.params["thread_id"])
    if not valid_permission(request, 'forum_edit'):
        request.errors.add('body', 'access_denied', 'Access denied')
        return
    if (valid_permission(request, 'forum_mod_edit') or
            thread.posts[0].user == user):
        thread.name = request.json_body['title']
        thread.description = request.json_body['description']
    else:
        request.errors.add('body', 'access_denied', 'Access denied')
        return
    return {"status": "success", "thread_id": thread.id,
            "thread_name": thread.name,
            "thread_desc": thread.description,
            "thread_total_posts": thread.total_posts()}

@thread.delete(validators=(valid_token, api_valid_thread_id))
def delete_thread(request):
    """Delete thread."""
    if not (valid_permission(request, 'forum_delete') and
            valid_permission(request, 'forum_mod_edit')):
        request.errors.add('body', 'access_denied', 'Access denied')
        return
    thread_id = request.params["thread_id"]
    bb.delete_thread(thread_id)
    return {"status": "success"}

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
          validators=(valid_token, colander_body_validator,
                      api_valid_thread_id))
def create_post(request):
    """Create post."""
    name = request.json_body['title']
    article = request.json_body['body']
    user = request.validated['user_db']
    thread_obj = bb.get_thread(request.params["thread_id"])
    if not valid_permission(request, 'forum_reply'):
        request.errors.add('body', 'access_denied', 'Access denied')
        return
    post_obj = bb.add_post(thread_obj, name, article, user)
    return {"status": "created", "post_name": post_obj.name,
            "post_content": post_obj.article,
            "post_time": str(post_obj.time),
            "post_username": post_obj.user.name,
            "post_id": post_obj.id}

@post.get(validators=api_valid_post_id)
def read_post(request):
    """Read post."""
    post_obj = bb.get_post(request.params["post_id"])
    return {"post_name": post_obj.name,
            "post_content": post_obj.article,
            "post_time": str(post_obj.time),
            "post_username": post_obj.user.name,
            "post_id": post_obj.id}


@post.patch(content_type=APP_JSON, schema=PostSchema,
            validators=(valid_token, colander_body_validator,
                        api_valid_post_id))
def update_post(request):
    """Update post."""
    user = request.validated['user_db']
    post_obj = bb.get_post(request.params["post_id"])
    if not valid_permission(request, 'forum_edit'):
        request.errors.add('body', 'access_denied', 'Access denied')
        return
    if not (valid_permission(request, 'forum_mod_edit') or
            post_obj.user == user):
        request.errors.add('body', 'access_denied', 'Access denied')
        return
    post_obj.name = request.json_body['title']
    post_obj.article = request.json_body['body']
    return {"status": "updated", "post_name": post_obj.name,
            "post_content": post_obj.article,
            "post_time": str(post_obj.time),
            "post_username": post_obj.user.name,
            "post_id": post_obj.id}

@post.delete(validators=(valid_token, api_valid_post_id))
def delete_post(request):
    """Delete post."""
    post_obj = bb.get_post(request.params["post_id"])
    if not (valid_permission(request, 'forum_delete') and
            valid_permission(request, 'forum_mod_edit')):
        request.errors.add('body', 'access_denied', 'Access denied')
        return
    what_id = bb.delete_post(post_obj)
    if what_id == 1:
        what = "post"
    else:
        what = "thread"
    return {"status": "deleted", "what": what, "what_id": what_id}