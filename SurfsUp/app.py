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
engine = create_engine("sqlite:///hawaii.sqlite")


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
@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days = 365)
    

    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year).all()
    
    prcp_dic = {}
    for result in results:
        prcp_dic[result[0]] = result[1]

    return jsonify(prcp_dic)

@app.route("/api/v1.0/stations")
def stations():
    total_stations = session.query(Station.station, Station.name).all()
    

    station_list = []
    for result in total_stations: 
        station_dic = {}
        station_dic["Station"] = result[0]
        station_dic["Name"] = result[1]
        station_list.append(station_dic)

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days = 365)
    
    most_active = session.query(Measurement.station).\
                group_by(Measurement.station).\
                order_by(func.count().desc()).first()[0]
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.station == most_active).\
                filter(Measurement.date >= one_year).\
                order_by(Measurement.date.desc()).all()
    

    tobs_list = []
    for date,tobs in tobs_data: 
        tobs_dic = {}
        tobs_dic["date"] = date
        tobs_dic["tobs"] = tobs
        tobs_list.append(tobs_dic)

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def temperature_start(start):
    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= start).all()
 

    temperature_start_list = []
    for min_temp, max_temp, avg_temp in results: 
        temperature_start_dic = {}
        temperature_start_dic["TMIN"] = min_temp
        temperature_start_dic["TMAX"] = max_temp
        temperature_start_dic["TAVG"] = avg_temp
        temperature_start_list.append(temperature_start_dic)

    return jsonify(temperature_start_list)

@app.route("/api/v1.0/<start>/<end>")
def temperature_range(start, end):
    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    temperature_range_list = []
    for min_temp, max_temp, avg_temp in results: 
        temperature_range_dic = {}
        temperature_range_dic["TMIN"] = min_temp
        temperature_range_dic["TMAX"] = max_temp
        temperature_range_dic["TAVG"] = avg_temp
        temperature_range_list.append(temperature_range_dic)

    return jsonify(temperature_range_list)

session.close()

if __name__ == '__main__':
    app.run(debug=True)