from ..models import BBUser, BBThread
from pyracms.models import DBSession, User
from sqlalchemy.orm.exc import NoResultFound

class BBUserNotFound(Exception):
    pass

class BBUserLib():
    """
    A (cut-down) library to manage the bbuser database.
    """
    
    def show(self, name):
        """
        Get a bbuser from his username, 
        It will automatically add a record if it does not exist.
        Raise BBUserNotFound if bbuser does not exist
        """
        if not name:
            raise BBUserNotFound
        try:
            user = DBSession.query(User).filter_by(name=name).one()
            try:
                bb_user = DBSession.query(BBUser).filter_by(user_id=user.id
                                                            ).one()
            except NoResultFound:
                bb_user = BBUser()
                bb_thread = BBThread(user.name, "Profile Comments")
                bb_user.user = user
                bb_user.thread = bb_thread
                DBSession.add(bb_user)
                return self.show(name)
            return bb_user
        except NoResultFound:
            raise BBUserNotFound
    