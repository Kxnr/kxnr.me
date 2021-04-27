import flask
from flask_security.datastore import Datastore, SQLAlchemyDatastore, SQLAlchemyUserDatastore
from sqlalchemy.orm import joinedload
# from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, true
from models import User, Role, Content, Category, db
from werkzeug.local import LocalProxy

# TODO: change models to not need db instance
# db = SQLAlchemy()

def create_user_datastore():
    if flask.current_app:
        if "user_datastore" not in flask.g:
            flask.g["user_datastore"] = SQLAlchemyUserDatastore(db, User, Role)
        return flask.g
    else:
        return LocalProxy(lambda: SQLAlchemyUserDatastore(db, User, Role))


def create_content_datastore():
    if flask.current_app:
        if "user_datastore" not in flask.g:
            flask.g["user_datastore"] = SQLAlchemyContentDatastore(db, Content, Category)
        return flask.g
    else:
        return LocalProxy(lambda: SQLAlchemyContentDatastore(db, Content, Category))


class SQLAlchemyContentDatastore(SQLAlchemyDatastore, Datastore):

    def __init__(self, db, content_model, category_model):
        self.content_model = content_model
        self.category_model = category_model
        SQLAlchemyDatastore.__init__(self, db)

    def find_content(self, user=None, one=False, **kwargs):
        '''

         Note: this doesn't use the sensible default of only retrieving columns without
               permissions restrictions unless a user is passed in due to the implementation
               of the cli--this should be fixed once the query is functioning properly

        :param user:
        :param kwargs:
        :return:
        '''

        query = self.content_model.query
        query = query.options(joinedload("categories")).options(joinedload("required_roles"))
        # if this doesn't work, most likely need to use relational algebra to divide by user.roles

        # TODO
        if "categories" in kwargs:
            kwargs.pop("categories")

        if "required_roles" in kwargs:
            kwargs.pop("required_roles")

        query = query.filter_by(**kwargs)
            # .where(and_(*[r.in_(self.content_model.required_roles) for r in (user.roles if user else [])]))

        if one:
            return query.first()
        else:
            return query.all()

    def find_category(self, **kwargs):
        cat = self.category_model.query.filter_by(**kwargs).first()
        return cat

    def create_content(self, name, content, description, **kwargs):
        content_obj = self.find_content(name=name)
        if len(content_obj):
            return False

        kwargs["name"] = name
        kwargs["content"] = content
        kwargs["description"] = description

        self.put(self.content_model(**kwargs))
        return True

    def update_content(self, entry, **kwargs):
        for k, v in kwargs.items():
            setattr(entry, k, v)
        self.put(entry)
        return True

    def create_category(self, category, description):
        cat_obj = self.find_category(name=category)
        if cat_obj is not None:
            return False

        self.put(self.category_model(category=category,
                                     description=description))
        return True

    def add_content_to_category(self, content, category):
        if category not in content.categories:
            content.categories.append(category)
            self.put(content)
            return True
        return False

    def remove_content_from_category(self, content, category):
        if category in content.categories:
            content.categories.remove(category)
            self.put(content)
            return True
        return False
