from ..models import BBComment, BBThread
from ..views import get_thread
from hashlib import sha512
from json import dumps
from pyracms.models import DBSession
from pyramid.renderers import render
from sqlalchemy.orm.exc import NoResultFound

class CommentLib(object):
    def get_comment(self, *args):
        args = dumps([int(z) if str(z).isnumeric() else z for z in args])
        hash_text = sha512(args.encode()).hexdigest()
        try:
            comment = DBSession.query(BBComment).filter_by(hash_text=
                                                           hash_text).one()
        except NoResultFound:
            comment = BBComment()
            comment.hash_text = hash_text
            comment.thread = BBThread("Comment", args)
            DBSession.add(comment)
        return comment
    
    def render_comment(self, context, request, *args):
        comment = self.get_comment(*args)
        DBSession.flush()
        return render('board/view_thread_content.jinja2', 
                      get_thread(context, request, comment.thread.id), request)