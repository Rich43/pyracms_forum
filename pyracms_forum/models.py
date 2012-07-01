from datetime import datetime
from pyracms.models import Files, User, RootFactory, DBSession, Base #@UnusedImport
from sqlalchemy import Column, Integer, Unicode, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey, UniqueConstraint

class BBVotes(Base):
    __tablename__ = 'bbvotes'
    __table_args__ = (UniqueConstraint('user_id', 'post_id'),
                      {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'})

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('bbpost.id'))
    post = relationship("BBPost")
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship(User)
    like = Column(Boolean, nullable=False, index=True)

    def __init__(self, user, like):
        self.user = user
        self.like = like

class BBTags(Base):
    __tablename__ = 'bbtags'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(128), index=True, nullable=False)
    thread_id = Column(Integer, ForeignKey('bbthread.id'))
    thread = relationship("BBThread")

    def __init__(self, name):
        self.name = name


class BBCategory(Base):
    __tablename__ = 'bbcategory'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(128), index=True, unique=True, nullable=False)
    forums = relationship("BBForum")

    def __init__(self, name):
        self.name = name

class BBPost(Base):
    __tablename__ = 'bbpost'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(128), index=True, nullable=False)
    article = Column(Unicode(16384), default='')
    time = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship(User)
    thread_id = Column(Integer, ForeignKey('bbthread.id'))
    thread = relationship("BBThread")
    file_id = Column(Integer, ForeignKey('files.id'))
    file_obj = relationship(Files, cascade="all, delete")
    votes = relationship(BBVotes, lazy="dynamic",
                         cascade="all, delete, delete-orphan")

    def __init__(self, name, article, user):
        self.name = name
        self.article = article
        self.user = user
        user.postcount += 1

class BBThread(Base):
    __tablename__ = 'bbthread'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(128), index=True, nullable=False)
    description = Column(Unicode(16384), default='')
    forum_id = Column(Integer, ForeignKey('bbforum.id'))
    forum = relationship("BBForum")
    view_count = Column(Integer, default=0, index=True)
    posts = relationship(BBPost, lazy="dynamic",
                         cascade="all, delete, delete-orphan")
    tags = relationship(BBTags, cascade="all, delete, delete-orphan")

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def total_posts(self):
        return self.posts.count()

class BBForum(Base):
    __tablename__ = 'bbforum'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(128), index=True, unique=True, nullable=False)
    category_id = Column(Integer, ForeignKey('bbcategory.id'))
    category = relationship("BBCategory")
    description = Column(Unicode(16384), default='')
    threads = relationship(BBThread)

    def __init__(self, name, description, category):
        self.name = name
        self.category = category
        self.description = description

    def total_threads(self):
        return len(self.threads)

    def total_posts(self):
        posts = 0
        for thread in self.threads:
            posts += thread.posts.count()
        return posts
