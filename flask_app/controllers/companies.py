from flask_app import app
from flask import render_template, redirect, request, session, flash, jsonify
from flask_app.models import company, influencer, post
from flask_bcrypt import Bcrypt
import re

bcrypt = Bcrypt(app)


@app.route("/company/login_registration")
def company_index():
    return render_template("company_register.html")


@app.route("/company_register", methods=['POST'])
def company_register():
    if not company.Company.validate_company_registration(request.form):
        return redirect("/company/login_registration")
    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    data = {
        "name": request.form["name"],
        "email": request.form["email"],
        "password": pw_hash,
        "website": request.form["website"],
    }
    company_id = company.Company.save(data)
    session['company_id'] = company_id
    return redirect("/company/dashbord")


@app.route("/company_login", methods=['Post'])
def company_login():
    data = {
        "email": request.form['email']
    }
    company_in_db = company.Company.get_company_by_email(data)
    if not company_in_db:
        flash("Invalid Email/Password!", "login")
        return redirect("/company/login_registration")
    if not bcrypt.check_password_hash(company_in_db.password, request.form['password']):
        flash("Invalid Email/Password!", "login")
        return redirect("/company/login_registration")
    session['company_id'] = company_in_db.id
    return redirect("/company/dashbord")


@app.route("/company/dashbord")
def company_dashbord():
    if 'company_id' not in session:
        return redirect("/")
    data = {
        "id": session['company_id']
    }
    posts = post.Post.get_all_posts_withUser_likedby()
    logged_in_company = company.Company.get_company_by_id(data)
    return render_template("all_posts.html", logged_in_company=logged_in_company, posts=posts, selected_category=category)


@app.route("/company/dashbord/<string:category>")
def category(category):
    if 'company_id' not in session:
        return redirect("/")
    data = {
        "id": session['company_id']
    }
    if category == "health":
        category = "Health & Fitness"
    elif category == "beauty":
        category = "Beauty & Makeup"
    elif category == "Lifestyle":
        category = "Home & Lifestyle"
    elif category == "tech":
        category = "Gaming & Technology"
    elif category == "music":
        category = "Music, Art & Entertainment"
    elif category == "animals":
        category = "Animals & Pets"
    elif category == "vacation":
        category = "Vacation & Travel"
    elif category == "nature":
        category = "Plants & Nature"

    posts = post.Post.get_all_posts_withUser_likedby()
    logged_in_company = company.Company.get_company_by_id(data)
    return render_template("categorized_post.html", logged_in_company=logged_in_company, posts=posts, category=category)


@app.route("/update_display", methods=['POST'])
def update_display():
    search_keyword = request.form['search_word'].lower().strip()
    print(search_keyword, "*****************")
    if 'company_id' not in session:
        return redirect("/")
    data = {
        "id": session['company_id']
    }
    posts_data = post.Post.get_all_posts_withUser_likedby()
    result = []
    for one_post in posts_data:
        print(one_post.keywords)
        keywords = one_post.keywords.lower()
        print("keywords string:", keywords)
        keyword_array = [x.strip() for x in keywords.split(',')]
        print(keyword_array)
        for x in keyword_array:
            if (x == search_keyword or search_keyword in x) and one_post not in result:
                result.append(one_post)
    logged_in_company = company.Company.get_company_by_id(data)
    print(result)
    return jsonify('', render_template("searched_post.html", logged_in_company=logged_in_company, posts=result))


@app.route("/logout")
def company_logout():
    session.clear()
    return redirect("/")
