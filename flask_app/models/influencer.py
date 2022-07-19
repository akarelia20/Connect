from poplib import POP3_SSL_PORT
from flask_app.config.mysqlconnection import MySQLConnection, connectToMySQL
from flask_app.models import post, company
from flask import flash, session
import re


EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class Influencer:
    db = 'connect'
    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.posts = []
        self.instagram= None
        self.tiktok= None
        self.bio = None
    
    @staticmethod
    def validate_influencer_registration(data):
        is_valid = True
        if len(data["first_name"]) <= 1:
            flash("First Name must be at least 2 characters.", "register")
            is_valid = False
        if len(data["last_name"]) <= 1:
            flash("Last Name must be at least 2 characters.", "register")
            is_valid = False
        if len(data["password"]) < 8:
            flash("Password must be atleast 8 characters.", "register")
            is_valid = False
        if not EMAIL_REGEX.match(data['email']):
            is_valid = False 
            flash("Invalid email address!", "register")
        if data['password'] != data['confirm_password']:
            is_valid = False 
            flash("Passwords do not match, try entering it again", "register")
        
        query = "SELECT * FROM influencers where email = %(email)s"
        result= connectToMySQL(Influencer.db).query_db(query,data)
        if len(result) >= 1:
            is_valid = False
            flash('Email already exist in database!!', "register")
        return is_valid

    @classmethod
    def save(cls,data):
        query = "INSERT INTO influencers (first_name, last_name, email, password) VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s);"
        return MySQLConnection(cls.db).query_db(query,data) #method returns users.id from database

    @classmethod
    def get_influencer_by_id(cls,data):
        query = "SELECT * FROM influencers where id = %(id)s;"
        results = connectToMySQL(Influencer.db).query_db(query,data)
        if len(results) < 1:
            return False
        return cls(results[0])
    
    @classmethod
    def get_influencer_by_email(cls,data):
        query = "SELECT * FROM influencers where email= %(email)s;"
        results = connectToMySQL(Influencer.db).query_db(query,data)
        if len(results) < 1:
            return False
        return cls(results[0])

    # @classmethod
    # def All_posts_from_one_influencer(cls,data):
    #     query = "SELECT * FROM influencers LEFT JOIN posts ON influencers.id = posts.influencer_id WHERE influencers.id = %(id)s"
    #     results = connectToMySQL(Influencer.db).query_db(query,data)
    #     if len(results) < 1:
    #         return False
    #     else:
    #         this_user = cls(results[0])
    #         for row in results:
    #             post_dict = {
    #                 "id" : row['posts.id'],
    #                 "title" : row['title'],
    #                 "category" : row['category'],
    #                 "social_platform": row['social_platform'],
    #                 "url" : row['url'],
    #                 "created_at" : row['posts.created_at'],
    #                 "updated_at" : row['posts.updated_at'],
    #                 "influencer_id" : row['influencer_id']
    #             }
    #             this_post = post.Post(post_dict)
    #             this_user.posts.append(this_post)
    #         return this_user.posts

    
