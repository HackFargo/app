
var express = require('express');
var app = express();
var fs = require('fs');
var sqlite3 = require('sqlite3');
var moment = require('moment');

var db = new sqlite3.Database("./tools/hackfargo.db");

var fakeLat = function() {
	var latMax = 46.919749,
		latMin = 46.803665;

	return latMin + (latMax - latMin) * Math.random();
};

var fakeLong = function() {
	var longMax = -96.785670,
		longMin = -96.900340;

	return longMin + (longMax - longMin) * Math.random();
};

var processRequest = function(req, res, tableName, descriptionColumnName, descriptionFilter) {
	var startDate = moment().subtract('days', 15), 
		endDate;

	if (!descriptionColumnName) {
		res.send(500, { error: 'something blew up' });
		return;	
	}

	if (!descriptionFilter) {
		descriptionFilter = '';
	}	

	if (req.query.start && moment(req.query.start).isValid()) {
		startDate = moment(req.query.start);
	}

	if (req.query.end && moment(req.query.end).isValid()) {
		endDate = moment(req.query.end);
	} else if (!(req.query.start) || !moment(req.query.end).isValid()) {
		// No dates were provided, default end date is today
		endDate = moment();
	} else {
		endDate = moment(startDate).add('days', 15)
	}
	
	// Set the end date to the end of the day.
	if (endDate){
		endDate.endOf('day');
	}

	db.all("SELECT * FROM " + tableName + " WHERE " + descriptionColumnName + " LIKE ? AND DateVal BETWEEN ? AND ? ORDER BY DateVal DESC LIMIT 10000", '%' + descriptionFilter + '%', startDate.unix(), endDate.unix(), function(err, rows) {
	 
		if (err) {
			res.send(500, { error: 'something blew up' });
			return;
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

var addHeaders = function(res) {
	res.header("Access-Control-Allow-Origin", "*");
	res.header("Access-Control-Allow-Headers", "X-Requested-With");
};

app.get('/calls', function(req, res){
	addHeaders(res);
	processRequest(req, res, 'DispatchLogs','NatureOfCall');
});
	

app.get('/calls/type/:typeFilter', function(req, res) {
	addHeaders(res);
 	processRequest(req, res, 'DispatchLogs', 'NatureOfCall', req.params.typeFilter);
});

app.get('/permits', function(req, res){
	addHeaders(res);
	processRequest(req, res, 'BuildingPermits','PermitType');
});
	

app.get('/permits/type/:typeFilter', function(req, res) {
	addHeaders(res);
 	processRequest(req, res, 'BuildingPermits', 'PermitType', req.params.typeFilter);
});

app.listen(8181);
console.log('Server running at http://0.0.0.0:8181/');