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
        tbl_stmts = [ "CREATE TABLE IF NOT EXISTS user (id INTEGER NOT NULL PRIMARY KEY"
                                                        + ", is_authorized INTEGER NOT NULL DEFAULT 0 CHECK (is_authorized == 0 or is_authorized == 1)"
                                                        + ", state TEXT NOT NULL)"
                    , "CREATE TABLE IF NOT EXISTS post (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT"
                                                        + ", user_id INTEGER NOT NULL"
                                                        + ", title TEXT NOT NULL"
                                                        + ", status TEXT NOT NULL DEFAULT 'draft' CHECK (status == 'draft' or status == 'published')"
                                                        + ", tmsp_create TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"
                                                        + ", is_selected INTEGER NOT NULL DEFAULT 0 CHECK (is_selected == 0 or is_selected == 1)"
                                                        + ", content TEXT"
                                                        + ", tmsp_publish TIMESTAMP"
                                                        + ", FOREIGN KEY(user_id) REFERENCES user(id))"
                    ]
        for stmt in tbl_stmts:
            self.__conn.execute(stmt)

        # create some indexes
        # TODO
        idx_stmts = ["CREATE INDEX IF NOT EXISTS postTitle ON post (title ASC)"]
        for stmt in idx_stmts:
            self.__conn.execute(stmt)

        self.__conn.commit()

    def __serialize_state(state):
        module = state.__module__
        klass = state.__class__.__name__
        return ".".join([module, klass])

    def __deserialize_state(self, module_dot_class):
        module, klass = module_dot_class.rsplit(".", 1)
        return getattr(importlib.import_module(module), klass)

    # -------------------------------------------------- user ----------------------------------------------------------

    def get_users(self, user_id=None, is_authorized=None, state=None):
        """
        Fetches users from the database that fulfill *all* given criteria.
        If no criterion is specified, all users stored in the database are returned.
        If multiple criteria are specified, all of them need to be fulfilled for a user to be part of the result set.

        :param user_id: only users with given user_id are returned (at most 1 as user_id is primary key)
        :param is_authorized: only users with specified authorization flag (True/False) are returned
        :param state: only users with specified state are returned
        :return: a list of dictionaries where each dictionary represents one user (user_id, is_authorized, state_class)
        """

        stmt = "SELECT * FROM user WHERE"
        args = []

        if user_id is not None:
            stmt += " id = ? AND"
            args.append(user_id)
        else:
            stmt += " 1 = 1 AND"

        if is_authorized is not None:
            stmt += " is_authorized = ? AND"
            args.append(1 if is_authorized else 0)
        else:
            stmt += " 1 = 1 AND"

        if state is not None:
            stmt += " state = ?"
            args.append(SQLDBWrapper.__serialize_state(state))
        else:
            stmt += " 1 = 1"

        args = tuple(args)
        return [dict({"user_id": x[0]
                         , "is_authorized": True if x[1] == 1 else False
                         , "state_class": self.__deserialize_state(x[2])}) for x in self.__conn.execute(stmt, args)]

    def add_user(self, user_id, is_authorized, state):
        stmt = "INSERT INTO user (id, is_authorized, state) VALUES (?, ?, ?)"
        args = (user_id, 1 if is_authorized else 0, SQLDBWrapper.__serialize_state(state))
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
            args.append(SQLDBWrapper.__serialize_state(state))

        stmt += " WHERE id = ?"
        args.append(user_id)
        args = tuple(args)
        self.__conn.execute(stmt, args)
        self.__conn.commit()

    # -------------------------------------------------- post ----------------------------------------------------------

    def get_posts(self, post_id=None, user_id=None, title=None, status=None, tmsp_create=None, is_selected=None, content=None, tmsp_publish=None):
        stmt = "SELECT * FROM post WHERE"
        args = []

        if post_id is not None:
            stmt += " id = ? AND"
            args.append(post_id)
        else:
            stmt += " 1 = 1 AND"

        if user_id is not None:
            stmt += " user_id = ? AND"
            args.append(user_id)
        else:
            stmt += " 1 = 1 AND"

        if title is not None:
            stmt += " title = ? AND"
            args.append(title)
        else:
            stmt += " 1 = 1 AND"

        if status is not None:
            stmt += " status = ? AND"
            args.append(status)
        else:
            stmt += " 1 = 1 AND"

        if tmsp_create is not None:
            stmt += " tmsp_create = ? AND"
            args.append(tmsp_create)
        else:
            stmt += " 1 = 1 AND"

        if is_selected is not None:
            stmt += " is_selected = ? AND"
            args.append(1 if is_selected else 0)
        else:
            stmt += " 1 = 1 AND"

        if content is not None:
            stmt += " content = ? AND"
            args.append(content)
        else:
            stmt += " 1 = 1 AND"

        if tmsp_publish is not None:
            stmt += " tmsp_publish = ?"
            args.append(tmsp_publish)
        else:
            stmt += " 1 = 1"

        args = tuple(args)
        return [dict({"post_id": x[0]
                         , "user_id": x[1]
                         , "title": x[2]
                         , "status": x[3]
                         , "tmsp_create": x[4]
                         , "is_selected": True if x[5] == 1 else False
                         , "content": x[6]
                         , "tmsp_publish": x[7]}) for x in self.__conn.execute(stmt, args)]

    def add_post(self, user_id, title, status=None, tmsp_create=None, is_selected=None, content=None, tmsp_publish=None):
        column_list = ["title", "user_id"]
        args = [title, user_id]

        if status is not None:
            column_list.append("status")
            args.append(status)

        if tmsp_create is not None:
            column_list.append("tmsp_create")
            args.append(tmsp_create)

        if is_selected is not None:
            column_list.append("is_selected")
            args.append(1 if is_selected else 0)

        if content is not None:
            column_list.append("content")
            args.append(content)

        if tmsp_publish is not None:
            column_list.append("tmsp_publish")
            args.append(tmsp_publish)

        stmt = "INSERT INTO post (" + ",".join(column_list) + ") VALUES (" + ",".join(["?" for x in column_list]) + ")"
        args = tuple(args)
        self.__conn.execute(stmt, args)
        self.__conn.commit()

    def delete_post(self, post_id):
        stmt = "DELETE FROM post WHERE id = ?"
        args = (post_id, )
        self.__conn.execute(stmt, args)
        self.__conn.commit()

    def update_post(self, post_id, user_id=None, title=None, status=None, tmsp_create=None, is_selected=None, content=None, tmsp_publish=None):
        stmt = "UPDATE post SET id = ?"
        args = [post_id]

        if user_id is not None:
            stmt += ", user_id = ?"
            args.append(user_id)

        if title is not None:
            stmt += ", title = ?"
            args.append(title)

        if status is not None:
            stmt += ", status = ?"
            args.append(status)

        if tmsp_create is not None:
            stmt += ", tmsp_create = ?"
            args.append(tmsp_create)

        if is_selected is not None:
            stmt += ", is_selected = ?"
            args.append(1 if is_selected else 0)

        if content is not None:
            stmt += ", content = ?"
            args.append(content)

        if tmsp_publish is not None:
            stmt += ", user_id = ?"
            args.append(tmsp_publish)

        stmt += " WHERE id = ?"
        args.append(post_id)
        args = tuple(args)
        self.__conn.execute(stmt, args)
        self.__conn.commit()