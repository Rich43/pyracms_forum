from ..models import DBSession, BBCategory, BBForum, BBThread, BBPost
from sqlalchemy.orm.exc import NoResultFound

class CategoryNotFound(Exception):
    pass

class ForumNotFound(Exception):
    pass

class ThreadNotFound(Exception):
    pass

class PostNotFound(Exception):
    pass

class BoardLib():
    """
    A library to manage and view the bulletin board
    """
    
    def add_category(self, name):
        """
        Add a forum category
        """
        DBSession.add(BBCategory(name))
        
    def delete_category(self, name):
        """
        Delete a forum category
        """
        DBSession.remove(self.get_category(name))
    
    def get_category(self, name):
        """
        Get a forum category
        """
        try:
            return DBSession.query(BBCategory).filter_by(name=name).one()
        except NoResultFound:
            raise CategoryNotFound
        
    def list_categories(self):
        """
        List the boards categories
        """
        categories = DBSession.query(BBCategory)
        return categories
    
    def delete_forum(self, forum):
        """
        Delete a forum
        """
        DBSession.delete(forum)
    
    def add_forum(self, name, description, category):
        """
        Add a forum
        """
        DBSession.add(BBForum(name, description, category))
        
    def get_forum(self, forumid):
        """
        Returns the specified forum
        """
        try:
            forum = DBSession.query(BBForum).filter_by(id=forumid).one()
        except NoResultFound:
            raise ForumNotFound
        return forum
    
    def get_thread(self, threadid):
        """
        Returns the specified thread
        """
        try:
            thread = DBSession.query(BBThread).filter_by(id=threadid).one()
        except NoResultFound:
            raise ThreadNotFound
        return thread
    
    def add_post(self, thread, title, body, user):
        """
        Add a post
        """
        post = BBPost(title, body, user)
        thread.posts.append(post)
    
    def add_thread(self, title, description, body, user, forum=None):
        """
        Add a thread, optionally to a forum.
        """
        thread = BBThread(title, description)
        if forum:
            thread.forum = forum
        self.add_post(thread, title, body, user)
        DBSession.add(thread)
        DBSession.flush()
        return thread
        
    def get_post(self, postid):
        """
        Get a bulletin board post database object
        """
        try:
            return DBSession.query(BBPost).filter_by(id=postid).one()
        except NoResultFound:
            raise PostNotFound
    
    def delete_post(self, post):
        """
        Delete the specified post
        
        Returns:
            1 - Post Deleted
            2 - Thread Deleted
        """
        
        # If it's the first post of a thread, delete the whole thread
        thread = post.thread
        if post == thread.posts[0]:
            for posts in thread.posts:
                posts.user.postcount += -1
            DBSession.delete(thread)
            return 2
        else:
            post.user.postcount += -1
            DBSession.delete(post)
            return 1