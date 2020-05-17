import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")


Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

# create weather app
app = Flask(__name__)


latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
latest_date = list(np.ravel(latest_date))[0]

latest_date = dt.datetime.strptime(latest_date, "%Y-%m-%d")
latest_year = int(dt.datetime.strftime(latest_date, "%Y"))
latest_month = int(dt.datetime.strftime(latest_date, "%m"))
latest_day = int(dt.datetime.strftime(latest_date, "%d"))

year_before = dt.date(latest_year, latest_month, latest_day) - dt.timedelta(days=365)
year_before = dt.datetime.strftime(year_before, "%Y-%m-%d")


@app.route("/")
def home():
    return (
        f"Welcome to Surf's Up API - Hawaii<br/>"
        f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/stations ~~~~~ a list of all weather observation stations<br/>"
        f"/api/v1.0/precipitaton ~~ the latest year of precipitation data<br/>"
        f"/api/v1.0/tobs ~~ the latest year of temperature data<br/>"
        f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~<br/>"
        f"/api/v1.0/2013-06-08 ~~ low, high, and average temp for dates given and each date after<br/>"
        f"/api/v1.0/2013-06-08/2014-06-08 ~~ low, high, and average temp for dates given and each date up to and including end date<br/>"
        f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~<br/>"
        f"~ data available from 2010-01-01 to 2017-08-23 ~<br/>"
        f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    )


@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.name).all()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)


@app.route("/api/v1.0/precipitaton")
def precipitation():

    results = (
        session.query(Measurement.date, Measurement.prcp, Measurement.station)
        .filter(Measurement.date > year_before)
        .order_by(Measurement.date)
        .all()
    )

    precip_data = []
    for result in results:
        precip_dict = {result.date: result.prcp, "Station": result.station}
        precip_data.append(precip_dict)

    return jsonify(precip_data)


@app.route("/api/v1.0/tobs")
def tobs():

    results = (
        session.query(Measurement.date, Measurement.tobs, Measurement.station)
        .filter(Measurement.date > year_before)
        .order_by(Measurement.date)
        .all()
    )

    temp_data = []
    for result in results:
        temp_dict = {result.date: result.tobs, "Station": result.station}
        temp_data.append(temp_dict)

    return jsonify(temp_data)


@app.route("/api/v1.0/<start>")
def start(start):
    sel = [
        Measurement.date,
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs),
    ]

    results = (
        session.query(*sel)
        .filter(func.strftime("%Y-%m-%d", Measurement.date) >= start)
        .group_by(Measurement.date)
        .all()
    )

    dates = []
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)


@app.route("/api/v1.0/<start>/<end>")
def startEnd(start, end):
    sel = [
        Measurement.date,
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs),
    ]

    results = (
        session.query(*sel)
        .filter(func.strftime("%Y-%m-%d", Measurement.date) >= start)
        .filter(func.strftime("%Y-%m-%d", Measurement.date) <= end)
        .group_by(Measurement.date)
        .all()
    )

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
