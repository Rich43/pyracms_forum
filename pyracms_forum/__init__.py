from .models import DBSession
from pyracms.lib.settingslib import SettingsLib
from pyracms.lib.widgetlib import WidgetLib
from pyracms.security import groupfinder
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.events import BeforeRender
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from sqlalchemy import engine_from_config


def add_renderer_globals(event):
    event['w'] = WidgetLib()
    event['s'] = SettingsLib()

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    # Get database settings
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    # Setup auth + auth policy's
    authentication_policy = AuthTktAuthenticationPolicy(
                            settings.get('auth_secret'), callback=groupfinder)
    authorization_policy = ACLAuthorizationPolicy()

    # Configure session support
    session_factory = UnencryptedCookieSessionFactoryConfig(
                                            settings.get('session_secret'))

    # Add basic configuration
    config = Configurator(settings=settings,
                          root_factory='.models.RootFactory',
                          authentication_policy=authentication_policy,
                          authorization_policy=authorization_policy,
                          session_factory=session_factory)
    config.include('pyramid_jinja2')
    config.add_jinja2_search_path("pyracms:templates")
    config.add_subscriber(add_renderer_globals, BeforeRender)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view("dstatic", "deform:static", cache_max_age=3600)
    
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
    config.scan()
    return config.make_wsgi_app()

