// api for returning geocoded strings from the postgis-enabled tiger database
/*
time psql -d hackfargo_gis -c "
SELECT g.rating, ST_X(g.geomout) As lon, ST_Y(g.geomout) As lat, (addy).address As stno, (addy).streetname As street,
(addy).streettypeabbrev As styp, (addy).location As city, (addy).stateabbrev As st,(addy).zip
FROM geocode('1728 35th st s, fargo ND 58103') As g; "

 rating |        lon        |       lat        | stno | street | styp | city  | st |  zip
--------+-------------------+------------------+------+--------+------+-------+----+-------
      0 | -96.8384208129789 | 46.8533715392449 | 1728 | 35th   | St   | Fargo | ND | 58103

*/
package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	_ "github.com/lib/pq"
	"log"
	"os"
)

type Configuration struct {
	//Users  []string
	Dbname   string
	User     string
	Password string
}

func loadconfig(configuration *Configuration) {
	// load config
	fmt.Print("Loading config.json...")
	file, _ := os.Open("./config.json")
	decoder := json.NewDecoder(file)
	err2 := decoder.Decode(&configuration)
	if err2 != nil {
		fmt.Println("error:", err2)
		os.Exit(1)
	}
	fmt.Println("success")
}

func dbconnect() *sql.DB {
	configuration := Configuration{}
	loadconfig(&configuration)
	db, _ := sql.Open("postgres", fmt.Sprintf("dbname=%s user=%s password=%s", configuration.Dbname, configuration.User, configuration.Password))
	return db
}

func main() {
	var (
		rating int
		lon    float64
		lat    float64
		stno   sql.NullString
		street sql.NullString
		styp   sql.NullString
		city   sql.NullString
		state  sql.NullString
		zip    sql.NullString
	)
	db := dbconnect()

	// let's try a query
	rows, err := db.Query("SELECT g.rating, ST_X(g.geomout) As lon, ST_Y(g.geomout) As lat, (addy).address As stno, (addy).streetname As street, (addy).streettypeabbrev As styp, (addy).location As city, (addy).stateabbrev As st,(addy).zip FROM geocode('Fargo, ND') As g;")
	if err != nil {
		log.Fatal(err)
		os.Exit(2)
	}
	for rows.Next() {
		if err := rows.Scan(&rating, &lon, &lat, &stno, &street, &styp, &city, &state, &zip); err != nil {
			log.Fatal(err)
		}
		fmt.Printf("%f, %f", lon, lat)
		fmt.Println("")
	}
	if err := rows.Err(); err != nil {
		log.Fatal(err)
		os.Exit(3)
	}
}
