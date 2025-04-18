from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from time import time
import jwt
from flask import current_app as app
from app.search import add_to_index, remove_from_index, query_index

class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)   
        if total == 0:
            return [], 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        query = sa.select(cls).where(cls.id.in_(ids)).order_by(sa.case(*when, value=cls.id))
        return db.session.scalars(query), total
    
    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

        '''
        session._changes is a custom attribute — it's not built into SQLAlchemy. 
        This temporarily stores the objects being added, updated, or deleted during the session. 
        Then, in after_commit, you use this _changes dictionary to update or remove documents in the Elasticsearch index. 
        So, you're hijacking the session object briefly to carry some extra info through the commit process. 
        '''

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in db.session.scalars(sa.select(cls)):
            add_to_index(cls.__tablename__, obj)

db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)



'''
Flask-SQLAlchemy uses a "snake case" naming convention for database tables by default. 
For the User model below, the corresponding table in the database will be named user. 
For a AddressAndPhone model class, the table would be named address_and_phone. 
If you prefer to choose your own table names, you can add an attribute named __tablename__ 
to the model class, set to the desired name as a string.
'''

followers = db.Table('followers',
                     db.metadata,
                     sa.Column('follower_id', sa.Integer, sa.ForeignKey('user.id'),primary_key=True),
                     sa.Column('followed_id',sa.Integer, sa.ForeignKey('user.id'), primary_key=True)
                     )

class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True) 
    #so.Mapped: Provides precise type information for ORM-mapped attributes.
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,unique=True)
    '''
    You can skip sa.String if you're using type hints with so.Mapped[str] unless you want to specify a length like
    we have done above. The mapped_column() function can infer the datatype from the type hint.

    '''
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    #Optional: Optional typing hint from Python indicates that an attribute can be None.
    posts: so.WriteOnlyMapped['Post'] = so.relationship(
        back_populates='author')
    
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc))
    
    following: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers, primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        back_populates='followers')
    followers: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers, primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        back_populates='following')
    
    '''
    The User model has a posts relationship attribute that was configured with the WriteOnlyMapped generic type. 
    This is a special type of relationship that adds a select() method that returns a database query for the related items. 
    The u.posts.select() expression takes care of generating the query that links the user to its blog posts.

    Also note, so.WriteOnlyMapped['Post'] encloses the Post class name in single quotes. 
    This is necessary because the Post class is not yet defined. When a class needs to reference another class 
    that is defined below it, you cannot write the name directly, because Python will give you an error. 
    This is called a "forward reference". SQLAlchemy allows you to enter forward references as strings. 
    When the Post class references 'User', it is not a forward reference because 'User' is defined above 'Post', 
    so in that case a string is not necessary (but if you want to be consistent you can use a string on that one as well).

    '''
    
    '''
    SQLAlchemy introduced so.Mapped and so.mapped_column for better type safety and clarity in static type checking.
    '''

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def __repr__(self):
        return '<User {}>'.format(self.username)
    '''
    The __repr__ method tells Python how to print objects of this class, 
    which is going to be useful for debugging.
    '''

    def follow(self, user):
        if not self.is_following(user):
            self.following.add(user)
    
    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        query = self.following.select().where(User.id == user.id)
        return db.session.scalar(query) is not None
    
    def followers_count(self):
        query = sa.select(sa.func.count()).select_from(self.followers.select().subquery())
        # All write-only relationships have a select() method that constructs a query that returns all the elements in the relationship
        # Whenever a query is included as part of a larger query, SQLAlchemy requires the inner query to be converted to a sub-query by calling the subquery() method.
        return db.session.scalar(query)
    
    def following_count(self):
        query = sa.select(sa.func.count()).select_from(self.following.select().subquery())
        # All write-only relationships have a select() method that constructs a query that returns all the elements in the relationship
        # Whenever a query is included as part of a larger query, SQLAlchemy requires the inner query to be converted to a sub-query by calling the subquery() method.
        return db.session.scalar(query)
    
    def following_posts(self):
        Author = so.aliased(User)
        Follower = so.aliased(User)
        return (
            sa.select(Post)
            .join(Post.author.of_type(Author))
            .join(Author.followers.of_type(Follower), isouter=True)
            .where(sa.or_(
                Follower.id == self.id,
                Author.id == self.id,
            ))
            .group_by(Post)
            .order_by(Post.timestamp.desc())
        )
    
    '''
    The joined table now has all the posts, so I can expand the where() clause to include both posts from followed 
    users as well as own posts. SQLAlchemy provides the sa.or_(), sa.and_() and sa.not_() helpers to create compound 
    conditions. In this case I need to use sa.or_() to specify that I have two options for selecting posts.
    '''

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')
    
    # @staticmethod is similar to @classmethod but the former does not receive the class as the first argument 
    # and a static method does not have access to class variables (or instance variables).
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return db.session.get(User, id)

class Post(SearchableMixin, db.Model):
    __searchable__ = ['body']

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    '''
    When you pass a function as a default, SQLAlchemy will set the field to the value returned by the function.
    In general, you will want to work with UTC dates and times in a server application instead of the local time 
    where you are located. This ensures that you are using uniform timestamps regardless of where the users and 
    the server are located. These timestamps will be converted to the user's local time when they are displayed.

    "2021-06-28T21:45:23+00:00" is the format for ISO 8601 dates and times. The "+00:00" part at the end 
    of the string represents timezone offset from UTC and +00:00 means UTC. For instance, +05:30 offset 
    would mean 5 hours 30 minutes ahead of UTC (India Standard Time). Knowing this info will be important when
    we display the date and time on the web page. 
    '''
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'),index=True)
    author: so.Mapped[User] = so.relationship(back_populates='posts')
    language: so.Mapped[Optional[str]] = so.mapped_column(sa.String(5))

    def __repr__(self):
        return '<Post {}>'.format(self.body)
    

    

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

'''
Password Hashing:

scrypt - what werkzeug.security uses in our project
PBKDF2-HMAC-SHA256
bcrypt
Argon2

from werkzeug.security import generate_password_hash, check_password_hash
hash = generate_password_hash("riddhi111") # for hash generation
print(hash)
Output: 'scrypt:32768:8:1$fkVYrl07tgm2HqFB$282a7165dea1f493beb7cbac26cb4de54d8f8cbae7165f9601947dc07ef2be45d46c20fc96eaefcba6635265891eedab4fdf1e6f76e8f3ae84b4501e2f92aa50'

# The password is transformed into a long encoded string through a series of cryptographic operations that have no known 
# reverse operation, which means that a person that obtains the hashed password will be unable to use it to recover the 
# original password. As an additional measure, if you hash the same password multiple times, you will get different results, 
# since all hashed passwords get a different cryptographic salt, so this makes it impossible to identify if two users have the 
# same password by looking at their hashes.

print(check_password_hash(hash, "riddhi111")) # for verification
Output: True
'''
    
