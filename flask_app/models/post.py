from unittest import result
from flask_app.config.mysqlconnection import MySQLConnection, connectToMySQL
from flask_app.models import influencer, company
from flask import flash
import re


URL_REGEX = re.compile(
    r'^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?')


class Post:
    db = 'connect'

    def __init__(self, data):
        self.id = data['id']
        self.title = data['title']
        self.category = data['category']
        self.social_platform = data['social_platform']
        self.url = data['url']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.influencer_id = data['influencer_id']
        self.tiktok_post_id = 0
        self.poster = influencer.Influencer.get_influencer_by_id(
            {"id": data['influencer_id']})
        self.liked_by = []
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
    def save(cls, data):
        query = "INSERT INTO posts (title, category, social_platform, url, influencer_id, tiktok_post_id) VALUES (%(title)s, %(category)s, %(social_platform)s, %(url)s, %(influencer_id)s, 0);"
        return MySQLConnection(cls.db).query_db(query, data)

    @classmethod
    def update(cls, data):
        query = "UPDATE posts SET title=%(title)s, category = %(category)s, social_platform= %(social_platform)s, url=%(url)s, WHERE id= %(id)s;"
        return MySQLConnection(cls.db).query_db(query, data)

    @classmethod
    def delete(cls, data):
        query = "DELETE from posts WHERE id = %(id)s"
        return MySQLConnection(cls.db).query_db(query, data)

    @classmethod
    def get_one_post(cls, data):
        query = "SELECT * from posts WHERE id = %(id)s;"
        results = MySQLConnection(cls.db).query_db(query, data)
        if len(results) < 1:
            return False
        return cls(results[0])

    @classmethod
    def update_post(cls, data):
        query = "UPDATE posts SET title=%(title)s, category = %(category)s, social_platform=%(social_platform)s, url=%(url)s WHERE id= %(id)s;"
        return MySQLConnection(cls.db).query_db(query, data)

    @classmethod
    def get_all_posts_withUser_likedby(cls):
        query = "SELECT * from posts LEFT JOIN likes ON posts.id = likes.post_id LEFT JOIN companies on companies.id = likes.company_id;"
        results = MySQLConnection(cls.db).query_db(query)
        # All posts with the likes from company and person(influencer) who created it
        posts_list = []
        for row in results:
            company_data = {
                "id": row['companies.id'],
                "name": row['name'],
                "email": row['email'],
                "website": row['website'],
                "password": row['password'],
                "created_at": row['companies.created_at'],
                "updated_at": row['companies.updated_at'],
            }
            if len(posts_list) > 0 and posts_list[len(posts_list)-1].id == row['id']:
                company_data = company.Company(company_data)
                if row['company_id'] != None:
                    posts_list[len(posts_list)-1].liked_by.append(company_data)
            else:
                this_post = cls(row)
                if row['company_id'] != None:
                    this_post.liked_by.append(
                        company.Company.get_company_by_id(company_data))
                posts_list.append(this_post)
        return posts_list

    @classmethod
    def get_all_posts_withUser(cls):
        query = "SELECT * from posts;"
        results = MySQLConnection(cls.db).query_db(query)
        posts = []
        for row in results:
            this_post = cls(row)
            posts.append(this_post)
        return posts

    @classmethod
    def add_like(cls, data):
        query = "INSERT into likes (post_id, company_id) VALUES (%(post_id)s, %(company_id)s)"
        return MySQLConnection(cls.db).query_db(query, data)

    @classmethod
    def remove_like(cls, data):
        query = "DELETE FROM likes WHERE post_id = %(post_id)s and company_id = %(company_id)s;"
        return MySQLConnection(cls.db).query_db(query, data)

    @classmethod
    def all_posts_with_likedby_for_oneUser(cls, data):
        query = "SELECT * from posts LEFT JOIN likes ON posts.id = likes.post_id LEFT JOIN companies on companies.id = likes.company_id WHERE posts.influencer_id= %(id)s;"
        results = MySQLConnection(cls.db).query_db(query, data)
        posts_list = []
        for row in results:
            company_data = {
                "id": row['companies.id'],
                "name": row['name'],
                "email": row['email'],
                "website": row['website'],
                "password": row['password'],
                "created_at": row['companies.created_at'],
                "updated_at": row['companies.updated_at'],
            }
            if len(posts_list) > 0 and posts_list[len(posts_list)-1].id == row['id']:
                company_data = company.Company(company_data)
                if row['company_id'] != None:
                    posts_list[len(posts_list)-1].liked_by.append(company_data)
            else:
                this_post = cls(row)
                print(this_post)
                if row['company_id'] != None:
                    this_post.liked_by.append(
                        company.Company.get_company_by_id(company_data))
                posts_list.append(this_post)
        return posts_list
