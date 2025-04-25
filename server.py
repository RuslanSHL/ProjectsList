import os
os.system('color')

from data import db_session
from data.users import User
from data.posts import Post
from data.comments import Comment

if __name__ == '__main__':
    import os
    os.system('color')
    db_session.global_init('db/database.db')
