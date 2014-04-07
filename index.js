
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

// tableName and descriptionColumn name should never com from user data since
// that would open us up to SQL injection attacks.
var processRequestRandom = function(req, res, tableName, descriptionColumnName, descriptionFilter) {

	if (!descriptionColumnName) {
		res.send(500, { error: 'something blew up' });
		return;
	}

	// Initialize an empty data set.
	var dataSet = [];

	db.each("SELECT * FROM " + tableName + " WHERE GeoLookupType=1 order by RANDOM() LIMIT 100",
		function(err, row) {  // Row Handler, called once per row.

		if (err) {
			res.send(500, { error: 'something blew up' });
			return;
		}

		if (row)
		{
			dataSet.push({
				DataSetID: tableName,
				Lat: row.Lat ? row.Lat : fakeLat(),
				Long: row.Long? row.Long : fakeLong(),
				Date: row.DateVal,
				Description: row[descriptionColumnName],
				Meta: row,
			});
		}
	},

	function(err, rowCount) {  // Query complete handler, called after query is executed.
		if (err) {
			res.send(500, { error: 'something blew up' });
			return;
		}
		res.json(dataSet);
	});
};

// tableName and descriptionColumn name should never com from user data since
// that would open us up to SQL injection attacks.
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

	var maxLat = 90,
			minLat = -90,
			maxLong = 180,
			minLong = -180;

	if (req.query.maxLat) {
		maxLat = req.query.maxLat;
	}

	if (req.query.minLat) {
		minLat = req.query.minLat;
	}

	if (req.query.maxLong) {
		maxLong = req.query.maxLong;
	}

	if (req.query.minLong) {
		minLong = req.query.minLong;
	}


	// Retrieve the start and end date or create one if needed.
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

	// Initialize an empty data set.
	var dataSet = []
	limit = 10000;
	if (descriptionFilter == 'random') {
		orderBy = 'RANDOM()';
		descriptionFilter = "";
		limit = 100;
	} else {
		orderBy = 'DateVal';
	}

	db.each("SELECT * FROM " + tableName + " WHERE " + descriptionColumnName + " LIKE ? AND DateVal BETWEEN ? AND ? AND Lat BETWEEN ? AND ? AND Long BETWEEN ? AND ? ORDER BY ? DESC LIMIT ?",
			'%' + descriptionFilter + '%',
			startDate.unix(),
			endDate.unix(),
			minLat,
			maxLat,
			minLong,
			maxLong,
			orderBy,
			limit,
		function(err, row) {  // Row Handler, called once per row.

		if (err) {
			res.send(500, { error: 'something blew up' });
			return;
		}

		if (row)
		{
			dataSet.push({
				DataSetID: tableName,
				Lat: row.Lat ? row.Lat : fakeLat(),
				Long: row.Long? row.Long : fakeLong(),
				Date: row.DateVal,
				Description: row[descriptionColumnName],
				Meta: row,
			});
		}
	},

	function(err, rowCount) {  // Query complete handler, called after query is executed.
		if (err) {
			res.send(500, { error: 'something blew up' });
			return;
		}

		res.json(dataSet);
	});
};

var addHeaders = function(res) {
	res.header("Access-Control-Allow-Origin", "*");
	res.header("Access-Control-Allow-Headers", "X-Requested-With");
};

app.use(express.compress());

app.get('/calls', function(req, res){
	addHeaders(res);
	processRequest(req, res, 'DispatchLogs','NatureOfCall');
});

app.get('/calls/type/random', function(req, res){
	addHeaders(res);
	processRequestRandom(req, res, 'DispatchLogs','NatureOfCall');
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
