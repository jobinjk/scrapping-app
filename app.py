from flask import Flask, jsonify, request, json, redirect, url_for, render_template, send_file
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
from flask_mongoengine import MongoEngine, DoesNotExist
from werkzeug.security import generate_password_hash, check_password_hash
from celery import Celery
import datetime,random,string, bcrypt
from uuid import uuid4
from bson.objectid import ObjectId
import urllib2


app = Flask(__name__)   # creating app name

db = MongoEngine()
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379/0',
    CELERY_RESULT_BACKEND='redis://localhost:6379/0'
)

def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

celery = make_celery(app)
app.config['DEBUG'] = True
app.config['MONGODB_DB'] = 'jusrun'
app.config['SECRET_KEY'] = "secret key is here !!!"
# app.config['MONGODB_HOST'] = ''
# app.config['MONGODB_PORT'] = 12345
db.init_app(app)


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user):
    return User.objects.get(id=user)



class User(db.Document):
    date_created = db.DateTimeField(default=datetime.datetime.now, required=True)
    username = db.StringField(max_length=50, required=True)
    password = db.StringField(required=True)

    def __unicode__(self):
        return self.id

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def is_authenticated(self):
        return True

    def get_id(self):
        return unicode(self.id)

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def validate_login(password_hash, password):
        return check_password_hash(password_hash, password)

    meta = {
        'allow_inheritance': True,
        'indexes': ['-date_created', 'username'],
        'ordering': ['-date_created']
    }

class Scrap(db.Document):
    user = db.ReferenceField(User)
    url = db.StringField(max_length=150, required=True)
    filename = db.StringField(max_length=500, required=True)


@app.route('/') # setting app route for eg 127.0.0.1:5000/<something>

def api_start(): # creating a function api_root which returns some txt to url
    try:
        if current_user:
            print True
            username = current_user.username
            return render_template('index.html', username=username) 
    except:
        return render_template('index.html', username=None) 



@app.route('/login', methods = ['POST']) # setting another route /messages methods as post

def api_login(): # creating a function api_message which gives a json data when a form is submitted in url
    data= request.get_json()

    try:
        user = User.objects.get(username=data['username'])
        if user.validate_login(user.password, data['password']):
            user_obj = User.objects.get(id=user.id)
            login_user(user_obj)
            return jsonify({'status': True})
    except DoesNotExist:
        return jsonify({'status': False})
    return jsonify({'status': False})


@app.route('/signup', methods = ['POST']) # setting another route /messages methods as post

def api_signup(): # creating a function api_message which gives a json data when a form is submitted in url
    data= request.get_json()

    print data
    try:
        data = User.objects.get(username=data['username'])
        return jsonify({'status': False})
    except DoesNotExist:

        hashed_pass = bcrypt.hashpw(str(data['password']), bcrypt.gensalt())
        user_obj = User(username=data['username'])
        user_obj.set_password(data['password'])
        user_obj.save()
    return jsonify({'status':True})


@app.route("/logout", methods=['GET'])
def api_logout():
    logout_user()
    return redirect(url_for('api_start'))


@app.route('/scrap', methods=['GET']) # setting another route /messages methods as post
@login_required
def api_url(): # creating a function api_message which gives a json data when a form is submitted in url
	data= request.get_json()
	print data

	return render_template('task.html',scrap=None)  


@app.route('/crawl', methods=['POST'])
@login_required
def api_crawl():
	data= request.get_json()
	print data
	try:
		url = data['scrap']
		filename = "{0}_{1}.txt".format(current_user.username, str(uuid4()))
		sc=Scrap(url=url,filename= filename, user= current_user.id)
		sc.save()
		celery.send_task('tasks.scrap',[url, filename])
		return jsonify(status=True, filename=filename, url=url)
	except Exception as e:
		raise e


@app.route('/download', methods=['GET'])
@login_required
def api_download():
	filename= request.args.get('filename',None)
	print ">>>>>>>>>>>>> file : ",filename
	try:
		f = open(filename,'r')
		print f
		
		return send_file(f, mimetype="text/plain", as_attachment=True, attachment_filename=filename)
	except Exception as e:
		raise e



if __name__ == '__main__':
    app.run()