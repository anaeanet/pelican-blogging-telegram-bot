import sqlite3

from packages.persistence.abstractdatabasewrapper import AbstractDatabaseWrapper
from packages.bot.state.idlestate import IdleState

__author__ = 'anaeanet'


class PelicanMarkdownDatabaseWrapper(AbstractDatabaseWrapper):

    def setup(self):

        # create required tables
        tblstmts = [  "CREATE TABLE IF NOT EXISTS state (name TEXT PRIMARY KEY NOT NULL, is_start_state INTEGER DEFAULT 0 CHECK (is_start_state == 0 or is_start_state == 1))"
                    , "CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY NOT NULL, is_authorized INTEGER DEFAULT 0 CHECK (is_authorized == 0 or is_authorized == 1), state TEXT NOT NULL)"
                    , "CREATE TABLE IF NOT EXISTS post (id INTEGER PRIMARY KEY NOT NULL, title TEXT NOT NULL, author TEXT NOT NULL, content TEXT, status TEXT DEFAULT 'draft' CHECK (status == 'draft' or status == 'published'), tmsp_create NUMERIC DEFAULT CURRENT_DATETIME, tmsp_publish NUMERIC)"
                    ]
        for stmt in tblstmts:
            self.conn.execute(stmt)

        # create some indexes
        idxstmts = ["CREATE INDEX IF NOT EXISTS postTitle ON post (title ASC)"]
        for stmt in idxstmts:
            self.conn.execute(stmt)

        start_state = IdleState.__name__                #IdleState is star state for blog bot
        if not self.get_start_state():
            self.add_state(start_state, True)

        authorized_user = 319920852                     #telegram-user: @anaea_net
        if len(self.get_user(authorized_user)) < 1:
            self.add_user(authorized_user, True, self.get_start_state())

        self.conn.commit()

    def get_states(self):
        stmt = "SELECT * FROM state"
        return [x for x in self.conn.execute(stmt)]

    def get_start_state(self):
        result_set = [x[0] for x in self.get_states() if x[1] == 1]
        return result_set[0] if len(result_set) == 1 else None

    def add_state(self, name, is_start_state):
        #constraint: only allow start state if there hasn't been any defined already
        stmt = "INSERT INTO state (name, is_start_state) SELECT ?, ? WHERE NOT EXISTS (SELECT * FROM state WHERE is_start_state == 1)"
        args = (name, 1 if is_start_state else 0)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_users(self):
        stmt = "SELECT * FROM user"
        return [x for x in self.conn.execute(stmt)]

    def get_user(self, user_id):
        return [x for x in self.get_users() if x[0] == user_id]

    def add_user(self, user_id, is_authorized, state):
        stmt = "INSERT INTO user (id, is_authorized, state) VALUES (?, ?, ?)"
        args = (user_id, 1 if is_authorized else 0, state)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def create_post(self, title, user):
        stmt = "INSERT INTO post (title, author) VALUES (?, ?)"
        args = (title, user)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_post(self, title, user):
        stmt = "DELETE FROM post WHERE title = (?) and author = (?)"
        args = (title, user)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_posts(self, user):
        stmt = "SELECT title FROM post WHERE author = (?)"
        args = (user, )
        return [x[0] for x in self.conn.execute(stmt, args)]
