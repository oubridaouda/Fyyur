#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from lib2to3.pytree import convert
from tokenize import String
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
# TODO: connect to a local postgresql database
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
from models import*
db.init_app(app)
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html',data=Artist.query.all())


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.   
  results = db.session.query(Venue.city,Venue.state).with_entities(Venue.city,Venue.state).group_by(Venue.city,Venue.state).all()
  list = []
  for result in results:
    dict={"city":result[0],"state": result[1],"venues":[]}
    venues = Venue.query.filter(Venue.state==result.state,Venue.city==result.city).all()
    for venue in venues:
      venuesData = {"id": venue.id,"name": venue.name,"num_upcoming_shows": db.session.query(Venue.id,Venue.name,Show.venue_id,db.func.count(Venue.id).label("num_upcoming_shows")).join(Venue,Show.venue_id == Venue.id).filter(Venue.state==result.state,Venue.city==result.city).group_by(Venue.id,Show.venue_id).count()}
      dict['venues'].append(venuesData)
    
    list.append(dict)
  data=list 
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  query = db.session.query(Venue.id,Venue.name,Show.venue_id,db.func.count(Venue.id).label("num_upcoming_shows")).join(Venue,Show.venue_id == Venue.id).filter(Venue.name.ilike('%'+request.form.get('search_term', '')+'%')).group_by(Venue.id,Show.venue_id).all()
  response={
    "count": db.session.query(Venue.id,Venue.name,Show.venue_id,db.func.count(Venue.id).label("num_upcoming_shows")).join(Venue,Show.venue_id == Venue.id).filter(Venue.name.ilike('%'+request.form.get('search_term', '')+'%')).group_by(Venue.id,Show.venue_id).count(),
    "data": query
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

    venues =  Venue.query.filter_by(id=venue_id).first()
    query = db.session.query(
      Venue,  
      Artist,
      Artist.name.label("artist_name"),
      Artist.id.label("artist_id"),
      Artist.image_link.label("artist_image_link"),
      Show,
      Show.start_time
    ).join(Show, Show.venue_id == Venue.id).join(Artist,Show.artist_id == Artist.id)
    dict = {}
    
    venues = Venue.query.get(venue_id)   # Returns object by primary key, or None
    print(venues)
    past_shows_count = 0
    upcoming_shows_count = 0
    now = datetime.now()
    query = db.session.query(
      Venue,
      Artist,
      Artist.name.label("artist_name"),
      Artist.id.label("artist_id"),
      Artist.image_link.label("artist_image_link"),
      Show,
      Show.start_time
    ).join(Show, Show.venue_id == Venue.id).join(Artist,Show.artist_id == Artist.id)
    print(query)
    for show in venues.shows:
            if show.start_time > now.strftime("%Y-%d-%m, %H:%M:%S"):
                upcoming_shows_count += 1
                print(show.start_time)
            if show.start_time < now.strftime("%Y-%d-%m, %H:%M:%S"):
                past_shows_count += 1

    data={
        "id": venues.id,
        "name": venues.name,
        "genres":  venues.genres.split(","),
        "address": venues.address,
        "city": venues.city,
        "state": venues.state,
        "phone": venues.phone,
        "website": venues.website_link,
        "facebook_link": venues.facebook_link,
        "seeking_talent": venues.seeking_talent,
        "seeking_description": venues.seeking_description,
        "image_link": venues.image_link,
        "past_shows": query.filter(Show.venue_id == venue_id,Show.start_time < now.strftime("%Y-%d-%m, %H:%M:%S")).all(),
        "past_shows_count": past_shows_count,
        "upcoming_shows": query.filter(Show.venue_id == venue_id,Show.start_time > now.strftime("%Y-%d-%m, %H:%M:%S")).all(),
        "upcoming_shows_count": upcoming_shows_count
    }
    return render_template('pages/show_venue.html', venue=data)
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    name = request.form.get('name','')
    city = request.form.get('city','')
    state = request.form.get('state','')
    address = request.form.get('address','')
    phone = request.form.get('phone','')
    genres = ','.join(request.form.getlist('genres'))
    facebook_link = request.form.get('facebook_link','')
    image_link = request.form.get('image_link','')
    website_link = request.form.get('website_link','')
    seeking_talent = request.form.get('seeking_talent','')
    seeking_description = request.form.get('seeking_description','')
    venue = Venue(name=name,city=city,state=state,address=address,genres=genres,phone=phone,image_link=image_link,facebook_link=facebook_link,website_link=website_link,seeking_talent=seeking_talent,seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  return render_template('pages/home.html')

@app.route('/venues/delete/<venue_id>/', methods=['Post'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
    name = Venue.query.filter_by(id=venue_id).first().name
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('Venue ' + name + ' was successfully delete!')
    return render_template('pages/home.html',data=Artist.query.all())
  except:
    flash('An error occurred. Venue could not be listed.')
    return render_template('pages/home.html',data=Artist.query.all())

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data= Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  query = db.session.query(Artist.id,Artist.name,Show.artist_id,db.func.count(Show.artist_id).label("num_upcoming_shows")).join(Artist,Show.artist_id == Artist.id).filter(Artist.name.ilike('%'+request.form.get('search_term', '')+'%')).group_by(Artist.id,Show.artist_id).all()
  response={
    "count": db.session.query(Artist.id,Artist.name,Show.artist_id,db.func.count(Show.artist_id).label("num_upcoming_shows")).join(Artist,Show.artist_id == Artist.id).filter(Artist.name.ilike('%'+request.form.get('search_term', '')+'%')).group_by(Artist.id,Show.artist_id).count(),
    "data": query
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  try:
    artists =  Artist.query.filter_by(id=artist_id).first()
    query = db.session.query(
      Venue,  
      Artist,
      Artist.name.label("artist_name"),
      Artist.id.label("artist_id"),
      Artist.image_link.label("artist_image_link"),
      Show,
      Show.start_time
    ).join(Show, Show.venue_id == Venue.id).join(Artist,Show.artist_id == Artist.id)
    
    artists = Artist.query.get(artist_id)   # Returns object by primary key, or None
    print(venues)
    past_shows_count = 0
    upcoming_shows_count = 0
    now = datetime.now()
    query = db.session.query(
      Venue,
      Artist,
      Venue.name.label("venue_name"),
      Venue.id.label("venue_id"),
      Venue.image_link.label("venue_image_link"),
      Show,
      Show.start_time
    ).join(Show, Show.venue_id == Venue.id).join(Artist,Show.artist_id == Artist.id)
    print(query)
    for show in artists.shows:
            if show.start_time > now.strftime("%Y-%d-%m, %H:%M:%S"):
                upcoming_shows_count += 1
                print(show.start_time)
            if show.start_time < now.strftime("%Y-%d-%m, %H:%M:%S"):
                past_shows_count += 1
    data={
      "id": artists.id,
      "name": artists.name,
      "genres":  artists.genres.split(","),
      "city": artists.city,
      "state": artists.state,
      "phone": artists.phone,
      "website": artists.website_link,
      "facebook_link": artists.facebook_link,
      "seeking_venue": artists.seeking_venue,
      "seeking_description": artists.seeking_description,
      "image_link": artists.image_link,
      "past_shows": query.filter(Artist.id == artist_id,Show.start_time < now.strftime("%Y-%d-%m, %H:%M:%S")).all(),
      "past_shows_count": past_shows_count,
      "upcoming_shows": query.filter(Artist.id == artist_id,Show.start_time > now.strftime("%Y-%d-%m, %H:%M:%S")).all(),
      "upcoming_shows_count": upcoming_shows_count
    }
    return render_template('pages/show_artist.html', artist=data)
  except:
    return render_template('errors/404.html')
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form.get('name','')
    artist.city = request.form.get('city','')
    artist.state = request.form.get('state','')
    artist.phone = request.form.get('phone','')
    artist.genres = ','.join(request.form.getlist('genres'))
    artist.facebook_link = request.form.get('facebook_link','')
    artist.image_link = request.form.get('image_link','')
    artist.website_link = request.form.get('website_link','')
    artist.seeking_venue = request.form.get('seeking_venue','')
    artist.seeking_description = request.form.get('seeking_description','')
    db.session.add(artist)
    db.session.commit()
    flash('Venue ' + request.form['name'] + '  was successfully update!')
  except:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
 
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue= Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    venue = Venue.query.get(venue_id)
    venue.name = request.form.get('name','')
    venue.city = request.form.get('city','')
    venue.state = request.form.get('state','')
    venue.address = request.form.get('address','')
    venue.phone = request.form.get('phone','')
    venue.genres = ','.join(request.form.getlist('genres'))
    venue.facebook_link = request.form.get('facebook_link','')
    venue.image_link = request.form.get('image_link','')
    venue.website_link = request.form.get('website_link','')
    venue.seeking_talent = request.form.get('seeking_talent','')
    venue.seeking_description = request.form.get('seeking_description','')
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + '  was successfully update!')
  except:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    name = request.form.get('name','')
    city = request.form.get('city','')
    state = request.form.get('state','')
    phone = request.form.get('phone','')
    genres = ','.join(request.form.getlist('genres'))
    facebook_link = request.form.get('facebook_link','')
    image_link = request.form.get('image_link','')
    website_link = request.form.get('website_link','')
    seeking_venue = request.form.get('seeking_venue','')
    seeking_description = request.form.get('seeking_description','')
    artist = Artist(name=name,city=city,state=state,phone=phone,genres=genres,image_link=image_link,facebook_link=facebook_link,website_link=website_link,seeking_venue=seeking_venue,seeking_description=seeking_description)
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  query = db.session.query(
    Venue,
    Artist,
    Show,
    Artist.name.label("artist_name"),
    Artist.id.label("artist_id"),
    Artist.image_link.label("artist_image_link"),
    Venue.name.label("venue_name"),
    Venue.id.label("venue_id"),
    Venue.image_link.label("venue_image_link"),
    Show.start_time
  ).join(Show, Show.venue_id == Venue.id).join(Artist,Show.artist_id == Artist.id)
  data=query.all()
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    artist_id = request.form.get('artist_id','') 
    venue_id = request.form.get('venue_id','')
    start_time = request.form.get('start_time','')
    show = Show(artist_id=artist_id,venue_id=venue_id,start_time=start_time)
    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Show could not be listed.')
  
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
