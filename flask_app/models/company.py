from flask_app.config.mysqlconnection import MySQLConnection, connectToMySQL
from flask_app.models import influencer, post
from flask import flash
import re


EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class Company:
    db = 'connect'
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.email = data['email']
        self.password = data['password']
        self.website = data['website']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
    
    @staticmethod
    def validate_company_registration(data):
        is_valid = True
        if len(data["name"]) < 2:
            flash("company name must be at least 2 characters.", "register")
            is_valid = False
        if len(data["website"]) < 5:
            flash("Website must be at least 8 characters.", "register")
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
        
        query = "SELECT * FROM companies where email = %(email)s"
        result= connectToMySQL(Company.db).query_db(query,data)
        if len(result) >= 1:
            is_valid = False
            flash('Email already exist in database!!', "register")
        return is_valid

    @classmethod
    def save(cls,data):
        query = "INSERT INTO companies (name, email, website, password) VALUES (%(name)s, %(email)s, %(website)s, %(password)s);"
        return MySQLConnection(cls.db).query_db(query,data) #method returns users.id from database

    @classmethod
    def get_company_by_id(cls,data):
        query = "SELECT * FROM companies where id = %(id)s;"
        results = connectToMySQL(Company.db).query_db(query,data)
        if len(results) < 1:
            return False
        return cls(results[0])
    
    @classmethod
    def get_company_by_email(cls,data):
        query = "SELECT * FROM companies where email= %(email)s;"
        results = connectToMySQL(Company.db).query_db(query,data)
        if len(results) < 1:
            return False
        return cls(results[0])
