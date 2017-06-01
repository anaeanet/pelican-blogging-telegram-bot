import sqlite3
import importlib
from packages.states.abstractuserpoststate import AbstractUserPostState

__author__ = 'anaeanet'


class SQLDBWrapper:
    """
    Data Access Module (DAM) providing an interface 
    to separate bot implementation from specific database implementation.
    """

    def __init__(self, datbase_name):
        self.__conn = sqlite3.connect(datbase_name)

    def setup(self):

        # create required tables
        tbl_stmts = [ "CREATE TABLE IF NOT EXISTS user (user_id INTEGER NOT NULL PRIMARY KEY"
                                                        + ", is_authorized INTEGER NOT NULL DEFAULT 0 CHECK (is_authorized == 0 or is_authorized == 1)"
                                                        + ", state TEXT NOT NULL)"

                    , "CREATE TABLE IF NOT EXISTS post (post_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT"
                                                        + ", user_id INTEGER NOT NULL"
                                                        + ", title TEXT NOT NULL"
                                                        + ", status TEXT NOT NULL DEFAULT 'draft' CHECK (status == 'draft' or status == 'published')"
                                                        + ", tmsp_create TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"
                                                        + ", content TEXT"
                                                        + ", title_image INTEGER"
                                                        + ", tmsp_publish TIMESTAMP"
                                                        + ", original_post_id INTEGER"
                                                        + ", FOREIGN KEY(user_id) REFERENCES user(user_id)"
                                                        + ", FOREIGN KEY(title_image) REFERENCES post_image(post_image_id)"
                                                        + ", FOREIGN KEY(original_post_id) REFERENCES post(post_id))"

                    , "CREATE TABLE IF NOT EXISTS tag (tag_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT"
                                                        + ", name TEXT NOT NULL UNIQUE)"

                    , "CREATE TABLE IF NOT EXISTS post_tag (post_tag_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT"
                                                        + ", post_id INTEGER NOT NULL"
                                                        + ", tag_id INTEGER NOT NULL"
                                                        + ", FOREIGN KEY(post_id) REFERENCES post(post_id)"
                                                        + ", FOREIGN KEY(tag_id) REFERENCES tag(tag_id))"

                    , "CREATE TABLE IF NOT EXISTS post_image (post_image_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT"
                                                        + ", post_id INTEGER NOT NULL"
                                                        + ", file_name TEXT NOT NULL"
                                                        + ", file_id TEXT NOT NULL"
                                                        + ", file BLOB NOT NULL"
                                                        + ", thumb_id TEXT"
                                                        + ", caption TEXT"
                                                        + ", FOREIGN KEY(post_id) REFERENCES post(post_id))"
                    ]
        for stmt in tbl_stmts:
            self.__conn.execute(stmt)

        # create some indexes
        # TODO
        idx_stmts = ["CREATE INDEX IF NOT EXISTS postTitle ON post (title ASC)"]
        for stmt in idx_stmts:
            self.__conn.execute(stmt)

        # make sure foreign keys are enforced
        fk_stmt = "PRAGMA foreign_keys = ON"
        self.__conn.execute(fk_stmt)

        self.__conn.commit()

    def __serialize_state(state):
        """ 
        Serializes any instance of IdleState through string representation 
        :return: <module>.<class>__message_id__<message_id_value>
        """
        module = state.__module__
        klass = state.__class__.__name__

        state_string = ".".join([module, klass]) + "__message_id__" + str(state.message_id)
        if isinstance(state, AbstractUserPostState):
            state_string += "__post_id__" + str(state.post_id)

        return state_string

    def __deserialize_state(module_class_params):
        module_dot_class, params = module_class_params.split("__", 1)
        param_list = params.split("__")

        module, klass = module_dot_class.rsplit(".", 1)
        param_dict = {param_list[i]: param_list[i+1] for i in range(0, len(param_list), 2)}

        return getattr(importlib.import_module(module), klass), param_dict

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

        param_dict = dict({key: value for key, value in locals().items() if key != "self" and value is not None})

        stmt = "SELECT * FROM user"
        args = []

        if len(param_dict) > 0:
            stmt += " WHERE " + " = ? AND ".join(param_dict.keys()) + " = ?"
            for key, value in param_dict.items():
                if key == "is_authorized":
                    args.append(1 if value else 0)
                elif key == "state":
                    args.append(SQLDBWrapper.__serialize_state(value))
                else:
                    args.append(value)

        return [dict({"user_id": x[0]
                        , "is_authorized": True if x[1] == 1 else False
                        , "state_class": SQLDBWrapper.__deserialize_state(x[2])}) for x in self.__conn.execute(stmt, tuple(args))]

    def add_user(self, user_id, is_authorized, state):
        stmt = "INSERT INTO user (user_id, is_authorized, state) VALUES (?, ?, ?)"
        args = [user_id, 1 if is_authorized else 0, SQLDBWrapper.__serialize_state(state)]

        cursor = self.__conn.cursor()
        cursor.execute(stmt, tuple(args))
        self.__conn.commit()

        return cursor.lastrowid

    def update_user(self, user_id, is_authorized=None, state=None):
        param_dict = dict({key: value for key, value in locals().items() if key != "self" and value is not None})

        stmt = "UPDATE user SET " + " = ?, ".join(param_dict.keys()) + " = ? WHERE user_id = ?"
        args = []

        for key, value in param_dict.items():
            if key == "is_authorized":
                args.append(1 if value else 0)
            elif key == "state":
                args.append(SQLDBWrapper.__serialize_state(value))
            else:
                args.append(value)
        args.append(user_id)

        cursor = self.__conn.cursor()
        cursor.execute(stmt, tuple(args))
        self.__conn.commit()

        return cursor.rowcount

    # -------------------------------------------------- post ----------------------------------------------------------

    def get_posts(self, post_id=None, user_id=None, title=None, status=None, tmsp_create=None, content=None, title_image=None, tmsp_publish=None, original_post_id=None):
        param_dict = dict({key: value for key, value in locals().items() if key != "self" and value is not None})

        stmt = "SELECT * FROM post"
        args = []

        if len(param_dict) > 0:
            stmt += " WHERE " + " = ? AND ".join(param_dict.keys()) + " = ?"
            for key, value in param_dict.items():
                args.append(value)

        return [dict({"post_id": x[0]
                        , "user_id": x[1]
                        , "title": x[2]
                        , "status": x[3]
                        , "tmsp_create": x[4]
                        , "content": x[5]
                        , "title_image": x[6]
                        , "tmsp_publish": x[7]
                        , "original_post_id": x[8]}) for x in self.__conn.execute(stmt, tuple(args))]

    def add_post(self, user_id, title, status=None, tmsp_create=None, content=None, title_image=None, tmsp_publish=None, original_post_id=None):
        param_dict = dict({key: value for key, value in locals().items() if key != "self" and value is not None})

        stmt = "INSERT INTO post (" + ",".join(param_dict.keys()) + ") VALUES (" + ",".join(["?" for x in param_dict.keys()]) + ")"
        args = []

        for key, value in param_dict.items():
            args.append(value)

        cursor = self.__conn.cursor()
        cursor.execute(stmt, tuple(args))
        self.__conn.commit()

        return cursor.lastrowid

    def delete_post(self, post_id):
        stmt = "DELETE FROM post WHERE post_id = ?"
        args = [post_id]

        cursor = self.__conn.cursor()
        cursor.execute(stmt, tuple(args))
        self.__conn.commit()

        return cursor.rowcount

    def update_post(self, post_id, user_id=None, title=None, status=None, tmsp_create=None, content=None, title_image=None, tmsp_publish=None, original_post_id=None):
        param_dict = dict({key: value for key, value in locals().items() if key != "self" and value is not None})

        stmt = "UPDATE post SET " + " = ?, ".join(param_dict.keys()) + " = ? WHERE post_id = ?"
        args = []

        for key, value in param_dict.items():
            args.append(value)
        args.append(post_id)

        cursor = self.__conn.cursor()
        cursor.execute(stmt, tuple(args))
        self.__conn.commit()

        return cursor.rowcount

    def delete_title_image(self, post_id):

        stmt = "UPDATE post SET title_image = NULL WHERE post_id = ?"
        args = [post_id]

        cursor = self.__conn.cursor()
        cursor.execute(stmt, tuple(args))
        self.__conn.commit()

    # -------------------------------------------------- tag -----------------------------------------------------------

    def get_tags(self, tag_id=None, name=None):
        param_dict = dict({key: value for key, value in locals().items() if key != "self" and value is not None})

        stmt = "SELECT * FROM tag"
        args = []

        if len(param_dict) > 0:
            stmt += " WHERE " + " = ? AND ".join(param_dict.keys()) + " = ?"
            for key, value in param_dict.items():
                args.append(value)

        return [dict({"tag_id": x[0]
                        , "name": x[1]}) for x in self.__conn.execute(stmt, tuple(args))]

    def add_tag(self, name):
        stmt = "INSERT INTO tag (name) VALUES (?)"
        args = [name]

        cursor = self.__conn.cursor()
        cursor.execute(stmt, tuple(args))
        self.__conn.commit()

        return cursor.lastrowid

    def delete_tag(self, tag_id):
        stmt = "DELETE FROM tag WHERE tag_id = ?"
        args = [tag_id]

        cursor = self.__conn.cursor()
        cursor.execute(stmt, tuple(args))
        self.__conn.commit()

        return cursor.rowcount

    # -------------------------------------------------- post_tag ------------------------------------------------------

    def get_post_tags(self, post_tag_id=None, post_id=None, tag_id=None):
        param_dict = dict({key: value for key, value in locals().items() if key != "self" and value is not None})

        stmt = "SELECT * FROM post_tag"
        args = []

        if len(param_dict) > 0:
            stmt += " WHERE " + " = ? AND ".join(param_dict.keys()) + " = ?"
            for key, value in param_dict.items():
                args.append(value)

        return [dict({"post_tag_id": x[0]
                        , "post_id": x[1]
                        , "tag_id": x[2]}) for x in self.__conn.execute(stmt, tuple(args))]

    def add_post_tag(self, post_id, tag_id):
        stmt = "INSERT INTO post_tag (post_id, tag_id) VALUES (?, ?)"
        args = [post_id, tag_id]

        cursor = self.__conn.cursor()
        cursor.execute(stmt, tuple(args))
        self.__conn.commit()

        return cursor.lastrowid

    def delete_post_tag(self, post_tag_id):
        stmt = "DELETE FROM post_tag WHERE post_tag_id = ?"
        args = [post_tag_id]

        cursor = self.__conn.cursor()
        cursor.execute(stmt, tuple(args))
        self.__conn.commit()

        return cursor.rowcount

    # -------------------------------------------------- post_image ----------------------------------------------------

    def get_post_images(self, post_image_id=None, post_id=None, file_name=None, file_id=None, file=None, thumb_id=None, caption=None):
        param_dict = dict({key: value for key, value in locals().items() if key != "self" and value is not None})

        stmt = "SELECT * FROM post_image"
        args = []

        if len(param_dict) > 0:
            stmt += " WHERE " + " = ? AND ".join(param_dict.keys()) + " = ?"
            for key, value in param_dict.items():
                args.append(value)

        return [dict({"post_image_id": x[0]
                        , "post_id": x[1]
                        , "file_name": x[2]
                        , "file_id": x[3]
                        , "file": x[4]
                        , "thumb_id": x[5]
                        , "caption": x[6]}) for x in self.__conn.execute(stmt, tuple(args))]

    def add_post_image(self, post_id, file_name, file_id, file, thumb_id=None, caption=None):
        param_dict = dict({key: value for key, value in locals().items() if key != "self" and value is not None})

        stmt = "INSERT INTO post_image (" + ",".join(param_dict.keys()) + ") VALUES (" + ",".join(["?" for x in param_dict.keys()]) + ")"
        args = []

        for key, value in param_dict.items():
            args.append(value)

        cursor = self.__conn.cursor()
        cursor.execute(stmt, tuple(args))
        self.__conn.commit()

        return cursor.lastrowid

    def delete_post_image(self, post_image_id):
        stmt = "DELETE FROM post_image WHERE post_image_id = ?"
        args = [post_image_id]

        cursor = self.__conn.cursor()
        cursor.execute(stmt, tuple(args))
        self.__conn.commit()

        return cursor.rowcount
