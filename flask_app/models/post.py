from unittest import result
from flask_app.config.mysqlconnection import MySQLConnection, connectToMySQL
from flask_app.models import influencer, company
from flask import flash
import re


import os
import openai
from env import API_KEY

openai.api_key = API_KEY


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
        self.tiktok_post_id = data['tiktok_post_id']
        self.keywords = data['keywords']
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
    def keyword(cls, data):
        url = data
        if "youtube.com/watch" in url:
            # video_id = url.split("v=")[1].split("&")[0]
            # video_url = f"https://www.youtube.com/watch?v={video_id}"
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"Given a youtube URL, generate keywords that are relevant to its content,and return them in a commma seprated string without any special char. The keywords should accurately reflect the main topic of the video and be useful for improving its searchability:\n{url}\nKeywords:",
                temperature=0.5,
                max_tokens=100,
                n=1,
                stop=None,
                timeout=10,
            )
        else:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"Given a social media post URL, generate keywords that are relevant to the post based on its content, hashtags and description and return them in a commma seprated string without any special char. The keywords should accurately reflect the main theme or topic of the post and be useful for improving its searchability:\n{url}\nKeywords:",
                temperature=0.5,
                max_tokens=100,
                n=1,
                stop=None,
                timeout=10,
            )

        keywords_list = response.choices[0].text
        return keywords_list

    # @classmethod
    # def keyword(cls, data):
    #     url = data
    #     print(url)
    #     response = openai.Completion.create(
    #         model="text-davinci-003",
    #         prompt=f"Given a social media post URL, generate keywords that are relevant to the post based on its content, hashtags and description and return them in a commma seprated string without any special char. The keywords should accurately reflect the main theme or topic of the post and be useful for improving its searchability, {url}",
    #         temperature=0.7,
    #         max_tokens=256,
    #         top_p=1,
    #         frequency_penalty=0,
    #         presence_penalty=0
    #     )
    #     print(response.choices[0].text)
    #     return str(response.choices[0].text)

    @classmethod
    def save(cls, data):
        query = "INSERT INTO posts (title, category, social_platform, url, influencer_id, tiktok_post_id, keywords) VALUES (%(title)s, %(category)s, %(social_platform)s, %(url)s, %(influencer_id)s, %(tiktok_post_id)s, %(keywords)s);"
        return MySQLConnection(cls.db).query_db(query, data)

    # @classmethod
    # def save(cls, data):
    #     query = "INSERT INTO posts (title, category, social_platform, url, influencer_id, tiktok_post_id) VALUES (%(title)s, %(category)s, %(social_platform)s, %(url)s, %(influencer_id)s, 0);"
    #     return MySQLConnection(cls.db).query_db(query, data)

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
