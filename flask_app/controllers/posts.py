from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_app.models import company, influencer, post
import re


@app.route("/new/post")
def newpost():
    if 'influencer_id' not in session:
        return redirect('/')
    data = {
        "id": session['influencer_id']
    }
    logged_in_user = influencer.Influencer.get_influencer_by_id(data)
    return render_template("create_post.html", logged_in_user=logged_in_user)


@app.route("/create/post", methods=['POST'])
def create_post():
    if not post.Post.validate_post(request.form):
        return redirect("/new/post")
    else:
        if request.form['social_platform'] == 'TikTok':
            post_id = re.search(r'(?<=video\/)\d+',
                                request.form['url']).group(0)
        else:
            post_id = None
        keywords = post.Post.keyword(request.form['url'])
        data = {
            "title": request.form['title'],
            "category": request.form['category'],
            "social_platform": request.form['social_platform'],
            "url": request.form['url'],
            "tiktok_post_id": post_id,
            "influencer_id": session['influencer_id'],
            "keywords": keywords + ","+request.form['social_platform']
        }
        post.Post.save(data)
        return redirect("/influencer/dashbord")


@app.route("/edit_post/<int:id>")
def edit(id):
    if 'influencer_id' not in session:
        return redirect('/')
    data = {
        "id": id
    }
    data2 = {
        "id": session['influencer_id']
    }
    return render_template("edit_post.html", post=post.Post.get_one_post(data), logged_in_user=influencer.Influencer.get_influencer_by_id(data2))


@app.route('/update_post/<int:id>', methods=["POST"])
def update_recipe(id):
    if not post.Post.validate_post(request.form):
        return redirect(f"/edit_post/{id}")
    else:
        data = {
            "id": id,
            "title": request.form['title'],
            "category": request.form['category'],
            "social_platform": request.form['social_platform'],
            "url": request.form['url'],
            "influencer_id": session['influencer_id']
        }
        post.Post.update_post(data)
        return redirect(f"/influencer/dashbord")


@app.route('/delete_post/<int:id>')
def delete_post(id):
    if 'influencer_id' not in session:
        return redirect('/')
    data = {
        "id": id
    }
    post.Post.delete(data)
    return redirect('/influencer/dashbord')


@app.route("/post_like/<int:id>")
def like_post(id):
    if 'company_id' not in session:
        return redirect('/')
    data = {
        "post_id": id,
        "company_id": session['company_id']
    }
    post.Post.add_like(data)
    return redirect("/company/dashbord")


@app.route("/post_dislike/<int:id>")
def dislike_post(id):
    if 'company_id' not in session:
        return redirect('/')
    data = {
        "post_id": id,
        "company_id": session['company_id']
    }
    post.Post.remove_like(data)
    return redirect("/company/dashbord")
