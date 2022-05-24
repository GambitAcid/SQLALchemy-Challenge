from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, and_, desc, func
import datetime as dt
import pandas as pd
import numpy as np
import datetime 
from flask import Flask, jsonify

#Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=True, connect_args={"check_same_thread": False})

#Refelcting our existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)
#Base.classes.keys()

#Saving our references to a table 
Measurement = Base.classes.measurement
Station = Base.classes.station

#Creating our session link from Python to the DB 
session = Session(engine)

#Creating the weather app 
app = Flask(__name__)

recentDate = (session.query(Measurement.date)
                .order_by(Measurement.date.desc())
                .first())
recentDate = list(np.ravel(recentDate))[0]

recentDate = dt.datetime.strptime(recentDate, '%Y-%m-%d')
recentYear = int(dt.datetime.strftime(recentDate, '%Y'))
recentMonth = int(dt.datetime.strftime(recentDate, '%m'))
recentDay= int(dt.datetime.strftime(recentDate, '%d'))

year_prior = dt.date(recentYear, recentMonth, recentDay) - dt.timedelta(days=365)
year_prior = dt.datetime.strftime(year_prior, '%Y-%m-%d')

#Creating Homepage route and lsiting all available routes 
@app.route("/")
def home():
    return (f"Welcome to Surf's Up! Climate API<br/>"
            f"---------------------------------------<br/>"
            f"All Available Routes:<br/>"
            f"/api/v1.0/precipitaton<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/temperature<br/>"
            f"---------------------------------------<br/>"
            f"~~~ datesearch (yyyy-mm-dd)<br/>"
            f"/api/v1.0/<start><br/>"
            f"/api/v1.0/<start>/<end><br/>"
            f"---------------------------------------<br/>")
        

#Convert the query results to a dictionary using date as the key and prcp as the value
#returning a jsonified dictionary
@app.route("/api/v1.0/precipitaton")
def precipitation():
    
    results = (session.query(Measurement.date, Measurement.prcp, Measurement.station)
                    .filter(Measurement.date > year_prior)
                    .order_by(Measurement.date)
                    .all())
    
    precip = []
    for result in results:
        precipDict = {result.date: result.prcp, "Station": result.station}
        precip.append(precipDict)

    return jsonify(precip)

#Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.name).all()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)    

#Query the dates and temperature observations of the most active station 
#for the previous year of data. Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/temperature")
def temperature():

    results = (session.query(Measurement.date, Measurement.tobs, Measurement.station)
                    .filter(Measurement.date > year_prior)
                    .order_by(Measurement.date)
                    .all())

    tempData = []
    for result in results:
        tempDict = {result.date: result.tobs, "Station": result.station}
        tempData.append(tempDict)

    return jsonify(tempData)

    #Return a JSON list of the minimum temperature, the average temperature, 
#and the maximum temperature for a given start or start-end range.
@app.route('/api/v1.0/datesearch/<startDate>')
def start(startDate):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel)
                    .filter(func.strftime("%Y-%m-%d", Measurement.date) >= startDate)
                    .group_by(Measurement.date)
                    .all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates from the start date 
#through the end date (inclusive).
@app.route('/api/v1.0/datesearch/<startDate>/<endDate>')
def startEnd(startDate, endDate):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel)
                    .filter(func.strftime("%Y-%m-%d", Measurement.date) >= startDate)
                    .filter(func.strftime("%Y-%m-%d", Measurement.date) <= endDate)
                    .group_by(Measurement.date)
                    .all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)


if __name__ == "__main__":
    app.run(debug=True)        