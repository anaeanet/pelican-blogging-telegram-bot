import sqlite3

__author__ = 'anaeanet'


class DBWrapper:

    def __init__(self, dbname="database.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def setup(self):
        tblstmts = ["CREATE TABLE IF NOT EXISTS post (id INTEGER PRIMARY KEY NOT NULL, title TEXT NOT NULL, "
                    + "author TEXT NOT NULL, content TEXT, status TEXT DEFAULT 'draft' CHECK (status == 'draft' or status == 'published'), "
                    + "tmsp_create NUMERIC DEFAULT CURRENT_DATETIME, tmsp_publish NUMERIC)"]
        idxstmts = ["CREATE INDEX IF NOT EXISTS postTitle ON post (title ASC)"]

        for stmt in tblstmts:
            self.conn.execute(stmt)

        for stmt in idxstmts:
            self.conn.execute(stmt)

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
