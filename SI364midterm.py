###############################
####### SETUP (OVERALL) #######
###############################

## Import statements
import requests
import json
# Import statements
import os
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError, IntegerField
from wtforms.validators import Required, Length
from flask_sqlalchemy import SQLAlchemy

## App setup code
app = Flask(__name__)
app.debug = True
app.use_reloader = True

## All app.config values
app.config['SECRET_KEY'] = 'hard to guess string from si364'
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://sadiestaudacher@localhost/sadiesMIDTERM"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

## Statements for db setup (and manager setup if using Manager)
db = SQLAlchemy(app)
# manager = Manager(app)

######################################
######## HELPER FXNS (If any) ########
######################################

def get_movie_results(title):
    baseurl = 'http://www.omdbapi.com/?apikey=24fbf529&'
    param_dict = {'t':title}
    response = requests.get(baseurl, params = param_dict).json()
    return(response)


def get_or_create_review(name):
    pass

##################
##### MODELS #####
##################
#
# class Name(db.Model):
#     __tablename__ = "names"
#     id = db.Column(db.Integer,primary_key=True)
#     name = db.Column(db.String(64), unique=True)
#     reviews = db.relationship('MovieReviews', backref='Name')
#
#     def __repr__(self):
#         return "{} (ID: {})".format(self.name, self.id)

class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True)
    director = db.Column(db.String)
    genre = db.Column(db.String)
    year_released = db.Column(db.String)
    plot = db.Column(db.String)
    reviews = db.relationship('MovieReviews', backref='Movie')
    #
    # def __repr__(self):
    #     return "{%r}, (Released: {%r})" % (self.text, self.id) ## __repr__ method

class MovieReviews(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    review = db.Column(db.String(300))
    name = db.Column(db.String)
    title = db.Column(db.String, db.ForeignKey('movies.title'))
    stars = db.Column(db.Integer)
    # # reviews = db.relationship('MovieReviews', backref='Movie')
    # # names = db.relationship('MovieReviews', backref='Name')


###################
###### FORMS ######
###################

class MovieForm(FlaskForm):
    title = StringField("Enter the title of a movie to recieve information.",validators=[Required()])
    submit = SubmitField()

class MovieReviewForm(FlaskForm):
    name = StringField("Your name: ",validators=[Required()])
    movie = StringField("Name of movie: ",validators=[Required()])
    movie_review_entry = StringField("Please enter a short review of the movie, no longer than 300 characters", validators=[Required(),Length(max=300, message="The review cannot be longer than 300 characters!")])
    number_of_stars = IntegerField("Rate the movie out of 5 stars ",validators=[Required()])
    submit = SubmitField("Submit your review")

    # def validate_number_of_stars(form, field):
    #     if '.' in field.data:
    #         raise ValidationError('Have to be full numbers, no decimals for star rating')


#######################
###### VIEW FXNS ######
#######################

@app.route('/')
def home():
    return render_template('base.html')

@app.route('/find_movie')
def find_movie():
    form = MovieForm()
    return render_template('find_movie.html', form = form)

@app.route('/movie_results', methods=['GET','POST'])
def movie_results():
    form = MovieForm(request.form)
    if form.validate_on_submit():
        title_name = form.title.data
        movie = Movie.query.filter_by(title=title_name).first()
        print(movie)

        if movie:
            movie_name = movie.title
            director = movie.director
            year = movie.year_released
            genre = movie.genre
            plot = movie.plot
            return render_template('movie_results.html', title = movie_name, director = director, year = year, genre = genre, plot = plot)

        else:
            movie_dict = get_movie_results(title_name)
            movie_title = movie_dict["Title"]
            director = movie_dict["Director"]
            year = movie_dict['Year']
            genre = movie_dict['Genre']
            plot = movie_dict['Plot']
            movie_info = Movie(title=movie_title, director = director, year_released = year, genre = genre, plot = plot)
            db.session.add(movie_info)
            db.session.commit()
            return render_template('movie_results.html', title = movie_title, director = director, year = year, genre = genre, plot = plot)


@app.route('/leave_review')
def leave_review():
    form = MovieReviewForm()
    return render_template('leave_review.html', form = form)

@app.route('/all_reviews', methods=["GET","POST"])
def view_reviews():
    form = MovieReviewForm(request.form)
    if form.validate_on_submit():
        name = form.name.data
        movie = form.movie.data
        movie_review_entry = form.movie_review_entry.data
        number_of_stars = form.number_of_stars.data
        movie_review = MovieReviews.query.filter_by(name = name, title = movie, review = movie_review_entry, stars = number_of_stars).first()

        if Movie.query.filter_by(title=movie).first():
            print('Movie in database')
        else:
            new_movie = get_movie_results(movie)
            movie_title = new_movie["Title"]
            director = new_movie["Director"]
            year = new_movie['Year']
            genre = new_movie['Genre']
            plot = new_movie['Plot']
            movie_info = Movie(title=movie_title, director = director, year_released = year, genre = genre, plot = plot)
            db.session.add(movie_info)
            db.session.commit()

        if movie_review:
            print("You have already submitted this review")
        else:
            movie_review = MovieReviews(name = name, title = movie, review = movie_review_entry, stars = number_of_stars)
            db.session.add(movie_review)
            db.session.commit()

    reviews = MovieReviews.query.all()
    all_reviews = []
    for review in reviews:
        tupple = (review.name, review.title, review.review, review.stars)
        all_reviews.append(tupple)
    return render_template('all_reviews.html', all_reviews = all_reviews)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html')

if __name__ == '__main__':
    db.create_all() # Will create any defined models when you run the application
    app.run(use_reloader=True,debug=True) # The usual
