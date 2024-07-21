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
from flask_migrate import Migrate

from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

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
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    website = db.Column(db.String(120), nullable=True)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500), nullable=True)

    shows = db.relationship('Show', backref='venue', lazy=True)
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

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    website = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500), nullable=True)
    shows = db.relationship('Show', backref='artist', lazy=True)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)

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
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  
  # Query to get all venues and group them by city and state
  venues_query = db.session.query(Venue).all()
  
  # Create a dictionary to store the data
  data = []
  cities_states = set((venue.city, venue.state) for venue in venues_query)
  
  for city_state in cities_states:
      city, state = city_state
      venues_in_city_state = [venue for venue in venues_query if venue.city == city and venue.state == state]
      
      venues_data = []
      for venue in venues_in_city_state:
          num_upcoming_shows = len([show for show in venue.shows if show.start_time > datetime.now()])
          venues_data.append({
              "id": venue.id,
              "name": venue.name,
              "num_upcoming_shows": num_upcoming_shows,
          })
      
      data.append({
          "city": city,
          "state": state,
          "venues": venues_data
      })
  
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  search_term = request.form.get('search_term', '')
  search_term = f"%{search_term.lower()}%"
  
  # Perform case-insensitive search using SQLAlchemy
  venues_query = Venue.query.filter(Venue.name.ilike(search_term)).all()
  
  # Prepare the response data
  response = {
      "count": len(venues_query),
      "data": []
  }
  
  for venue in venues_query:
      num_upcoming_shows = len([show for show in venue.shows if show.start_time > datetime.now()])
      response["data"].append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": num_upcoming_shows,
      })

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  # Query the venue by ID
  venue = Venue.query.get(venue_id)
  if not venue:
      return render_template('errors/404.html'), 404
  
  # Query the past shows
  past_shows = Show.query.filter(Show.venue_id == venue_id, Show.start_time < datetime.now()).all()
  past_shows_data = []
  for show in past_shows:
      past_shows_data.append({
          "artist_id": show.artist.id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
      })

  # Query the upcoming shows
  upcoming_shows = Show.query.filter(Show.venue_id == venue_id, Show.start_time > datetime.now()).all()
  upcoming_shows_data = []
  for show in upcoming_shows:
      upcoming_shows_data.append({
          "artist_id": show.artist.id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
      })

  # Create the data structure

  # venue.genres = [Genre("Rock"), Genre("Jazz")]
  data = {
      "id": venue.id,
      "name": venue.name,
      # "genres": [genre.name for genre in venue.genres],
      "genres": venue.genres,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": past_shows_data,
      "upcoming_shows": upcoming_shows_data,
      "past_shows_count": len(past_shows_data),
      "upcoming_shows_count": len(upcoming_shows_data),
  }
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
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
    form = VenueForm(request.form)

    if form.validate():
        try:
            # Create a new Venue object
            new_venue = Venue(
                name=form.name.data,
                genres=form.genres.data,
                address=form.address.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                website=form.website_link.data,
                facebook_link=form.facebook_link.data,
                seeking_talent=form.seeking_talent.data,
                seeking_description=form.seeking_description.data,
                image_link=form.image_link.data
            )

            # Add the new Venue to the database
            db.session.add(new_venue)
            db.session.commit()

            # Flash success message
            flash('Venue ' + new_venue.name + ' was successfully listed!')
            return redirect(url_for('index'))

        except Exception as e:
            # Rollback in case of error and flash error message
            db.session.rollback()
            flash('An error occurred. Venue ' + form.name.data + ' could not be listed. Error: ' + str(e))
            return render_template('forms/new_venue.html', form=form)

    # If form is not valid, render the form again with error messages
    flash('Please correct the errors below and try again.')
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        # Find the venue by its ID
        venue = Venue.query.get(venue_id)
        
        if venue is None:
            # Venue not found
            flash('Venue not found.')
            return redirect(url_for('index'))

        # Delete the venue from the database
        db.session.delete(venue)
        db.session.commit()

        # Flash success message
        flash('Venue ' + venue.name + ' was successfully deleted!')
        return redirect(url_for('index'))

    except Exception as e:
        # Rollback in case of error and flash error message
        db.session.rollback()
        flash('An error occurred. Venue could not be deleted. Error: ' + str(e))
        return redirect(url_for('index'))
    
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

    # Query all artists from the database
    artists = Artist.query.all()
    
    # Format the data to match the expected structure
    data = [{"id": artist.id, "name": artist.name} for artist in artists]
    
    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  search_term = request.form.get('search_term', '').strip().lower()
    
  # Query the database for artists with names containing the search term
  artists = Artist.query.filter(
      Artist.name.ilike(f'%{search_term}%')
  ).all()
  
  # Format the data for response
  response = {
      "count": len(artists),
      "data": [{
          "id": artist.id,
          "name": artist.name,
          "num_upcoming_shows": len(UpcomingShow.query.filter_by(artist_id=artist.id).all()) 
      } for artist in artists]
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)
  # return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  # Query the artist with the given artist_id from the database
    artist = Artist.query.get(artist_id)
    
    if artist is None:
        # Handle the case where the artist_id does not exist
        flash('Artist not found!', 'error')
        return redirect(url_for('artists'))
    
    # Query the past shows for this artist
    past_shows = Show.query.filter(Show.artist_id == artist_id, Show.start_time < datetime.utcnow()).all()
    upcoming_shows = Show.query.filter(Show.artist_id == artist_id, Show.start_time >= datetime.utcnow()).all()
    
    # Format the data
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres.split(','),
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": [{
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": show.start_time.isoformat()
        } for show in past_shows],
        "upcoming_shows": [{
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": show.start_time.isoformat()
        } for show in upcoming_shows],
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
    
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    
    if artist is None:
        flash('Artist not found!', 'error')
        return redirect(url_for('artists'))

    form = ArtistForm(obj=artist)
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm(request.form)
    artist = Artist.query.get(artist_id)

    if artist is None:
        flash('Artist not found!', 'error')
        return redirect(url_for('artists'))

    if form.validate():
        try:
            # Update artist with new data from the form
            artist.name = form.name.data
            artist.genres = ','.join(form.genres.data)  # Assuming genres is a list
            artist.city = form.city.data
            artist.state = form.state.data
            artist.phone = form.phone.data
            artist.website = form.website_link.data
            artist.facebook_link = form.facebook_link.data
            artist.seeking_venue = form.seeking_venue.data
            artist.seeking_description = form.seeking_description.data
            artist.image_link = form.image_link.data

            db.session.commit()
            flash(f'Artist {artist.name} was successfully updated!', 'success')
            return redirect(url_for('show_artist', artist_id=artist_id))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Artist could not be updated.', 'error')
    else:
        flash('Form validation failed. Please check the input values.', 'error')

    # If form validation fails, re-render the edit form with validation errors
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # Query the database to get the venue with the specified ID
  venue = Venue.query.get(venue_id)

  # If the venue is not found, flash an error message and redirect to the venues list page
  if venue is None:
      flash('Venue not found!', 'error')
      return redirect(url_for('venues'))

  # Initialize the form with values from the venue object
  form = VenueForm(obj=venue)

  # Render the edit venue template with the form and venue data
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  # Retrieve the venue from the database using the provided ID
    venue = Venue.query.get(venue_id)

    # If the venue is not found, flash an error message and redirect to the venues list page
    if venue is None:
        flash('Venue not found!', 'error')
        return redirect(url_for('venues'))

    # Populate the venue object with data from the form
    form = VenueForm(request.form, obj=venue)

    # Validate the form
    if form.validate():
        try:
            # Update the venue with the new data from the form
            form.populate_obj(venue)
            
            # Commit the changes to the database
            db.session.commit()

            # Flash a success message
            flash('Venue ' + venue.name + ' was successfully updated!', 'success')
        except Exception as e:
            # If there’s an error, roll back the session and flash an error message
            db.session.rollback()
            flash('An error occurred. Venue ' + venue.name + ' could not be updated. Error: ' + str(e), 'error')
    
    # Redirect to the venue's detail page
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  
  form = ArtistForm(request.form)
    
  if form.validate():
      try:
          # Create a new Artist object using form data
          artist = Artist(
              name=form.name.data,
              genres=form.genres.data,
              city=form.city.data,
              state=form.state.data,
              phone=form.phone.data,
              website=form.website_link.data,
              facebook_link=form.facebook_link.data,
              seeking_venue=form.seeking_venue.data,
              seeking_description=form.seeking_description.data,
              image_link=form.image_link.data
          )
          
          # Add the new artist to the session and commit to the database
          db.session.add(artist)
          db.session.commit()
          
          # Flash success message
          flash('Artist ' + artist.name + ' was successfully listed!', 'success')
          
      except Exception as e:
          # Rollback in case of error
          db.session.rollback()
          
          # Flash error message
          flash('An error occurred. Artist ' + form.name.data + ' could not be listed. Error: ' + str(e), 'error')
      
  else:
      # If the form is not valid, flash an error message
      flash('An error occurred. The form data was not valid.', 'error')
    
    # Redirect to the home page after form submission
  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  # Query the database to get all shows
  shows = Show.query.join(Artist).join(Venue).all()
  
  data = []
  for show in shows:
      data.append({
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
      })
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
        # Get form data
        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']
        start_time = request.form['start_time']

        # Create a new Show record
        new_show = Show(
            artist_id=artist_id,
            venue_id=venue_id,
            start_time=start_time
        )

        # Add and commit the new Show to the database
        db.session.add(new_show)
        db.session.commit()

        # On successful db insert, flash success
        flash('Show was successfully listed!')
  except Exception as e:
      # Rollback in case of error
      db.session.rollback()
      flash(f'An error occurred. Show could not be listed. Error: {str(e)}')
  finally:
      # Close the session
      db.session.close()

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
