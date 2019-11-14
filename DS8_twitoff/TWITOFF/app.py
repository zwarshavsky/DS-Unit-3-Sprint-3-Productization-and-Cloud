"""Build my app factory and do routes and configuration"""


from decouple import config
from dotenv import load_dotenv
from flask import Flask, render_template, request
from .models import DB, User
from .predict import predict_user
from .twitter import add_or_update_user


#now we make a app factory

def create_app():
    app = Flask(__name__)
    # app.run(debug=True)

    app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False

    DB.init_app(app)

    @app.route('/')
    def root():
        users = User.query.all()
        return render_template('base.html', title='Home', users=users)
    
    #adding in a new route to add users or get users
    @app.route('/user',methods=['POST']) #uses form
    @app.route('/user/<name>', methods=['GET']) #needs parameter
    def user(name=None, message=''):
        name = name or request.values['user_name']
        try:
            if request.method == 'POST':
                add_or_update_user(name)
                message = "User {} successfully added!".format(name)
            tweets = User.query.filter(User.name == name).one().tweets
        except Exception as e:
            message = 'Error adding {}: {}'.format(name,e)
            tweets = []
        return render_template('user.html', title=name, tweets=tweets, message = message)
    
    #adding in a route for predictions
    @app.route('/compare', methods = ["POST"])
    def compare(message = ''):
        user1,user2 = sorted([request.values['user1'],
        request.values['user2']])
        if user1 == user2:
            message = "Cannot compare a user to themselves"
        else:
            prediction = predict_user(user1, user2, request.values['tweet_text'])
            message = '"{}" is more likely to be said by {} than {}'.format(request.values['tweet_text'],user1 if prediction else user2, user2 if prediction else user1)
        return render_template('prediction.html', title='Prediction', message=message)

    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return render_template('base.html', title="Reset", users = [])
    return app
