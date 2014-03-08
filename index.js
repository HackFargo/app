
var express = require('express');
var app = express();
var fs = require('fs');
var moment = require('moment');

var getPathForDate = function (date) {
	return './tools/json/' + date.format('MM-DD-YYYY') + '.json';
};

app.get('/calls', function(req, res){

	var startDate = moment('March 8, 2010'), endDate;
	
	if (req.query.start) {
		startDate = moment(req.query.start);
	}

	if (req.query.end) {
		endDate = moment(req.query.end);
	}

	fs.readFile(getPathForDate(date), {encoding: 'utf-8'}, function(err, data){
		var callsForDay = JSON.parse(data);
		res.json(callsForDay);
	});
	
});

app.get('/calls', function(req, res){

	var date = moment('March 8, 2010');
	if (req.query.start) {
		date = moment(req.query.start);
	}


	fs.readFile(getPathForDate(date), {encoding: 'utf-8'}, function(err, data){
		var calls = JSON.parse(data);
		res.json(calls);
	});
	
});


app.listen(8181);
console.log('Server running at http://0.0.0.0:8181/');