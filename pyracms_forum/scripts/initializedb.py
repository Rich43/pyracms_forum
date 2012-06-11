from ..models import DBSession, Base
from pyracms.lib.userlib import UserLib
from pyracms.models import RootFactory
from pyramid.paster import get_appsettings, setup_logging
from pyramid.security import Allow
from sqlalchemy import engine_from_config
import os
import sys
import transaction

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
        u.create_group("forum_moderator", "Ability to Edit " +
                       "and Delete forum posts/threads.")
        u.create_group("forum", "Ability to Add forum posts/threads.")
    
        # Default ACL
        acl = RootFactory()
        acl.__acl__.add((Allow, "group:admin", 'edit_board'))
        acl.__acl__.add((Allow, "group:forum", "group:forum"))
        acl.__acl__.add((Allow, "group:forum", 'forum_reply'))
        acl.__acl__.add((Allow, "group:forum", 'forum_edit'))
        acl.__acl__.add((Allow, "group:forum", 'forum_delete'))
        acl.__acl__.add((Allow, "group:forum_moderator",
                         "group:forum_moderator"))
        acl.__acl__.add((Allow, "group:forum_moderator", 'forum_mod_edit'))
        acl.__acl__.add((Allow, "group:forum_moderator", 'forum_mod_delete'))
        acl.sync_to_database()
