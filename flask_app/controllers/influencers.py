from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_app.models import company, influencer, post
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

@app.route("/")
def welcome():
    return render_template("welcome.html")

@app.route("/influencer/login_registration")
def influancer_index():
    return render_template("influencer_register.html") 

@app.route("/influencer_register", methods = ['POST'])
def register():
    if not influencer.Influencer.validate_influencer_registration(request.form):
        return redirect("/influencer/login_registration")
    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    data = {
        "first_name": request.form["first_name"],
        "last_name": request.form["last_name"],
        "email": request.form["email"],
        "password" : pw_hash,
    }
    influencer_id = influencer.Influencer.save(data) 
    session['influencer_id'] = influencer_id
    return redirect ("/influencer/dashbord")

@app.route("/influencer_login", methods= ['Post'])
def login():
    data = {
        "email": request.form['email']
    }
    influencer_in_db = influencer.Influencer.get_influencer_by_email(data)
    if not influencer_in_db: 
        flash("Invalid Email/Password!", "login")
        return redirect("/influencer/login_registration")
    if not bcrypt.check_password_hash(influencer_in_db.password, request.form['password']):
        flash("Invalid Email/Password!", "login")
        return redirect("/influencer/login_registration")
    session['influencer_id'] = influencer_in_db.id
    return redirect("/influencer/dashbord")

@app.route("/influencer/dashbord")
def dashbord():
    if 'influencer_id' not in session:
        return redirect("/")
    data = {
        "id"  : session['influencer_id']
    }
    posts = influencer.Influencer.All_posts_from_one_influencer(data)
    print(posts)
    return render_template("influencer_dashbord.html", logged_in_user = influencer.Influencer.get_influencer_by_id(data), posts = posts)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

