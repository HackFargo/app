/*

An HTTP API for a working postgis installation
Author: Blaine Booher (for HackFargo)

Current Status:
   * /geocode/<query:string> -- fully functional

   		To use the api endpoint, simply set up config.json with your
   		postgres parameters (in current directory), and run this
   		application. Then visit "http://localhost:8282/geocode/Fargo, ND"
   		which will return a json geocoded packet like:
   		{'lon': -96.88020266719587425541, 'lat': 46.71740545406462530309, 'rating': 100}

   		Data format subject to change, but likely only by adding new fields.

   		You can put any parsable string in there -- postgis handles the rest.

   		ex: "Fargo, ND", "Fargo, North Dakota 58103", "400 NP Ave, Fargo ND"

   		Production (running on http://gis.hackfargo.co) has minnesota and
   		north dakota tiger data loaded (but no other states), which should
   		cut down on abuse.


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
	"net/http"
	"os"
)

type Configuration struct {
	//Users  []string
	Dbname   string
	User     string
	Password string
}

type GeoCodeResult struct {
	rating int
	lon    float64
	lat    float64
	stno   sql.NullString
	street sql.NullString
	styp   sql.NullString
	city   sql.NullString
	st     sql.NullString
	zip    sql.NullString
}

// let's make the db pointer global, for now, so we don't
// need to overload the http endpoint parameter list
var db *sql.DB = dbconnect()

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

// return full struct for geo code result
func geocode(db *sql.DB, query string) []*GeoCodeResult {
	// let's try a query
	rows, err := db.Query("SELECT g.rating, ST_X(g.geomout) As lon, ST_Y(g.geomout) As lat, (addy).address As stno, (addy).streetname As street, (addy).streettypeabbrev As styp, (addy).location As city, (addy).stateabbrev As st,(addy).zip FROM geocode($1) As g;", query)
	if err != nil {
		log.Fatal(err)
		os.Exit(2)
	}
	if err := rows.Err(); err != nil {
		log.Fatal(err)
		os.Exit(3)
	}

	rlist := []*GeoCodeResult{}
	for rows.Next() {
		result := new(GeoCodeResult)
		if err := rows.Scan(&(result.rating), &(result.lon), &(result.lat), &(result.stno), &(result.street), &(result.styp), &(result.city), &(result.st), &(result.zip)); err != nil {
			log.Fatal(err)
		}
		rlist = append(rlist, result)
	}
	//return lon, lat
	//return result
	return rlist
}

// return just lon, lat -- no structs
func geocode_longlat(db *sql.DB, query string) (float64, float64) {
	gc := geocode(db, query)
	// todo: check for length bounds here
	if len(gc) > 0 {
		return gc[0].lon, gc[0].lat
	}
	return 0, 0 // todo: make this a real error
}

// HTTP Endpoints
func http_geocoder(w http.ResponseWriter, r *http.Request) {
	query := r.URL.Path[len("/geocode/"):]
	//lon, lat := geocode(db, query)
	gc := geocode(db, query)
	fmt.Fprintf(w, "[")
	for i := 0; i < len(gc); i++ {
		fmt.Fprintf(w, "{'lon': %.20f, 'lat': %.20f, 'rating': %d},", gc[i].lon, gc[i].lat, gc[i].rating)
	}
	fmt.Fprintf(w, "]")
}

func http_root(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Hi there! Check out http://hackfargo.co")
}

func main() {
	//lon, lat := geocode(db, "Fargo, ND")
	r := geocode(db, "Fargo, ND")
	fmt.Println(fmt.Sprintf("Fargo, ND: %.20f, %.20f", r[0].lon, r[0].lat))

	fmt.Println("Server listening on :8282")
	http.HandleFunc("/geocode/", http_geocoder)
	http.HandleFunc("/", http_root)
	http.ListenAndServe(":8282", nil)
}
