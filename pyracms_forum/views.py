"""
A bulletin board, all non-admin views go in here.
"""
from .deform_schemas.board import QuickReplySchema, ThreadSchema, PostSchema
from .deform_schemas.board_admin import ForumCategory, EditForum
from .lib.boardlib import BoardLib
from pyracms.errwarninfo import (INFO_FORUM_CATEGORY_UPDATED, INFO, 
    INFO_ACL_UPDATED)
from pyracms.lib.helperlib import (get_username, rapid_deform, redirect, 
    serialize_relation)
from pyracms.lib.userlib import UserLib
from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.security import has_permission
from pyramid.url import route_url
from pyramid.view import view_config

bb = BoardLib()
u = UserLib()

@view_config(route_name='category_list', 
             renderer='board/category_list.jinja2')
def category_list(context, request):
    """
    List forum categories
    """
    return {'categories': bb.list_categories()}

@view_config(route_name='thread_list', renderer='board/thread_list.jinja2')
def get_forum(context, request):
    """
    List all threads in a forum.
    """
    return {'forum': bb.get_forum(request.matchdict.get('forumid'))}

@view_config(route_name='thread', renderer='board/view_thread.jinja2')
def get_thread(context, request, threadid=None):
    """
    List all posts in a thread
    """
    threadid = threadid or request.matchdict.get('threadid')
    thread = bb.get_thread(threadid)
    thread.view_count += 1
    user = u.show(get_username(request))
    def get_thread_submit(context, request, deserialized, bind_params):
        """
        Handle "Quick Reply" box. Add post to database.
        """
        threadid = bind_params.get('threadid')
        if has_permission('forum_reply', context, request):
            title = "Re: " + deserialized.get('title')
            body = deserialized.get('body')
            if not title == '' and not body == '':
                bb.add_post(thread, title, body, user)
            raise HTTPFound(location=request.path_qs)
        else:
            raise HTTPForbidden
    result_dict = rapid_deform(context, request, QuickReplySchema, 
                               get_thread_submit, True, 
                               thread_name=thread.name,
                               threadid=threadid)
    result_dict.update({'thread': thread, 'user': user})
    if has_permission('forum_reply', context, request):
        result_dict['forum_reply'] = True
    if (has_permission('forum_mod_edit', context, request) and 
        has_permission('forum_mod_delete', context, request)):
        result_dict['forum_moderator'] = True
    return result_dict

@view_config(route_name='create_thread', permission='forum_reply', 
             renderer='deform.jinja2')
def create_thread(context, request):
    """
    Display create thread form
    """
    def create_thread_submit(context, request, deserialized, bind_params):
        """
        Add submitted thread and post to database
        """
        user = u.show(get_username(request))
        thread = bb.add_thread(deserialized.get("title"), 
                               deserialized.get("description"), 
                               deserialized.get("body"), user,
                               bind_params['forum'])
        return redirect(request, 'thread', threadid=thread.id)
    forum = bb.get_forum(request.matchdict.get('forumid'))
    result = rapid_deform(context, request, ThreadSchema, 
                          create_thread_submit, forum=forum)
    if isinstance(result, dict):
        message = "Create Thread"
        result.update({"title": message, "header": message})
    return result

@view_config(route_name='edit_post', permission='forum_edit', 
             renderer='deform.jinja2')
def edit_post(context, request):
    """
    Display edit post form
    """
    def edit_post_submit(context, request, deserialized, bind_params):
        """
        Save edited post to database
        """
        bind_params['post'].name = deserialized['title']
        bind_params['post'].article = deserialized['body']
        return redirect(request, 'thread', 
                        threadid=bind_params['post'].thread.id)
    post = bb.get_post(request.matchdict.get('postid'))
    if (has_permission('forum_mod_edit', context, request) or 
        post.user == u.show(get_username(request))):
        result = rapid_deform(context, request, PostSchema, 
                              edit_post_submit, thread_name=post.name, 
                              body=post.article, post=post)
        if isinstance(result, dict):
            message = "Editing Post From " + post.name
            result.update({"title": message, "header": message})
        return result
    else:
        raise HTTPForbidden

@view_config(route_name='delete_post', permission='forum_delete')
def delete_post(context, request):
    """
    Delete a post
    """
    postid = request.matchdict.get('postid')
    post = bb.get_post(postid)
    thread = post.thread
    forum = thread.forum
    
    if (has_permission('forum_mod_delete', context, request) or 
        post.user == u.show(get_username(request))):
        result = bb.delete_post(post)
        if result == 1:
            return HTTPFound(location=route_url('thread', request, 
                                                threadid=thread.id))
        elif result == 2:
            return HTTPFound(location=route_url('thread_list', request,
                                                forumid=forum.id))
    else:
        raise HTTPForbidden

# ----- Start of Admin Views -----

@view_config(route_name='delete_forum', permission='edit_board')
def delete_forum(context, request):
    """
    Delete a forum
    """
    forum = bb.get_forum(request.matchdict.get('forum_id'))
    category_id = forum.category.name
    bb.delete_forum(forum)
    return redirect(request, 'list_forum', category_id=category_id)

@view_config(route_name='add_forum', permission='edit_board', 
             renderer='deform.jinja2')
def add_forum(context, request):
    """
    Display add forum form
    """
    def add_forum_submit(context, request, deserialized, bind_params):
        """
        Add the forum to the database
        """
        category = bind_params.get("category")
        bb.add_forum(deserialized.get("name"), 
                     deserialized.get("description"), category)
        request.session.flash(INFO_ACL_UPDATED, INFO)
        return redirect(request, 'list_forum', 
                        category_id=category.name)
    category = bb.get_category(request.matchdict.get('category_id'))
    forum_id = request.matchdict.get('forum_id')
    result = rapid_deform(context, request, EditForum, add_forum_submit, 
                          name=forum_id, category=category, cache=False)
    if isinstance(result, dict):
        message = "Adding a Forum"
        result.update({"title": message, "header": message})
    return result

@view_config(route_name='edit_forum', permission='edit_board', 
             renderer='deform.jinja2')
def edit_forum(context, request):
    """
    Display edit forum form
    """
    def edit_forum_submit(context, request, deserialized, bind_params):
        """
        Save edited forum to database
        """
        forum = bind_params.get("forum")
        forum.name = deserialized.get("name")
        forum.description = deserialized.get("description")
        request.session.flash(INFO_ACL_UPDATED, INFO)
        return redirect(request, 'list_forum', 
                        category_id=forum.category.name)
    forum = bb.get_forum(request.matchdict.get('forum_id'))
    result = rapid_deform(context, request, EditForum, edit_forum_submit, 
                          forum=forum, cache=False)
    if isinstance(result, dict):
        message = "Editing Forum"
        result.update({"title": message, "header": message})
    return result

@view_config(route_name='list_forum', permission='edit_board', 
             renderer='board_admin/forums.jinja2')
def list_forum(context, request):
    """
    Display a list of forums
    """
    category = bb.get_category(request.matchdict.get('category_id'))
    return {'forums': category.forums, 'category_id': category.name}

@view_config(route_name='list_forum_category', 
             permission='edit_menu', renderer='list.jinja2')
def list_forum_category(context, request):
    """
    Display a list of forum categories
    """
    message = "Select a Forum Category"
    route_name = "list_forum"
    return {'items': [(route_url(route_name, request, 
                                 category_id=item.name), item.name) 
                      for item in bb.list_categories()],
            'title': message, 'header': message}

@view_config(route_name='edit_forum_category', permission='edit_board', 
             renderer='deform.jinja2')
def edit_forum_category(context, request):
    """
    Display edit forum category form
    """
    def edit_forum_category_submit(context, request, deserialized, 
                                   bind_params):
        """
        Save edited forum category to database
        """
        groups = set([g.name for g in bind_params["groups"]])
        deserialized_groups = set(deserialized['forum_categories'])
        for item in deserialized_groups - groups:
            bb.add_category(item)
        for item in groups - deserialized_groups:
            bb.delete_category(item)
        request.session.flash(INFO_FORUM_CATEGORY_UPDATED, INFO)
        return redirect(request, 'category_list')
    groups = bb.list_categories().all()
    appstruct = {'forum_categories': 
                 [x['name'] for x in serialize_relation(groups)]}
    result = rapid_deform(context, request, ForumCategory, 
                          edit_forum_category_submit, appstruct=appstruct,
                          groups=groups)
    if isinstance(result, dict):
        message = "Editing Forum Categorys"
        result.update({"title": message, "header": message})
    return result