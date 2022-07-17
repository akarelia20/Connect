from unittest import result
from flask_app.config.mysqlconnection import MySQLConnection, connectToMySQL
from flask_app.models import influencer, company
from flask import flash
import re


URL_REGEX = re.compile(r'^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?')

class Post:
    db = 'connect'
    def __init__(self, data):
        self.id = data['id']
        self.title = data['title']
        self.category = data['category']
        self.social_platform= data['social_platform']
        self.url = data['url']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.influencer_id = data['influencer_id']
        self.poster = influencer.Influencer.get_influencer_by_id({"id": data['influencer_id']})
        # self.users = None
        # self.visitors = []

    @staticmethod
    def validate_post(data):
        is_valid = True
        if len(data["title"]) < 3:
            flash("Title must be atleast 3 characters", "error")
            is_valid = False
        if len(data["category"]) < 3:
            flash("Category must be selected", "error")
            is_valid = False
        if len(data["social_platform"]) == 0:
            flash("Please select one social platform to proceed further.", "error")
            is_valid = False
        if len(data["url"]) < 8:
            flash("Please enter valid URL", "error")
            is_valid = False 
        return is_valid

    @classmethod
    def save(cls,data):
        query = "INSERT INTO posts (title, category, social_platform, url, influencer_id) VALUES (%(title)s, %(category)s, %(social_platform)s, %(url)s, %(influencer_id)s);"
        return MySQLConnection(cls.db).query_db(query,data) 

    @classmethod
    def update(cls,data):
        query = "UPDATE posts SET title=%(title)s, category = %(category)s, social_platform= %(social_platform)s, url=%(url)s, WHERE id= %(id)s;"
        return MySQLConnection(cls.db).query_db(query,data)

    @classmethod
    def delete(cls,data):
        query = "DELETE from posts WHERE id = %(id)s"
        return MySQLConnection(cls.db).query_db(query,data)
    
    @classmethod
    def get_one_post(cls,data):
        query= "SELECT * from posts WHERE id = %(id)s;"
        results = MySQLConnection(cls.db).query_db(query, data)
        if len(results) < 1:
            return False
        return cls(results[0])
    
    @classmethod
    def update_post(cls,data):
        query = "UPDATE posts SET title=%(title)s, category = %(category)s, social_platform=%(social_platform)s, url=%(url)s WHERE id= %(id)s;"
        return MySQLConnection(cls.db).query_db(query,data)

    @classmethod
    def get_all_posts_withUser(cls):
        query = "SELECT * from posts"
        results= MySQLConnection(cls.db).query_db(query)
        posts= []
        for row in results:
            this_post = cls(row)
            posts.append(this_post)
        return posts
