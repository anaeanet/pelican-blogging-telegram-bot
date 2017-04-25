import sqlite3

from packages.bot.state.idlestate import IdleState

__author__ = 'anaeanet'


class SQLDBWrapper:

    def __init__(self, datbase_name):
        self.__conn = sqlite3.connect(datbase_name)

    def setup(self):

        # create required tables
        tblstmts = [  "CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY NOT NULL, is_authorized INTEGER DEFAULT 0 CHECK (is_authorized == 0 or is_authorized == 1), state TEXT NOT NULL)"
                    , "CREATE TABLE IF NOT EXISTS post (id INTEGER PRIMARY KEY NOT NULL, title TEXT NOT NULL, author TEXT NOT NULL, content TEXT, status TEXT DEFAULT 'draft' CHECK (status == 'draft' or status == 'published'), tmsp_create NUMERIC DEFAULT CURRENT_DATETIME, tmsp_publish NUMERIC)"
                    ]
        for stmt in tblstmts:
            self.__conn.execute(stmt)

        # create some indexes
        idxstmts = ["CREATE INDEX IF NOT EXISTS postTitle ON post (title ASC)"]
        for stmt in idxstmts:
            self.__conn.execute(stmt)

        self.__conn.commit()

    def get_users(self, user_id=None, is_authorized=None, state=None):
        stmt = "SELECT * FROM user WHERE"
        args = []

        if user_id is not None:
            stmt += " id = ? AND"
            args.append(user_id)
        else:
            stmt += " 1 = 1 AND"

        if is_authorized is not None:
            stmt += " is_authorized = ? AND"
            args.append(is_authorized)
        else:
            stmt += " 1 = 1 AND"

        if state is not None:
            stmt += " state = ?"
            args.append(state)
        else:
            stmt += " 1 = 1"

        args = tuple(args)
        return [x for x in self.__conn.execute(stmt, args)]

    def add_user(self, user_id, is_authorized, state):
        stmt = "INSERT INTO user (id, is_authorized, state) VALUES (?, ?, ?)"
        args = (user_id, 1 if is_authorized else 0, state)
        self.__conn.execute(stmt, args)
        self.__conn.commit()

    def update_user(self, user_id, is_authorized=None, state=None):
        stmt = "UPDATE user SET id = ?"
        args = [user_id]

        if is_authorized is not None:
            stmt += ", is_authorized = ?"
            args.append(1 if is_authorized else 0)

        if state is not None:
            stmt += ", state = ?"
            args.append(state)

        stmt += " WHERE id = ?"
        args.append(user_id)
        args = tuple(args)
        self.__conn.execute(stmt, args)
        self.__conn.commit()

    #-------------- not used yet -----------------------

    def create_post(self, title, user):
        stmt = "INSERT INTO post (title, author) VALUES (?, ?)"
        args = (title, user)
        self.__conn.execute(stmt, args)
        self.__conn.commit()

    def delete_post(self, title, user):
        stmt = "DELETE FROM post WHERE title = (?) and author = (?)"
        args = (title, user)
        self.__conn.execute(stmt, args)
        self.__conn.commit()

    def get_posts(self, user):
        stmt = "SELECT title FROM post WHERE author = (?)"
        args = (user, )
        return [x[0] for x in self.__conn.execute(stmt, args)]
