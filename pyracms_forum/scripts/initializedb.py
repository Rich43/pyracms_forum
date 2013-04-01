from ..models import BBCategory, BBForum, BBPost, BBVotes, BBTags #@UnusedImport
from ..models import BBThread #@UnusedImport
from pyracms.factory import RootFactory
from pyracms.lib.menulib import MenuLib
from pyracms.lib.userlib import UserLib
from pyracms.lib.settingslib import SettingsLib
from pyracms.models import DBSession, Base, Menu
from pyramid.paster import get_appsettings, setup_logging
from pyramid.security import Allow, Everyone
from sqlalchemy import engine_from_config
import os
import sys
import transaction

css = """
.category_list, .post_list {
    margin-bottom: 10px;
}

.forum_list {
    text-indent: 20px;
}

.forum_list_title, .thread_list_title, .post_container {
    width: 80%;
    float: left;
}

.post_list_body {
    min-height: 75px;
}

.forum_list_topic_count, .forum_list_post_count, .thread_list_post_count,
.thread_list_author {
    float: left;
    width: 10%;
}

.post_user_container {
    width: 20%;
    float: left;
}

.post_list_title {
    font-size: 12px;
    font-weight: bold;
    float: left;
}

.post_list_sig {
    margin-top: 20px;
    border-color: #000000;
    border-top: solid;
    border-top-width: 1px;
    padding-top: 10px;
}

.post_mod_links {
    width: 100%;
    text-align: right
}

.quickreply {
float: left;
}

.quickreply .req {
display: none;
}

.quickreply_input {
    text-align: center;
}

.quickreply_textarea {
    width: 95%;
}
"""

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd)) 
    sys.exit(1)

def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        # Add Groups
        u = UserLib()
        admin_user = u.show("admin")
        u.create_group("forum_moderator", "Ability to Edit " +
                       "and Delete forum posts/threads.", [admin_user])
        u.create_group("forum", "Ability to Add forum posts/threads.", 
                       [admin_user])
    
        # Default ACL
        acl = RootFactory(session=DBSession)
        acl.__acl__.append((Allow, "group:admin", 'edit_board'))
        acl.__acl__.append((Allow, "group:forum", "group:forum"))
        acl.__acl__.append((Allow, "group:forum", 'forum_reply'))
        acl.__acl__.append((Allow, "group:forum", 'forum_edit'))
        acl.__acl__.append((Allow, "group:forum", 'forum_delete'))
        acl.__acl__.append((Allow, "group:forum_moderator",
                         "group:forum_moderator"))
        acl.__acl__.append((Allow, "group:forum_moderator", 'forum_mod_edit'))
        acl.__acl__.append((Allow, "group:forum_moderator", 'forum_mod_delete'))

        # Add Menu Items
        m = MenuLib()
        DBSession.add(Menu("Forum", "/board/list", 10, 
                           m.show_group("main_menu"), Everyone))
        group = m.show_group("admin_area")
        DBSession.add(Menu("Forum Categories", 
                           "/board_admin/edit_forum_category", 20, group, 
                           'edit_menu'))
        DBSession.add(Menu("Edit Forums", "/board_admin/list_forum_category", 
                           21, group, 'edit_menu'))
        
        # Append CSS
        s = SettingsLib()
        s.update("CSS", s.show_setting("CSS").value + css)