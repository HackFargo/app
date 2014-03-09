var sqlite3 = require('sqlite3');

//var db = new sqlite3.Database("calls.db");
var db = new sqlite3.Database(":memory:");
  db.serialize(function() {
  db.run("CREATE TABLE lorem (info TEXT, time INT)");

  var stmt = db.prepare("INSERT INTO lorem VALUES (?, ?)");
  for (var i = 0; i < 10; i++) {
      stmt.run("Ipsum " + i, i);
  }
  stmt.finalize();

  db.all("SELECT * FROM DispactLogs LIMIT 10", function(err, rows) {
     
     if (rows)
     { 
      rows.forEach(function (row) {
          console.log(row.id + ": " + row.info + ' : '+ row.time);
      });
    }
  });

  db.all("SELECT rowid AS id, info, time FROM lorem WHERE info LIKE ? AND time BETWEEN ? AND ?", '%Ipsum%', 3, 8
    , function(err, rows) {
     console.log('Trying param query');
     if (rows)
     { 
      rows.forEach(function (row) {
          console.log(row.id + ": " + row.info + ' : '+ row.time);
      });
    }
  });
});

db.close();