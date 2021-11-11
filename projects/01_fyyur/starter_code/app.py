#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

## TODO: connect to a local postgresql database  ##Done
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(100))
    up_show_count = db.Column(db.Integer, default=0)
    past_shows_count = db.Column(db.Integer, default=0)
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
      return f'<Venue {self.id} {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate ##Done

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(100))
    up_show_count = db.Column(db.Integer, default=0)
    past_shows_count = db.Column(db.Integer, default=0)
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
      return f'<Artist {self.id} {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate ##Done

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

##Association table
class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id', ondelete='CASCADE'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id', ondelete='CASCADE'), nullable = False)

    def __repr__(self):
        return f'<Show {self.id} {self.artist_id} {self.venue_id} {self.start_time}>'
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


db.create_all()

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')
#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.  ##Done
  # num_upcoming_shows should be aggregated based on number of upcoming shows per venue. ##done

  venue_query = Venue.query.group_by(Venue.id, Venue.state, Venue.city).all()
  location = ''
  data = []

  up_show = []
  up_show = db.session.query(Show).filter(Show.start_time > datetime.now()).all()
  for venue in venue_query:
    if location == venue.city + venue.state:
      data[len(data) - 1] ["venues"].append({
        "id": venue.id,"name": venue.name,"num_ up_show": len(up_show)})
    else:
      location = venue.city + venue.state
      data.append({
        "state": venue.state,"city": venue.city,
        "venues": [{"id": venue.id,"name": venue.name,"num_ up_show": len(up_show)}]
      })
  return render_template('pages/venues.html', areas=data)

####SEARCH VENUE 
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. ##Done
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee" 
  search_term = request.form.get('search_term')
  venue_query = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
  count_venues = len(venue_query)
  response={
    "count": count_venues,"data": venue_query
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term'))


####BONUS Search show
@app.route('/shows/search', methods=['POST'])
def search_show():
  search_term = request.form.get('search_term', '')
  venue_search = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
  artist_search = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()
  show_id = [] 
  data = []
  show_query_all = Show.query.all()
  for show in show_query_all:
      for venue in venue_search:
        for artist in artist_search:
          if ((venue.id == show.venue_id ) and (artist.id == show.artist_id)):
                 data.append({
                    "venue_id": show.venue_id,"venue_name": show.venue.name,"artist_id": show.artist_id,
                    "artist_name": show.artist.name, "artist_image_link": show.artist.image_link,
                    "start_time": str(show.start_time)
                  })
  
  count_show = len(show_id)         
  response={
    "count": count_show,"data": data
  }
  return render_template('pages/show.html', results=response, search_term=request.form.get('search_term'))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id  ##Done
  # TODO: replace with real venue data from the venues table, using venue_id ##Done
  venue_query = Venue.query.get(venue_id)
  past_show = []
  up_show = []
  shows = venue_query.shows
  for show in shows:
      show_details ={
        "artist_id": show.artist_id,"artist_name": show.artist.name,"artist_image_link": show.artist.image_link,
        "start_time": str(show.start_time)
       }
      if (show.start_time > datetime.now()):
        up_show.append(show_details)
      else:
        past_show.append(show_details)
  data={
    "id": venue_query.id,"name": venue_query.name,"genres": venue_query.genres.split(','),"address": venue_query.address,
    "city": venue_query.city,"state": venue_query.state,"phone": venue_query.phone,"website": venue_query.website_link,
    "facebook_link": venue_query.facebook_link,"seeking_talent": venue_query.seeking_talent,"seeking_description": venue_query.seeking_description,
    "image_link": venue_query.image_link,"past_shows": past_show,"up_show": up_show,"past_shows_count": len(past_show),
    "up_show_count": len(up_show)
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
  # TODO: insert form data as a new Venue record in the db, instead  ##Done
  # TODO: modify data to be the data object returned from db insertion
  create_venue = Venue()
  create_venue.name = request.form['name']
  create_venue.city = request.form['city']
  create_venue.state = request.form['state']
  create_venue.address = request.form['address']
  create_venue.phone = request.form['phone']
  create_venue.facebook_link = request.form['facebook_link']
  create_venue.genres = request.form['genres']
  create_venue.website_link = request.form['website_link']
  create_venue.seeking_description = request.form['seeking_description']
  
  try:
    db.session.add(create_venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('New Venue ' + request.form['name'] + ' is successfully created!')
    
  except:
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('Something error!!!. New Venue ' + request.form['name'] + ' could not be created.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close()
  return redirect(url_for('index'))

@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    try:
        venue_query = Venue.query.get(venue_id)
        venue_name = venue_query.name
        db.session.delete(venue_query)
        db.session.commit()
        flash('Venue ' + venue_name + ' is deleted')
    except:
         db.session.rollback()
         return "Something error!! Venue " + venue_name + " cannot be dleted"
    finally:
         db.session.close()
    return redirect(url_for('index'))

###Delete artist
@app.route('/artists/<int:artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

    try:
        artist = Artist.query.get(artist_id)
        artist_name = artist.name
        db.session.delete(artist)
        db.session.commit()
        flash('Artist ' + artist_name + ' is deleted')
    except:
         db.session.rollback()
         return "Something error!!. Artist " + venue_name + " cannot be dleted"
    finally:
         db.session.close()
    return redirect(url_for('index'))
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database  ##Done
  artist_query = Artist.query.all()
  return render_template('pages/artists.html', artists=artist_query)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. ##Done
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term = request.form.get('search_term')
  artist_search = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()
  count_artist= len(artist_search)

  response={
    "count": count_artist,
    "data": artist_search,
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term'))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id ##Done
  # TODO: replace with real artist data from the artist table, using artist_id
  artist_query = Artist.query.get(artist_id)
  shows = artist_query.shows
  past_show = []
  up_show = []
  for show in shows:
    show_details = {
      "venue_id": show.venue_id,"venue_name": show.venue.name,"venue_image_link": show.venue.image_link,
      "start_time": str(show.start_time)
    }
    if(show.start_time > datetime.now()):
      up_show.append(show_details)
    else:
      past_show.append(show_details)
  data = {
    "id": artist_query.id,"name": artist_query.name,"genres": artist_query.genres.split(','),"city": artist_query.city,"state": artist_query.state,
    "phone": artist_query.phone,"website": artist_query.website_link,"facebook_link": artist_query.facebook_link,"seeking_venue": artist_query.seeking_venue,
    "seeking_description":artist_query.seeking_description,"image_link": artist_query.image_link,"past_shows": past_show,
    "up_show": up_show,"past_shows_count": len(past_show),"up_show_count": len(up_show)
  }

  return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # TODO: populate form with fields from artist with ID <artist_id>

  form = ArtistForm()
  artist_query = Artist.query.get(artist_id)

  form.name.data = artist_query.name
  form.city.data = artist_query.city
  form.state.data= artist_query.state
  form.phone.data= artist_query.phone
  form.website_link.data= artist_query.website_link
  form.facebook_link.data= artist_query.facebook_link
  form.seeking_venue.data= artist_query.seeking_venue
  form.seeking_description.data= artist_query.seeking_description
  form.image_link.data= artist_query.image_link

  return render_template('forms/edit_artist.html', form=form, artist=artist_query)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
    form = ArtistForm()
    artist_query = Artist.query.get(artist_id)

    artist_query.name = form.name.data
    artist_query.phone = form.phone.data
    artist_query.state = form.state.data
    artist_query.city = form.city.data
    artist_query.genres = form.genres.data
    artist_query.image_link = form.image_link.data
    artist_query.facebook_link = form.facebook_link.data
    artist_query.seeking_description = form.seeking_description.data
    artist_query.seeking_venue= form.seeking_venue.data
    artist_query.website_link = form.website_link.data
    try:
      db.session.commit()
      flash('Artist ' + artist_query.name  + ' is successfully updated!')
    except:
      db.session.rollback()
      flash('Something error!!!. Artist ' + artist_query.name  + ' could not be updated.')
    finally:
      db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # TODO: populate form with values from venue with ID <venue_id> ##Done

  form = VenueForm()
  venue_query = Venue.query.get(venue_id)
  form.name.data = venue_query.name 
  form.genres.data = venue_query.genres 
  form.address.data = venue_query.address 
  form.city.data = venue_query.city 
  form.state.data = venue_query.state 
  form.phone.data = venue_query.phone 
  form.website_link.data = venue_query.website_link 
  form.facebook_link.data = venue_query.facebook_link 
  form.seeking_talent.data = venue_query.seeking_talent 
  form.seeking_description.data = venue_query.seeking_description 
  form.image_link.data = venue_query.image_link 
  
  return render_template('forms/edit_venue.html', form=form, venue=venue_query)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing  ##Done
  # venue record with ID <venue_id> using the new attributes
    form = VenueForm()
    venue_query = Venue.query.get(venue_id)

    venue_query.name = form.name.data
    venue_query.genres = form.genres.data
    venue_query.city = form.city.data
    venue_query.state = form.state.data
    venue_query.address = form.address.data
    venue_query.phone = form.phone.data
    venue_query.facebook_link = form.facebook_link.data
    venue_query.website_link = form.website_link.data
    venue_query.image_link = form.image_link.data
    venue_query.seeking_talent = form.seeking_talent.data
    venue_query.seeking_description = form.seeking_description.data
    try:
      db.session.commit()
      flash('Venue ' + venue_query.name+ ' is successfully updated!')
    except:
      db.session.rollback()
      flash('Something error!!!. Venue ' + venue_query.name+ ' could not be updated.')
    finally:
      db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form ##Done
  # TODO: insert form data as a new Venue record in the db, instead ##Done
  # TODO: modify data to be the data object returned from db insertion ##Done
  create_artist = Artist()
  create_artist.name = request.form['name']
  create_artist.city = request.form['city']
  create_artist.state = request.form['state']
  create_artist.genres = request.form['genres']
  create_artist.phone = request.form['phone']
  create_artist.facebook_link = request.form['facebook_link']
  create_artist.image_link = request.form['image_link']
  create_artist.website_link = request.form['website_link']
  create_artist.seeking_description = request.form['seeking_description']
  
  
  try:
    db.session.add(create_artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + create_artist.name + ' is successfully created!')
  except:
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead. ##Done
    flash('Something error!!!. Artist ' + create_artist.name + ' could not be created.')
  finally:
    db.session.close()
  return render_template('pages/home.html')



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.   ##done
  show_query_all = Show.query.all()
  show_data = []
  
  for show in show_query_all:
    if(show.start_time > datetime.now()):  ##only upcoming it will show
      show_data.append({
      "venue_id": show.venue_id,"venue_name": show.venue.name,"artist_id": show.artist_id,"artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,"start_time": str(show.start_time)
      })
  return render_template('pages/shows.html', shows=show_data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead  ##Done

  create_show = Show()
  create_show.artist_id = request.form['artist_id']
  create_show.venue_id = request.form['venue_id']
  create_show.start_time = request.form['start_time']
  try:
    db.session.add(create_show)
    Update_Artist= Artist.query.get(create_show.artist_id)
    Update_Venue= Venue.query.get(create_show.venue_id)
    db.session.commit()
    flash('Show is created successfully!')
  except:
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead. ##Done
    flash('Something error!!Show could not be created.')
  finally:
    db.session.close()
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
