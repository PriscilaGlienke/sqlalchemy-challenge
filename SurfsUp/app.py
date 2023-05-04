# Import the dependencies.
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# reflect an existing database into a new model
database_path = 'SurfsUp/Resources/hawaii.sqlite'
engine = create_engine(f"sqlite:///{database_path}")


# reflect the tables
Base = automap_base()
Base.prepare(engine, reflect=True)
# print(Base.classes.keys())


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
# Start at the homepage.
# List all the available routes.
@app.route("/")
def welcome():
    return (
        f"Congratulations! You've decided to treat yourself to a long holiday vacation in Honolulu, Hawaii. To help you with your trip planning, here are some interesting pages providing a climate analysis about the area:<br/>"
        f"<br/>"
        f"Check the Precipitation for 1 year here:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>"
        f"Check the Weather Stations here:<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>"
        f"Check the Temperature Observations for the Most Active Station here:<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"Check the Temperature Overview at a start date here (replace 'start' by YYYY-MM-DD):<br/>"
        f"/api/v1.0/start<br/>"
        f"<br/>"
        f"Check the Temperature Overview from a start to end date here (replace 'start/end' by YYYY-MM-DD/YYYY-MM-DD):<br/>"
        f"/api/v1.0/start/end<br/>"
    )

# Precipitation for 1 year page
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year from the last date in data set.
    one_year = dt.date(2017,8,23) - dt.timedelta(days = 365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year).all()
    
    # Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value. 
    prcp_dic = {}
    for result in results:
        prcp_dic[result[0]] = result[1]

    # Return the JSON representation of your dictionary.
    return jsonify(prcp_dic)

# Weather Stations page
@app.route("/api/v1.0/stations")
def stations():
    # Query to retrieve the list of stations in the dataset and their names
    total_stations = session.query(Station.station, Station.name).all()
    
# Create an empty station_list and append the data from the dictionary
    station_list = []
    for station, name in total_stations: 
        station_dic = {}
        station_dic["Station"] = station
        station_dic["Name"] = name
        station_list.append(station_dic)
    # Return a JSON list of stations from the dataset
    return jsonify(station_list)

# Temperature Observations page
@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date one year from the last date in data set.
    one_year = dt.date(2017,8,23) - dt.timedelta(days = 365)

    # Calculate the most active station id
    most_active_id = session.query(Measurement.station).\
                group_by(Measurement.station).\
                order_by(func.count().desc()).first()[0]
    # Query the last 12 months of temperature observation data for this station and plot the results as a histogram
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.station == most_active_id).\
                filter(Measurement.date >= one_year).\
                order_by(Measurement.date.desc()).all()
    

# Create an empty tobs_list and append the data from the dictionary
    tobs_list = []
    for date,tobs in tobs_data: 
        tobs_dic = {}
        tobs_dic["date"] = date
        tobs_dic["tobs"] = tobs
        tobs_list.append(tobs_dic)
    # Return a JSON list of stations from the dataset
    return jsonify(tobs_list)

# Temperature at a start date page
@app.route("/api/v1.0/<start>")
def temperature_start(start):
    # Create a query to calculate the lowest, highest, and average temperature from a specific start date.
    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= start).all()
 
    # Create an empty temperature_start_list and append the data from the dictionary
    temperature_start_list = []
    for min_temp, max_temp, avg_temp in results: 
        temperature_start_dic = {}
        temperature_start_dic["Temperature Min"] = min_temp
        temperature_start_dic["Temperature Max"] = max_temp
        temperature_start_dic["Temperature Avg"] = avg_temp
        temperature_start_list.append(temperature_start_dic)

    # Return a JSON list of stations from the dataset
    return jsonify(temperature_start_list)

# Temperature at a start to end date page
@app.route("/api/v1.0/<start>/<end>")
def temperature_range(start, end):
    # Create a query to calculate the lowest, highest, and average temperature from a specific start and end date.
    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Create an empty temperature_start_list and append the data from the dictionary
    temperature_range_list = []
    for min_temp, max_temp, avg_temp in results: 
        temperature_range_dic = {}
        temperature_range_dic["Temperature Min"] = min_temp
        temperature_range_dic["Temperature Max"] = max_temp
        temperature_range_dic["Temperature Avg"] = avg_temp
        temperature_range_list.append(temperature_range_dic)

    # Return a JSON list of stations from the dataset
    return jsonify(temperature_range_list)

#Close session
session.close()

#Debug
if __name__ == '__main__':
    app.run(debug=True)