def includeme(config):
    """ Activate the forum; usually called via
    ``config.include('pyracms_forum')`` instead of being invoked
    directly. """
    config.add_jinja2_search_path("pyracms_forum:templates")
    # Forum routes
    config.add_route('thread', '/board/thread/{threadid}')
    config.add_route('create_thread', '/board/create_thread/{forumid}')
    config.add_route('thread_list', '/board/forum/{forumid}')
    config.add_route('edit_post', '/board/edit_post/{postid}')
    config.add_route('delete_post', '/board/delete_post/{postid}')
    config.add_route('category_list', '/board/list')

    # Forum Administration routes
    config.add_route('edit_forum_category',
                     '/board_admin/edit_forum_category')
    config.add_route('list_forum_category',
                     '/board_admin/list_forum_category')
    config.add_route('list_forum',
                     '/board_admin/list_forum/{category_id}')
    config.add_route('add_forum',
                     '/board_admin/add_forum/{category_id}/{forum_id}')
    config.add_route('edit_forum',
                     '/board_admin/edit_forum/{forum_id}')
    config.add_route('delete_forum',
                     '/board_admin/delete_forum/{forum_id}')
    config.scan("pyracms_forum.views")
