import importlib
import sqlite3
from datetime import datetime
from packages.datamodel.user import User
from packages.datamodel.tag import Tag
from packages.datamodel.post import Post
from packages.datamodel.poststate import PostState
from packages.datamodel.gallery import Gallery
from packages.datamodel.image import Image

from packages.states.abstract.abstractuserpoststate import AbstractUserPostState

__author__ = 'anaeanet'


class DBWrapper:
    """
    Data Access Module (DAM) providing an interface
    to separate bot implementation from specific database implementation.
    """

    # TODO get rid of image id, use file_id
    # TODO re-introduce image_name in table

    def __init__(self, datbase_name):
        self.__conn = sqlite3.connect(datbase_name)

    def setup(self):

        # create required tables
        tbl_stmts = [
            "CREATE TABLE IF NOT EXISTS user (user_id INTEGER NOT NULL PRIMARY KEY"
                                                + ", state TEXT NOT NULL"
                                                + ", name TEXT)"

            , "CREATE TABLE IF NOT EXISTS post (post_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT"
                                                + ", user_id INTEGER NOT NULL"
                                                + ", title TEXT NOT NULL"
                                                + ", status TEXT NOT NULL"
                                                + ", gallery_title TEXT NOT NULL"
                                                + ", content TEXT NOT NULL"
                                                + ", title_image INTEGER"
                                                + ", tmsp_publish TIMESTAMP"
                                                + ", original_post INTEGER"
                                                + ", FOREIGN KEY(user_id) REFERENCES user(user_id)"
            #TODO add FK for title_image
                                                + ", FOREIGN KEY(original_post) REFERENCES post(post_id))"

            , "CREATE TABLE IF NOT EXISTS tag (tag_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT"
                                                + ", name TEXT NOT NULL UNIQUE)"

            , "CREATE TABLE IF NOT EXISTS post_tag (post_tag_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT"
                                                + ", post_id INTEGER NOT NULL"
                                                + ", tag_id INTEGER NOT NULL"
                                                + ", FOREIGN KEY(post_id) REFERENCES post(post_id)"
                                                + ", FOREIGN KEY(tag_id) REFERENCES tag(tag_id))"

            , "CREATE TABLE IF NOT EXISTS image (image_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT"
                                                + ", file_id TEXT NOT NULL UNIQUE"
                                                + ", file_name TEXT NOT NULL UNIQUE"
                                                + ", file BLOB NOT NULL"
                                                + ", thumb_id TEXT)"

            , "CREATE TABLE IF NOT EXISTS post_image (post_image_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT"
                                                + ", post_id INTEGER NOT NULL"
                                                + ", image_id INTEGER NOT NULL"
                                                + ", caption TEXT"
                                                + ", FOREIGN KEY(post_id) REFERENCES post(post_id)"
                                                + ", FOREIGN KEY(image_id) REFERENCES image(image_id))"
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

    @staticmethod
    def __serialize_state(state):
        """ Serializes any instance of AbstractUserState
        :param state (:class:`AbstractUserState`): the state to be serialized
        :return str: <module>.<class>__message_id__<message_id_value> + (__post_id__<post_id_value> if state instanceof AbstractUserPostState)
        """
        module = state.__module__
        klass = state.__class__.__name__

        state_string = ".".join([module, klass]) + "__message_id__" + str(state.message_id)
        if isinstance(state, AbstractUserPostState):
            state_string += "__post_id__" + str(state.post_id)

        return state_string

    @staticmethod
    def __deserialize_state(module_class_params):
        module_dot_class, params = module_class_params.split("__", 1)
        param_list = params.split("__")

        module, klass = module_dot_class.rsplit(".", 1)
        param_dict = {param_list[i]: param_list[i+1] for i in range(0, len(param_list), 2)}

        return getattr(importlib.import_module(module), klass), param_dict

    # -------------------------------------------------- commit/rollback -----------------------------------------------

    def commit(self):
        self.__conn.commit()

    def rollback(self):
        self.__conn.rollback()

    # -------------------------------------------------- user ----------------------------------------------------------

    def get_users(self, user_id=None, state=None, name=None):
        param_dict = dict({key: value for key, value in locals().items() if key not in ["self"] and value is not None})

        stmt = "SELECT * FROM user"
        args = []

        if len(param_dict) > 0:
            stmt += " WHERE " + " = ? AND ".join(param_dict.keys()) + " = ?"
            for key, value in param_dict.items():
                if key == "state":
                    args.append(self.__serialize_state(value))
                else:
                    args.append(value)

        return [User(x[0], self.__deserialize_state(x[1]), name=x[2]) for x in self.__conn.execute(stmt, tuple(args))]

    def get_user(self, user_id):
        user = None

        users = self.get_users(user_id=user_id)
        if len(users) == 1:
            user = users[0]

        return user

    def add_user(self, user_id, state, name=None, commit=True):
        param_dict = dict({key: value for key, value in locals().items() if key not in ["self", "commit"] and value is not None})

        stmt = "INSERT INTO user (" + ",".join(param_dict.keys()) + ") VALUES (" + ",".join(["?" for x in param_dict.keys()]) + ")"
        args = []

        for key, value in param_dict.items():
            if key == "state":
                args.append(self.__serialize_state(value))
            else:
                args.append(value)

        cursor = self.__conn.cursor()
        cursor.execute(stmt, tuple(args))
        if commit:
            self.__conn.commit()

        return self.get_user(cursor.lastrowid)

    def update_user(self, user_id, state, name, commit=True):
        param_dict = dict({key: value for key, value in locals().items() if key not in ["self", "commit"] and value is not None})

        stmt = "UPDATE user SET " + " = ?, ".join(param_dict.keys()) + " = ? WHERE user_id = ?"
        args = []

        for key, value in param_dict.items():
            if key == "state":
                args.append(self.__serialize_state(value))
            else:
                args.append(value)
        args.append(user_id)

        cursor = self.__conn.cursor()
        cursor.execute(stmt, tuple(args))
        if commit:
            self.__conn.commit()

        return self.get_user(user_id) if cursor.rowcount > 0 else None

    def delete_user(self, user_id, commit=True):
        user = self.get_user(user_id)
        cursor = self.__conn.cursor()

        if user is not None:

            # attempt to delete all user posts, rollback in case of failure
            for post in self.get_posts(user_id=user.id):
                deleted_post = self.delete_post(post.id, commit=False)
                if deleted_post is None:
                    self.__conn.rollback()
                    return None

        stmt = "DELETE FROM user WHERE user_id = ?"
        args = [user_id]
        cursor.execute(stmt, tuple(args))
        if commit:
            self.__conn.commit()

        return user if cursor.rowcount > 0 else None

    # -------------------------------------------------- post ----------------------------------------------------------

    def get_posts(self, post_id=None, user_id=None, title=None, status=None, gallery_title=None, content=None, title_image=None, tmsp_publish=None, original_post=None):
        param_dict = dict({key: value for key, value in locals().items() if key not in ["self"] and value is not None})

        stmt = "SELECT * FROM post"
        args = []

        if len(param_dict) > 0:
            stmt += " WHERE " + " = ? AND ".join(param_dict.keys()) + " = ?"
            for key, value in param_dict.items():
                if key == "tmsp_publish":
                    args.append(value.strftime("%Y-%m-%d %H:%M:%S.%f") if value is not None else None)
                elif key == "status":
                    args.append(value.value)
                else:
                    args.append(value)

        posts = []
        for p in [post for post in self.__conn.execute(stmt, tuple(args))]:
            p_post_id = p[0]
            p_user = self.get_user(p[1])
            p_title = p[2]
            p_status = PostState(p[3])
            p_gallery_title = p[4]
            p_content = p[5]

            p_title_image = None
            p_gallery_images = []
            post_images = self.get_post_images(post_id=post_id)
            for post_image in post_images:

                # set title_image
                if post_image.id == p[6]:
                    p_title_image = post_image
                else:
                    # add to gallery images
                    p_gallery_images.append(post_image)

            p_tmsp_publish = p[7]
            p_original_post = p[8]

            posts.append(
                Post(p_post_id, p_user, p_title, p_status
                    , content=p_content
                    , tags=self.get_post_tags(post_id=p_post_id)
                    , title_image=p_title_image
                    , gallery=Gallery(p_gallery_title, p_gallery_images)
                    , tmsp_publish=datetime.strptime(p_tmsp_publish, "%Y-%m-%d %H:%M:%S.%f") if p_tmsp_publish is not None else None
                    , original_post=self.get_post(post_id=p_original_post) if p_original_post is not None else None)
            )

        return posts

    def get_post(self, post_id):
        post = None

        posts = self.get_posts(post_id)
        if len(posts) == 1:
            post = posts[0]

        return post

    def add_post(self, user_id, title, status, gallery_title, content, title_image=None, tmsp_publish=None, original_post=None, commit=True):
        param_dict = dict({key: value for key, value in locals().items() if key not in ["self", "commit"] and value is not None})

        stmt = "INSERT INTO post (" + ",".join(param_dict.keys()) + ") VALUES (" + ",".join(["?" for x in param_dict.keys()]) + ")"
        args = []

        for key, value in param_dict.items():
            if key == "tmsp_publish":
                args.append(value.strftime("%Y-%m-%d %H:%M:%S.%f") if value is not None else None)
            elif key == "status":
                args.append(value.value)
            else:
                args.append(value)

        cursor = self.__conn.cursor()
        cursor.execute(stmt, tuple(args))
        if commit:
            self.__conn.commit()

        return self.get_post(cursor.lastrowid)

    def copy_post(self, post_id):
        copy_post = None

        post = self.get_post(post_id)
        if post is not None:

            new_post = self.add_post(post.user.id, post.title, PostState.DRAFT, post.gallery.title, post.content
                                     , title_image=None if post.title_image is None else post.title_image.id
                                     , original_post=post.id
                                     , commit=False)
            if new_post is not None:

                # add tags to new post
                for tag in post.tags:
                    self.add_post_tag(new_post.id, tag.name, commit=False)

                # copy title image
                if post.title_image is not None:
                    self.add_post_image(new_post.id, post.title_image.file_id, post.title_image.name, post.title_image.file, thumb_id=post.title_image.thumb_id, caption=post.title_image.caption, commit=False)
                    self.update_post(new_post.id, new_post.user.id, new_post.title, new_post.status
                                     , new_post.gallery.title
                                     , new_post.content
                                     , post.title_image.id
                                     , new_post.tmsp_publish
                                     , new_post.original_post.id
                                     , commit=False)

                # add gallery to new post
                if post.gallery is not None:
                    for image in post.gallery.images:
                        self.add_post_image(new_post.id, image.file_id, image.name, image.file
                                            , thumb_id=image.thumb_id
                                            , caption=image.caption
                                            , commit=False)

                new_post = self.get_post(new_post.id)

                # check if copy was successful
                if new_post.tags == post.tags and new_post.title_image == post.title_image and new_post.gallery == post.gallery:
                    copy_post = new_post
                    self.__conn.commit()
                else:
                    self.__conn.rollback()

            else:
                self.__conn.rollback()

        return copy_post

    def update_post(self, post_id, user_id, title, status, gallery_title, content, title_image, tmsp_publish, original_post, commit=True):
        param_dict = dict({key: value for key, value in locals().items() if key not in ["self", "commit"]})

        stmt = "UPDATE post SET " + " = ?, ".join(param_dict.keys()) + " = ? WHERE post_id = ?"
        args = []

        for key, value in param_dict.items():
            if key == "tmsp_publish":
                args.append(value.strftime("%Y-%m-%d %H:%M:%S.%f") if value is not None else None)
            elif key == "status":
                args.append(value.value)
            else:
                args.append(value)
        args.append(post_id)

        cursor = self.__conn.cursor()
        cursor.execute(stmt, tuple(args))
        if commit:
            self.__conn.commit()

        return self.get_post(post_id) if cursor.rowcount > 0 else None

    def delete_post(self, post_id, commit=True):
        post = self.get_post(post_id)
        cursor = self.__conn.cursor()

        if post is not None:

            # attempt to delete all tags, rollback in case of failure
            for tag in post.tags:
                deleted_tag = self.delete_post_tag(post.id, tag.id, commit=False)
                if deleted_tag is None:
                    self.__conn.rollback()
                    return None

            # un-set title image, then attempt to delete it, rollback in case of failure
            if post.title_image is not None:
                updated_post = self.update_post(post_id, post.user.id, post.title, post.status
                                                , post.gallery.title
                                                , post.content
                                                , None
                                                , post.tmsp_publish
                                                , None if post.original_post is None else post.original_post.id
                                                , commit=False)

                if updated_post is not None and updated_post.title_image is None:
                    deleted_image = self.delete_post_image(post.id, post.title_image.id)

                if updated_post is None or deleted_image is None:
                    self.__conn.rollback()
                    return None

            # attempt to delete all images in gallery, rollback in case of failure
            for image in post.gallery.images:
                deleted_image = self.delete_post_image(post.id, image.id)
                if deleted_image is None:
                    self.__conn.rollback()
                    return None

        stmt = "DELETE FROM post WHERE post_id = ?"
        args = [post_id]
        cursor.execute(stmt, tuple(args))
        if commit:
            self.__conn.commit()

        if cursor.rowcount == 0:
            post = None

        return post

    # -------------------------------------------------- post_tag ------------------------------------------------------

    def get_post_tags(self, post_tag_id=None, post_id=None, tag_id=None):
        param_dict = dict({key: value for key, value in locals().items() if key not in ["self"] and value is not None})

        stmt = "SELECT * FROM post_tag"
        args = []

        if len(param_dict) > 0:
            stmt += " WHERE " + " = ? AND ".join(param_dict.keys()) + " = ?"
            for key, value in param_dict.items():
                args.append(value)

        tags = []
        for pt in [post_tag for post_tag in self.__conn.execute(stmt, tuple(args))]:
            pt_tag_id = pt[2]

            tags.append(self.get_tag(pt_tag_id))

        return tags

    def get_post_tag(self, post_id, tag_id):
        post_tag = None

        post_tags = self.get_post_tags(post_id=post_id, tag_id=tag_id)
        if len(post_tags) == 1:
            post_tag = post_tags[0]

        return post_tag

    def add_post_tag(self, post_id, name, commit=True):

        # if tag already exists fetch it, otherwise add new tag record
        tags = self.get_tags(name=name)
        if len(tags) == 1:
            tag = tags[0]
        else:
            tag = self.add_tag(name, commit=False)

        if tag is not None and self.get_post_tag(post_id, tag.id) is None:

            stmt = "INSERT INTO post_tag (post_id, tag_id) VALUES (?, ?)"
            args = [post_id, tag.id]

            cursor = self.__conn.cursor()
            cursor.execute(stmt, tuple(args))
            if commit:
                self.__conn.commit()

            post_tag = self.get_post_tag(post_id, tag.id) if cursor.lastrowid > 0 else None

        else:
            post_tag = None

        return post_tag

    def delete_post_tag(self, post_id, tag_id, commit=True):
        post_tag = self.get_post_tag(post_id, tag_id)
        cursor = self.__conn.cursor()

        stmt = "DELETE FROM post_tag WHERE post_id = ? AND tag_id = ?"
        args = [post_id, tag_id]
        cursor.execute(stmt, tuple(args))
        if commit:
            self.__conn.commit()

        if cursor.rowcount > 0:
            # if tag not used in any other post delete it
            tags = self.get_post_tags(tag_id=tag_id)
            if len(tags) == 0:
                self.delete_tag(tag_id)

        return post_tag if cursor.rowcount > 0 else None

    # -------------------------------------------------- post_image ----------------------------------------------------

    def get_post_images(self, post_image_id=None, post_id=None, image_id=None, caption=None):
        param_dict = dict({key: value for key, value in locals().items() if key not in ["self"] and value is not None})

        stmt = "SELECT * FROM post_image"
        args = []

        if len(param_dict) > 0:
            stmt += " WHERE " + " = ? AND ".join(param_dict.keys()) + " = ?"
            for key, value in param_dict.items():
                args.append(value)

        post_images = []
        for img in [x for x in self.__conn.execute(stmt, tuple(args))]:
            image = self.get_image(img[2])
            post_images.append(Image(image.id, image.name, image.file_id, image.file, thumb_id=image.thumb_id, caption=img[3]))

        return post_images

    def get_post_image(self, post_id, image_id):
        post_image = None

        post_images = self.get_post_images(post_id=post_id, image_id=image_id)
        if len(post_images) == 1:
            post_image = post_images[0]

        return post_image

    def add_post_image(self, post_id, file_id, file_name, file, thumb_id=None, caption=None, commit=True):
        param_dict = dict({key: value for key, value in locals().items() if key in ["post_id", "caption"] and value is not None})

        # if image already exists fetch it, otherwise add new image record
        images = self.get_images(file_id=file_id)
        if len(images) == 1:
            image = images[0]
        else:
            image = self.add_image(file_id, file_name, file, thumb_id=thumb_id, commit=False)

        if image is not None and self.get_post_image(post_id, image.id) is None:
            param_dict["image_id"] = image.id

            stmt = "INSERT INTO post_image (" + ",".join(param_dict.keys()) + ") VALUES (" + ",".join(["?" for x in param_dict.keys()]) + ")"
            args = []

            for key, value in param_dict.items():
                args.append(value)

            cursor = self.__conn.cursor()
            cursor.execute(stmt, tuple(args))
            if commit:
                self.__conn.commit()

            post_image = self.get_post_image(post_id, image.id) if cursor.lastrowid > 0 else None

        else:
            post_image = None

        return post_image

    def delete_post_image(self, post_id, image_id, commit=True):
        post_image = self.get_post_image(post_id, image_id)
        cursor = self.__conn.cursor()

        stmt = "DELETE FROM post_image WHERE post_id = ? AND image_id = ?"
        args = [post_id, image_id]
        cursor.execute(stmt, tuple(args))
        if commit:
            self.__conn.commit()

        if cursor.rowcount > 0:
            # if image not used in any other post delete it
            images = self.get_post_images(image_id=image_id)
            if len(images) == 0:
                self.delete_image(image_id)

        return post_image if cursor.rowcount > 0 else None

    # -------------------------------------------------- tag -----------------------------------------------------------

    # TODO make tag methods private?

    def get_tags(self, tag_id=None, name=None):
        param_dict = dict({key: value for key, value in locals().items() if key not in ["self"] and value is not None})

        stmt = "SELECT * FROM tag"
        args = []

        if len(param_dict) > 0:
            stmt += " WHERE " + " = ? AND ".join(param_dict.keys()) + " = ?"
            for key, value in param_dict.items():
                args.append(value)

        return [Tag(x[0], x[1]) for x in self.__conn.execute(stmt, tuple(args))]

    def get_tag(self, tag_id):
        tag = None

        tags = self.get_tags(tag_id=tag_id)
        if len(tags) == 1:
            tag = tags[0]

        return tag

    def add_tag(self, name, commit=True):
        stmt = "INSERT INTO tag (name) VALUES (?)"
        args = [name]

        cursor = self.__conn.cursor()
        cursor.execute(stmt, tuple(args))
        if commit:
            self.__conn.commit()

        return self.get_tag(cursor.lastrowid)

    def delete_tag(self, tag_id, commit=True):
        tag = self.get_tag(tag_id)
        cursor = self.__conn.cursor()

        stmt = "DELETE FROM tag WHERE tag_id = ?"
        args = [tag_id]
        cursor.execute(stmt, tuple(args))
        if commit:
            self.__conn.commit()

        return tag if cursor.rowcount > 0 else None

    # -------------------------------------------------- image ---------------------------------------------------------

    # TODO make image methods private?

    def get_images(self, image_id=None, file_id=None, file=None, thumb_id=None):
        param_dict = dict({key: value for key, value in locals().items() if key not in ["self"] and value is not None})

        stmt = "SELECT * FROM image"
        args = []

        if len(param_dict) > 0:
            stmt += " WHERE " + " = ? AND ".join(param_dict.keys()) + " = ?"
            for key, value in param_dict.items():
                args.append(value)

        return [Image(x[0], x[2], x[1], x[3], thumb_id=x[4]) for x in self.__conn.execute(stmt, tuple(args))]

    def get_image(self, image_id):
        image = None

        images = self.get_images(image_id=image_id)
        if len(images) == 1:
            image = images[0]

        return image

    def add_image(self, file_id, file_name, file, thumb_id=None, commit=True):
        param_dict = dict({key: value for key, value in locals().items() if key not in ["self", "commit"] and value is not None})

        stmt = "INSERT INTO image (" + ",".join(param_dict.keys()) + ") VALUES (" + ",".join(["?" for x in param_dict.keys()]) + ")"
        args = []

        for key, value in param_dict.items():
            args.append(value)

        cursor = self.__conn.cursor()
        cursor.execute(stmt, tuple(args))
        if commit:
            self.__conn.commit()

        return self.get_image(cursor.lastrowid)

    def delete_image(self, image_id, commit=True):
        image = self.get_image(image_id)
        cursor = self.__conn.cursor()

        stmt = "DELETE FROM image WHERE image_id = ?"
        args = [image_id]
        cursor.execute(stmt, tuple(args))
        if commit:
            self.__conn.commit()

        return image if cursor.rowcount > 0 else None