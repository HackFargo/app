
var express = require('express');
var app = express();
var fs = require('fs');
var sqlite3 = require('sqlite3');
var moment = require('moment');

var db = new sqlite3.Database("./tools/hackfargo.db");

var fakeLat = function() {
	var latMax = 46.919749,
		latMin= 46.803665;

	return latMin + (latMax - latMin) * Math.random();
};

var fakeLong = function() {
	var longMax = -96.785670,
		longMin= -96.900340;

	return longMin + (longMax - longMin) * Math.random();
}

var processRequest = function(req, res) {
	var startDate = moment().subtract('days', 15), 
		endDate;

	if (req.query.start) {
		startDate = moment(req.query.start);
	}

	if (req.query.end) {
		endDate = moment(req.query.end);
	} else (!(req.query.start)) {
		// No dates were provided, default end date is today
		endDate = moment();
	} else {
		moment(startDate).add('days', 15)
	}
	
	// Set the end date to the end of the day.
	endDate.endOf('day')

	var descriptionColumnName = 'NatureOfCall';
	db.all("SELECT * FROM DispatchLogs WHERE DateVal BETWEEN ? AND ? LIMIT 10000", startDate.unix(), endDate.unix(), function(err, rows) {
	 
		if (err) {
			res.send(500, { error: 'something blew up' });
		}

		if (rows)
		{ 
			var dataSet = []
			rows.forEach(function (row) {
				dataSet.push({
					DataSetID: 'DispatchLogs',
					Lat: row.Lat ? row.Lat : fakeLat(),
					Long: row.Long? row.Long : fakeLong(),
					Date: row.DateVal,
					Description: row[descriptionColumnName],
					Meta: row,
				})
			});
			res.json(dataSet);
		}
	});
};

app.get('/calls', function(req, res){
	processRequest(req, res);
});
	

app.get('/calls/type/:id', function(req, res) {
  processRequest(req, res);
});

app.listen(8181);
console.log('Server running at http://0.0.0.0:8181/');