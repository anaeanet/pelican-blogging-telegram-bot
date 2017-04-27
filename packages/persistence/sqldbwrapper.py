import sqlite3
import importlib

__author__ = 'anaeanet'


class SQLDBWrapper:
    """
    Data Access Module (DAM) providing an interface 
    to separate bit implementation from specific database implementation.
    """

    def __init__(self, datbase_name):
        self.__conn = sqlite3.connect(datbase_name)

    def setup(self):

        # create required tables
        tblstmts = [  "CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY NOT NULL, is_authorized INTEGER DEFAULT 0 CHECK (is_authorized == 0 or is_authorized == 1), states TEXT NOT NULL)"
                    , "CREATE TABLE IF NOT EXISTS post (id INTEGER PRIMARY KEY NOT NULL, title TEXT NOT NULL, author TEXT NOT NULL, content TEXT, status TEXT DEFAULT 'draft' CHECK (status == 'draft' or status == 'published'), tmsp_create NUMERIC DEFAULT CURRENT_DATETIME, tmsp_publish NUMERIC)"
                    ]
        for stmt in tblstmts:
            self.__conn.execute(stmt)

        # create some indexes
        idxstmts = ["CREATE INDEX IF NOT EXISTS postTitle ON post (title ASC)"]
        for stmt in idxstmts:
            self.__conn.execute(stmt)

        self.__conn.commit()

    def __serialize_state(state):
        module = state.__module__
        klass = state.__class__.__name__
        return ".".join([module, klass])

    def __deserialize_state(self, module_dot_class):
        module, klass = module_dot_class.rsplit(".", 1)
        return getattr(importlib.import_module(module), klass)

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
            stmt += " states = ?"
            args.append(SQLDBWrapper.__serialize_state(state))
        else:
            stmt += " 1 = 1"

        args = tuple(args)
        return [dict({"user_id": x[0], "is_authorized": True if x[1] == 1 else False
                      , "state": self.__deserialize_state(x[2])}) for x in self.__conn.execute(stmt, args)]

    def add_user(self, user_id, is_authorized, state):
        stmt = "INSERT INTO user (id, is_authorized, states) VALUES (?, ?, ?)"
        args = (user_id, 1 if is_authorized else 0, SQLDBWrapper.__serialize_state(state))
        self.__conn.execute(stmt, args)
        self.__conn.commit()

    def update_user(self, user_id, is_authorized=None, state=None):
        """
        Fetches users from the database that fulfill *all* given criteria.
        If no criterion is specified, all users stored in the database are returned.
        If multiple criteria are specified, all of them need to be fulfilled for a user to be part of the result set.
        
        :param user_id: only users with given user_id are returned (at most 1 as user_id is primary key)
        :param is_authorized: only users with specified authorization flag (True/False) are returned
        :param state: only users with specified state are returned
        :return: a list of dicionaries where each dictionary represents one user (user_id, is_authorized, state_class)
        """

        stmt = "UPDATE user SET id = ?"
        args = [user_id]

        if is_authorized is not None:
            stmt += ", is_authorized = ?"
            args.append(1 if is_authorized else 0)

        if state is not None:
            stmt += ", states = ?"
            args.append(SQLDBWrapper.__serialize_state(state))

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
