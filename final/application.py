from flask import Flask, render_template, session, redirect, request
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError

from cs50 import SQL
from helpers import login_required, apology
from numpy import random
from subprocess import call

app = Flask(__name__)

db = SQL("sqlite:///final.db")

app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

username=""

def user():

    global username
    return username

def posts():

    posts = db.execute("SELECT * FROM posts")

    num = len(posts)
    if num < 10:
        return num
    else:
        return 10

@app.route('/')
def home():

    username = user()
    rows = db.execute("SELECT id FROM users WHERE username = ?",
                      username)

    postsize = posts()

    if username == "":
        kpost = db.execute("SELECT * FROM posts ORDER BY post_time DESC LIMIT 10")
        print(kpost)

        return render_template("home.html", username=username, list=kpost)

    else:

        uid = rows[0]["id"]

        flist = []

        rows = db.execute("SELECT * FROM follow WHERE follower_id = ?",
                              uid)
        for row in rows:
            flist.append(row["followed_id"])

        print(flist)

        if len(rows) == 0:
            content = ""

            return render_template("home2.html", username=username)

        else:

            fdisp_post = []

            for item in flist:
                fpost = db.execute("SELECT * FROM posts WHERE poster_name = ? ORDER BY post_time DESC LIMIT 2",
                                   item)
                fdisp_post.append(fpost)

            print(fdisp_post)
            return render_template("home2.html", username=username, list=fdisp_post)

@app.route('/login', methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":

        global username

        username = request.form.get("uname")

        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          username)

        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("psw")):
            return apology("invalid username/password", 403)

        session["user_id"] = rows[0]["id"]

        return redirect('/')

    else:
        return render_template("login.html")

@app.route('/register', methods=["GET", "POST"])
def register():

    session.clear()

    if request.method == "POST":

        if request.form.get("username") == "":
            return apology("must provide username", 403)

        else:
            print("username is", request.form.get("username"))

        if request.form.get("password") == "":
            return apology("must provide password", 403)

        else:
            print("password is", request.form.get("password"))

        if not request.form.get("password") == request.form.get("con"):
            return apology("passwords don't match", 403)

        username = request.form.get("username")
        password = request.form.get("password")
        phash = generate_password_hash(password)

        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          username)

        if len(rows) != 0:
            return apology("username taken", 403)
        else:
            db.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                       username, phash)

        return redirect('/')

    else:
        return render_template("register.html")

@app.route('/registeruser')
def registeruser():

    return call(["php", "mail.php"])

@app.route('/profile')
@login_required
def profile():

    username = user()

    rows = db.execute("SELECT id FROM users WHERE username = ?",
                      username)

    for row in rows:
        uid = row["id"]

    follower = db.execute("SELECT * FROM follow WHERE followed_id = ?",
                          uid)

    followings = db.execute("SELECT * FROM follow WHERE follower_id = ?",
                            uid)

    post = db.execute("SELECT * FROM posts WHERE poster_name = ? ORDER BY post_time DESC",
                      username)

    followers = len(follower)
    following = len(followings)
    posts = len(post)

    return render_template("profile.html", username=username, followers=followers, following=following, posts=posts, list=post)


@app.route('/create', methods=["GET", "POST"])
@login_required
def create():

    username = user()
    rows = db.execute("SELECT id FROM users WHERE username = ?",
            username)
    for row in rows:
        uid = row["id"]

    if request.method == "POST":

        title = request.form.get("title")
        content = request.form.get("content")

        print(username)
        print(title)
        print(content)

        db.execute("INSERT INTO posts (poster_name, post_title, post_text, poster_id) VALUES (?, ?, ?, ?)",
                   username, title, content, uid)

        return redirect('/')

    else:
        return render_template('create.html', username=username)

@app.route('/review', methods=["GET", "POST"])
@login_required
def review():

    if request.method == "POST":

        title = request.form.get("title")
        content = request.form.get("content")

        print(title)
        print(content)

        return redirect('/')

    else:

        return render_template('review.html')

@app.route('/settings')
@login_required
def settings():

    username = user()

    return render_template('settings.html', username=username)

@app.route('/forgot')
def forgot():

    session.clear()

    return render_template("forgot.html")

@app.route('/profileupdate', methods=["GET", "POST"])
def profileupdate():

    if request.method == "POST":
        username = user()
        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          username)
        uid = rows[0]["id"]

        rows = db.execute("SELECT * FROM customize WHERE user_id = ?",
                          uid)

        if len(rows) == 0:
            db.execute("INSERT INTO customize (user_id) VALUES (?)",
                       uid)

        dispname = request.form.get("newname")
        flair = request.form.get("flair-")
        email = request.form.get("email")
        oldpwd = request.form.get("oldpwd")
        newpwd = request.form.get("newpwd")
        newcon = request.form.get("newcon")

        print(dispname)

        if not dispname == "":
            db.execute("UPDATE customize SET display_name = ? WHERE id = ?",
                       dispname, uid)
        elif not flair == "":
            db.execute("UPDATE customize SET flair = ? WHERE id = ?",
                       flair, uid)
        elif not email == "":
            db.execute("UPDATE customize SET email = ? WHERE id = ?",
                       email, uid)
        elif not newpwd == "":
            if not check_password_hash(rows[0]["password"], oldpwd):
                return apology("invalid username/password", 403)
            else:
                if not newpwd == newcon:
                    return apology("invalid username/password", 403)
                else:
                    pwd = generate_password_hash(newpwd)
                    db.execute("UPDATE users SET password = ? WHERE id = ?",
                               pwd, uid)
    return redirect('/settings')

@app.route('/users/<userid>/')
def users(userid):

    username = user()
    rows = db.execute("SELECT * FROM users WHERE username = ?",
                      username)

    print(len(rows))
    if not len(rows) == 0:
        uid = rows[0]["id"]

        print("I'm here now")

        if uid == userid:
            return redirect('/profile')

        rows = db.execute("SELECT * FROM users WHERE id = ?",
                          userid)
        for row in rows:
            username_ = row["username"]

            print(uid)
            print(userid)


            rows = db.execute("SELECT status FROM friends WHERE user1 = ? AND user2 = ? OR user1 = ? AND user2 = ?",
                              str(uid), userid, userid, str(uid))
            print("SELECT status FROM friends WHERE user1 = ? AND user2 = ? OR user1 = ? AND user2 = ?",
                              uid, userid, userid, uid)
            if len(rows) == 0:
                status = "Send Friend Request"
                style = "createbtn"
                href = f"/friendrequest/{userid}"
            else:
                for row in rows:
                    status = row["status"]
                if status == "request":
                    status = "Cancel Friend Request"
                    style = "cancel_btn"
                    href = f"/rmfriend/{userid}"
                else:
                    status = "Unfriend"
                    style = "rmbtn"
                    href = f"/rmfriend/{userid}"

        print(status)

    else:
        print("I'm here meow")

        rows = db.execute("SELECT * FROM users WHERE id = ?",
                          userid)
        for row in rows:
            username_ = row["username"]

        status = "Send Friend Request"
        style = "createbtn"
        href = f"/friendrequest/{userid}"

    follower = db.execute("SELECT * FROM follow WHERE followed_id = ?",
                          userid)
    followings = db.execute("SELECT * FROM follow WHERE follower_id = ?",
                            userid)
    post = db.execute("SELECT * FROM posts WHERE poster_name = ? ORDER BY post_time DESC",
                      username_)

    followers = len(follower)
    following = len(followings)
    posts = len(post)

    return render_template("uprofile.html",
                           username=username, username_=username_, followers=followers, following=following, posts=posts,
                           list=post, id=userid, status=status, style=style, href=href)


@app.route('/logout')
def logout():

    session.clear()

    global username
    username = ""

    return redirect('/')

@app.route('/upvote')
@login_required
def upvote():

    username = user()
    rows = db.execute("SELECT * FROM users WHERE username = ?",
                      username)
    uid = rows[0]["id"]

    db.execute("INSERT INTO vote (user_id, vote) VALUES (?, 'u')", uid)

    return redirect('/')

@app.route('/downvote')
@login_required
def downvote():

    username = user()
    rows = db.execute("SELECT * FROM users WHERE username = ?",
                      username)
    uid = rows[0]["id"]

    db.execute("INSERT INTO vote (user_id, vote) VALUES (?, 'd')", uid)

    return redirect('/')


@app.route('/friends')
@login_required
def friends():

    friends = []
    fusername = []
    requests = []
    request2 = []
    frequests = []

    username = user()
    rows = db.execute("SELECT * FROM users WHERE username = ?",
                      username)
    uid = rows[0]["id"]

    rows = db.execute("""SELECT user1 FROM friends WHERE user2 = ? AND status = 'approved'
                         UNION
                         SELECT user2 FROM friends WHERE user1 = ? AND status = 'approved'""",
                      uid, uid)
    for row in rows:
        if not row["user1"] == "":
            friends.append(row["user1"])
        elif not row["user2"] == "":
            friends.append(row["user2"])

    print(friends)

    for friend in friends:
        friend_name = db.execute("SELECT username FROM users WHERE id = ?",
                                 friend)
        for name in friend_name:
            username = name["username"]

        fusername.append(username)

    rows = db.execute("SELECT user1 FROM friends WHERE user2 = ? AND status = 'request'",
                      uid)
    for row in rows:
        if not row["user1"] == "":
            requests.append(row["user1"])
        elif not row["user2"] == "":
            requests.append(row["user2"])

    for request in requests:
        request_name = db.execute("SELECT username FROM users WHERE id = ?",
                                  request)
        for name in request_name:
            username = name["username"]

        frequests.append({'username': username, 'id': request})
        print(frequests)

    return render_template('friends.html', list=fusername, list2=frequests, username=username)

@app.route('/friendrequest/<userid>')
@login_required
def friendrequest(userid):

    username = user()
    rows = db.execute("SELECT * FROM users WHERE username = ?",
                      username)
    uid = rows[0]["id"]

    db.execute("INSERT INTO friends VALUES (?, ?, 'request')",
               uid, userid)

    return redirect(f'/users/{userid}')

@app.route('/rmfriend/<userid>')
@login_required
def rmfriend(userid):

    username = user()
    rows = db.execute("SELECT * FROM users WHERE username = ?",
                      username)
    uid = rows[0]["id"]

    db.execute("DELETE FROM friends WHERE user1 = ? AND user2 = ? OR user1 = ? AND user2 = ?",
                uid, userid, userid, uid)

    return redirect(f'/users/{userid}')

@app.route('/accept/<userid>')
@login_required
def accept(userid):

    username = user()
    rows = db.execute("SELECT * FROM users WHERE username = ?",
                      username)
    uid = rows[0]["id"]

    db.execute("UPDATE friends SET status = 'approved' WHERE user1 = ? AND user2 = ? OR user1 = ? AND user2 = ?",
                uid, userid, userid, uid)

    return redirect('/friends')

@app.route('/reject/<userid>')
@login_required
def reject(userid):

    username = user()
    rows = db.execute("SELECT * FROM users WHERE username = ?",
                      username)
    uid = rows[0]["id"]

    db.execute("DELETE FROM friends WHERE user1 = ? AND user2 = ? OR user1 = ? AND user2 = ?",
                uid, userid, userid, uid)

    return redirect('/friends')

@app.route('/upload', methods=["POST"])
def upload():
    file = request.files["img"]



def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)