# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


#################################################
# Database Setup
#################################################
# Create an engine to connect to the SQLite database
engine = create_engine("sqlite:///hawaii.sqlite")

# Create our session (link) from Python to the DB
session = Session(engine)


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB

session = Session(engine)
#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year ago from the last data point in the database
    most_recent_date = session.query(func.max(Measurement.date)).first()[0]
    one_year_ago = pd.to_datetime(most_recent_date) - pd.DateOffset(years=1)
    one_year_ago = one_year_ago.strftime('%Y-%m-%d')  # Convert to string
    
    
    
    
 # Query the last 12 months of precipitation data
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    
    # Convert query results to dictionary
    precip_data = {date: prcp for date, prcp in results}
    
    return jsonify(precip_data)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station, Station.name).all()
    
    # Convert list of tuples into normal list
    stations_list = list(np.ravel(results))
    
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date one year ago from the last data point in the database
    most_recent_date = session.query(func.max(Measurement.date)).first()[0]
    one_year_ago = pd.to_datetime(most_recent_date) - pd.DateOffset(years=1)
    one_year_ago = one_year_ago.strftime('%Y-%m-%d')
    
    # Find the most active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
                          group_by(Measurement.station).\
                          order_by(func.count(Measurement.station).desc()).first()[0]
    
    # Query the last 12 months of temperature observation data for the most active station
    results = session.query(Measurement.date, Measurement.tobs).\
              filter(Measurement.station == most_active_station).\
              filter(Measurement.date >= one_year_ago).all()
    
    # Convert list of tuples into normal list
    tobs_list = list(np.ravel(results))
    
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats(start, end=None):
    # If no end date provided, set it to the most recent date in the database
    if not end:
        end = session.query(func.max(Measurement.date)).first()[0]
    
    # Query the temperature statistics for the specified date range
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).\
              filter(Measurement.date <= end).all()
    
    # Convert list of tuples into a dictionary
    temp_stats = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }
    
    return jsonify(temp_stats)

if __name__ == '__main__':
    app.run(debug=True)
    
    
    
    