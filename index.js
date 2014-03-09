
var express = require('express');
var app = express();
var fs = require('fs');
var sqlite3 = require('sqlite3');
var moment = require('moment');

var defaultDate = moment('March 7, 2014')
var db = new sqlite3.Database("./tools/hackfargo.db");

var processRequest = function(req, res) {
	var startDate = defaultDate, endDate;

	if (req.query.start) {
		startDate = moment(req.query.start);
	}

	if (req.query.end) {
		endDate = moment(req.query.end);
	} else {
		endDate = startDate;
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
					Lat: row.Lat,
					Long: row.Long,
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