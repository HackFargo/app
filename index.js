
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

// tableName name should never com from user data since
// that would open us up to SQL injection attacks.
var calculateQueryParams = function(req, tableName, descriptionColumnName) {
	var params = {
		tableName: tableName,
		descriptionColumnName: descriptionColumnName,
		descriptionFilter: req.params.typeFilter
	};

	if (!params.descriptionFilter) {
		params.descriptionFilter = '';
	}

	params.maxLat = 90;
	params.minLat = -90;
	params.maxLong = 180;
	params.minLong = -180;

	if (req.query.maxLat) {
		params.maxLat = req.query.maxLat;
	}

	if (req.query.minLat) {
		params.minLat = req.query.minLat;
	}

	if (req.query.maxLong) {
		params.maxLong = req.query.maxLong;
	}

	if (req.query.minLong) {
		params.minLong = req.query.minLong;
	}

	params.startDate = moment().subtract('days', 15);

	// Retrieve the start and end date or create one if needed.
	if (req.query.start && moment(req.query.start).isValid()) {
		params.startDate = moment(req.query.start);
	}

	if (req.query.end && moment(req.query.end).isValid()) {
		params.endDate = moment(req.query.end);
	} else if (!(req.query.start) || !moment(req.query.end).isValid()) {
		// No dates were provided, default end date is today
		params.endDate = moment();
	} else {
		params.endDate = moment(params.startDate).add('days', 15)
	}

	// Set the end date to the end of the day.
	if (params.endDate){
		params.endDate.endOf('day');
	}

	return params
};

var processRequestRandom = function(res, params) {

	// Initialize an empty data set.
	var dataSet = [];

	db.each("SELECT * FROM " + params.tableName + " WHERE GeoLookupType=1 order by RANDOM() LIMIT 100",
		function(err, row) {  // Row Handler, called once per row.

		if (err) {
			res.send(500, { error: 'something blew up' });
			return;
		}

		addRowToDataSet(dataSet, row, params);
	},

	function(err, rowCount) {  // Query complete handler, called after query is executed.
		if (err) {
			res.send(500, { error: 'something blew up' });
			return;
		}
		res.json(dataSet);
	});
};

var processRequest = function(res, params) {

	if (!params.descriptionColumnName) {
		res.send(500, { error: 'something blew up' });
		return;
	}

	// Initialize an empty data set.
	var dataSet = []

	db.each("SELECT * FROM " + params.tableName + " WHERE " + params.descriptionColumnName + " LIKE ? AND DateVal BETWEEN ? AND ? AND Lat BETWEEN ? AND ? AND Long BETWEEN ? AND ? ORDER BY ? DESC LIMIT ?",
			'%' + params.descriptionFilter + '%',
			params.startDate.unix(),
			params.endDate.unix(),
			params.minLat,
			params.maxLat,
			params.minLong,
			params.maxLong,
			'DateVal',
			10000,
		function(err, row) {  // Row Handler, called once per row.

		if (err) {
			res.send(500, { error: 'something blew up' });
			return;
		}

		addRowToDataSet(dataSet, row, params);
	},

	function(err, rowCount) {  // Query complete handler, called after query is executed.
		if (err) {
			res.send(500, { error: 'something blew up' });
			return;
		}

		res.json(dataSet);
	});
};

var addRowToDataSet = function(dataSet, row, params) {
	if (row)
	{
		dataSet.push({
			DataSetID: params.tableName,
			Lat: row.Lat ? row.Lat : fakeLat(),
			Long: row.Long? row.Long : fakeLong(),
			Date: row.DateVal,
			Description: row[params.descriptionColumnName],
			Meta: row,
		});
	}
};

var processCountRequest = function(res, params) {

	if (!params.descriptionColumnName) {
		res.send(500, { error: 'something blew up' });
		return;
	}

	db.get("SELECT COUNT(*) as count FROM " + params.tableName + " WHERE " + params.descriptionColumnName + " LIKE ? AND DateVal BETWEEN ? AND ? AND Lat BETWEEN ? AND ? AND Long BETWEEN ? AND ?",
			'%' + params.descriptionFilter + '%',
			params.startDate.unix(),
			params.endDate.unix(),
			params.minLat,
			params.maxLat,
			params.minLong,
			params.maxLong,
		function(err, row) {  // Row Handler, called once per row.

		if (err) {
			res.send(500, { error: 'something blew up' });
			return;
		}
			res.json({
				count: row['count']
			});
	});
};



var addHeaders = function(res) {
	res.header("Access-Control-Allow-Origin", "*");
	res.header("Access-Control-Allow-Headers", "X-Requested-With");
};

app.use(express.compress());

var endpoints = [
	{
		endpoint: 'calls',
		table: 'DispatchLogs',
		descriptionColumn: 'NatureOfCall'
	},
	{
		endpoint: 'permits',
		table: 'BuildingPermits',
		descriptionColumn: 'PermitType'
	}
];

endpoints.forEach(function(endpoint) {
		app.get('/' + endpoint.endpoint, function(req, res){
			addHeaders(res);
			processRequest(res, calculateQueryParams(req, endpoint.table, endpoint.descriptionColumn));
		});

		app.get('/' + endpoint.endpoint + '/count', function(req, res){
			addHeaders(res);
			processCountRequest(res, calculateQueryParams(req, endpoint.table, endpoint.descriptionColumn));
		});

		app.get('/' + endpoint.endpoint + '/type/random', function(req, res){
			addHeaders(res);
			processRequestRandom(res, calculateQueryParams(req, endpoint.table, endpoint.descriptionColumn));
		});

		app.get('/' + endpoint.endpoint + '/type/:typeFilter', function(req, res) {
			addHeaders(res);
			processRequest(res, calculateQueryParams(req, endpoint.table, endpoint.descriptionColumn));
		});

		app.get('/' + endpoint.endpoint + '/type/:typeFilter/count', function(req, res) {
			addHeaders(res);
			processCountRequest(res, calculateQueryParams(req, endpoint.table, endpoint.descriptionColumn));
		});
});

app.listen(8181);
console.log('Server running at http://0.0.0.0:8181/');
