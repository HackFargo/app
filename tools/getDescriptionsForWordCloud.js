// Combine the JSONs files output by the scrape calls in to one file.
var fs = require('fs');
var moment = require('moment');

var currentDate = moment('March 8, 2010');

var words = '';

var getPathForDate = function (date) {
	return './json/' + date.format('MM-DD-YYYY') + '.json';
};

while(currentDate.isBefore('March 8, 2014')) {
	var jsonString = fs.readFileSync(getPathForDate(currentDate), {encoding: 'utf-8'});

	var data = JSON.parse(jsonString);

	var length = data.DispatchLog.length;
	for (var i =0;  i < length; i++) {
		words += '\n' + data.DispatchLog[i].NatureOfCall;
	}
	
	currentDate.add('d', 1);
}




fs.writeFile('./words.txt', words, function(err) {
	if (err) throw err;

	console.log('Words saved');

});



