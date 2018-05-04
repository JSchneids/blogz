from flask import Flask, request, redirect, render_template, session, flash 
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__) 
app.config['DEBUG'] = True
#connection string = mysql connection ://user :user password @host  :port number /database to connect to
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:jakesblog@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'zasdsagdsgadsf'   #randomly selected

#creates blog table in database
class Blog(db.Model): 
    id = db.Column(db.Integer, primary_key=True)  #primary key causes it to auto increment
    title = db.Column(db.String(120))
    body = db.Column(db.String(50000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id')) #foreign key linking the user's id to the blog post
    
    def __init__(self, title, body, owner):    #constructer 
        self.title = title
        self.body = body 
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25))
    password = db.Column(db.String(25))
    blogs = db.relationship('Blog', backref='owner')   #signifies a relationship between the blog table and this user, thus binding this user with the blog posts they write.
 
    def __init__(self, username, password):  #constructer 
        self.username = username
        self.password = password

#check to make sure blog title and blog body are not empty 
def input_error(input):
    if input == "":
        return  True
    else:
        return False

#username minimum and maximum length
def error_check(text):
    if " " in text or 3 > len(text) or len(text) > 50:
        return True
    else:
        return False

#passwords can not match
def password_check(pass1, pass2):
    if not pass1 == pass2 or pass2 == "" or len(pass1) < 3:
        return True
    else:
        return False

#specific routes we want to allow
@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'list_blogs', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':
        
        username_error = ""
        password_error = ""
        verify_password_error = ""
        email_error = ""

        username = request.form['username']
        password = request.form['password']
        verify_password = request.form['verify-password']

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            username_error = "That username is not available. Please input a new username."

        if error_check(username):
            username_error = "That's not a valid username. Please resubmit."

        if error_check(password):
            password_error = "That's not a valid password. Please resubmit."

        if password_check(password, verify_password):
            verify_password_error = "Passwords do not match. Please submit."
        if not existing_user and not error_check(username) and not error_check(password) and not password_check(password, verify_password):
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
    
        return render_template('signup.html', username_error=username_error, password_error=password_error, 
        verify_password_error=verify_password_error, username=username, 
        password=password, verify_password=verify_password)

    return render_template('signup.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Welcome back, you are logged in", 'success')
            return redirect('/newpost')
        else:
            flash("User password incorrect, or user does not exist.", "error")

    return render_template('login.html')        

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/blog', methods=['POST', 'GET'])
def list_blogs():
    
    if 'user' in request.args:
        user_id = request.args.get('user')
        user = User.query.get(user_id)
        blog_list = Blog.query.filter_by(owner=user).all()
        return render_template('singleUser.html', title=user.username + " posts", blog_list=blog_list)

    blog_id = request.args.get('id')
    if blog_id:
        blog = Blog.query.get(blog_id)
        return render_template('blog_display.html',title="Blog Post",blog=blog)

    
    blogs = Blog.query.filter_by().order_by(Blog.id.desc()).all()
    return render_template('blog.html',title="blogz", 
        blogs=blogs)

@app.route('/blog?id={{blog.id}}', methods=['POST', 'GET'])
def display_blog():
    if request.method == 'POST':
        blog_title = request.form['blog-title']
        blog_body = request.form['blog-body']

    return render_template('blog_display.html',title=blog_title,blog_body=blog_body)


@app.route('/newpost', methods=['POST', 'GET'])
def add_blog():

    title_error = ""
    body_error = ""

    if request.method == 'POST':
        blog_title = request.form['blog-title']
        blog_body = request.form['blog-body']
        owner = User.query.filter_by(username=session['username']).first()

        new_blog = Blog(blog_title, blog_body, owner)

        if input_error(blog_title):
            title_error = "Please do not leave the title blank"
        
        if input_error(blog_body):
            body_error = "Please do not leave the blog body blank"

        if not input_error(blog_title) and not input_error(blog_body):
            db.session.add(new_blog)
            db.session.commit()
            new_blog_page = "/blog?id=" + str(new_blog.id)
            return redirect(new_blog_page)

    return render_template('newpost.html', title="Add a Blog Entry", title_error=title_error, body_error=body_error)


if __name__ == '__main__':  #use if running main.py on terminal 
    app.run()