// Combine the JSONs files output by the scrape calls in to one file.
var fs = require('fs');
var moment = require('moment');

var currentDate = moment('March 8, 2014');

var logs = {DispatchLog: []};

var getPathForDate = function (date) {
	return './json/' + date.format('MM-DD-YYYY') + '.json';
};

while(currentDate.isBefore('May 4, 2014')) {
	var jsonString = fs.readFileSync(getPathForDate(currentDate), {encoding: 'utf-8'});

	var data = JSON.parse(jsonString);

	logs.DispatchLog = logs.DispatchLog.concat(data.DispatchLog);
	
	currentDate.add('d', 1);
}

console.log(logs.DispatchLog.length);



fs.writeFile('./json/combined.json', JSON.stringify(logs), function(err) {
	if (err) throw err;

	console.log('Combined DispatchLog saved');

});



