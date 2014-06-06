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
	Rating int            `json:"rating"`
	Lon    float64        `json:"lon"`
	Lat    float64        `json:"lat"`
	Stno   sql.NullString `json:"stno"`
	Street sql.NullString `json:"street"`
	Styp   sql.NullString `json:"styp"`
	City   sql.NullString `json:"city"`
	St     sql.NullString `json:"st"`
	Zip    sql.NullString `json:"zip"`
}

// let's make the db pointer global, for now, so we don't
// need to overload the http endpoint parameter list
//var db *sql.DB = dbconnect()
//var configuration = loadconfig()
var db *sql.DB = dbconnect()
var num_requests uint = 0
var cache map[string][]*GeoCodeResult = make(map[string][]*GeoCodeResult)
var cache_hits = 0

func loadconfig() *Configuration {
	// load config
	c := new(Configuration)
	fmt.Print("Loading config.json...")
	file, _ := os.Open("./config.json")
	decoder := json.NewDecoder(file)
	err2 := decoder.Decode(&c)
	if err2 != nil {
		fmt.Println("error:", err2)
		os.Exit(1)
	}
	fmt.Println("success")
	return c
}

func dbconnect() *sql.DB {
	var configuration = loadconfig()
	//loadconfig(&configuration)
	db, _ := sql.Open("postgres", fmt.Sprintf("dbname=%s user=%s password=%s", configuration.Dbname, configuration.User, configuration.Password))
	return db
}

func geo2json(obj GeoCodeResult) []byte {
	b, _ := json.Marshal(obj)
	return b
}

func json2geo(obj []byte) *GeoCodeResult {
	result := new(GeoCodeResult)
	return json.Unmarshal(obj, &result)
}

// return full struct for geo code result
// if db crashes, returns an empty list
//func geocode(db *sql.DB, query string) []*GeoCodeResult {
func geocode(query string) []*GeoCodeResult {
	// let's try a query
	rlist := []*GeoCodeResult{}
	num_requests++

	// check cache
	var ok bool
	_, ok = cache[query]
	//fmt.Println(fmt.Sprintf("Is '%s' in cache (%d items)? %d", query, len(cache), ok))
	if ok == true {
		cache_hits++
		return cache[query]
	}

	rows, err := db.Query("SELECT g.rating, ST_X(g.geomout) As lon, ST_Y(g.geomout) As lat, (addy).address As stno, (addy).streetname As street, (addy).streettypeabbrev As styp, (addy).location As city, (addy).stateabbrev As st,(addy).zip FROM geocode($1) As g;", query)
	if err != nil {
		log.Fatal(err)
	}
	if err := rows.Err(); err != nil {
		log.Fatal(err)
	}

	for rows.Next() {
		result := new(GeoCodeResult)
		if err := rows.Scan(&(result.Rating), &(result.Lon), &(result.Lat), &(result.Stno), &(result.Street), &(result.Styp), &(result.City), &(result.St), &(result.Zip)); err != nil {
			log.Fatal(err)
		}
		rlist = append(rlist, result)
	}
	cache[query] = rlist
	return rlist
}

// return just lon, lat -- no structs
func geocode_longlat(query string) (float64, float64) {
	gc := geocode(query)
	// todo: check for length bounds here
	if len(gc) > 0 {
		return gc[0].Lon, gc[0].Lat
	}
	return 0, 0 // todo: make this a real error
}

// HTTP Endpoints
func http_geocoder(w http.ResponseWriter, r *http.Request) {
	query := r.URL.Path[len("/geocode/"):]
	//lon, lat := geocode(db, query)
	gc := geocode(query)
	fmt.Fprintf(w, "[")
	delim := ""
	for i := 0; i < len(gc); i++ {
		// stno | street | styp |   city    | st |  zip
		fmt.Fprintf(w, "%s", delim)
		fmt.Fprintf(w, "{\"lon\":%.20f, \"lat\":%.20f, \"rating\":%d, \"stno\":\"%s\", \"street\":\"%s\", \"styp\":\"%s\", \"city\":\"%s\", \"state\":\"%s\", \"zip\":\"%s\"}", gc[i].Lon, gc[i].Lat, gc[i].Rating, gc[i].Stno.String, gc[i].Street.String, gc[i].Styp.String, gc[i].City.String, gc[i].St.String, gc[i].Zip.String)
		delim = ","
		fmt.Fprintln(w, "")

	}
	fmt.Fprintf(w, "]")
}

func http_root(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Hi there! Check out http://hackfargo.co")
}

func http_status(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "{\"status\": \"OK\", \"requests\": %d, \"cache_hits\": %d, \"cache_size\": %d}", num_requests, cache_hits, len(cache))
}

func main() {
	//lon, lat := geocode(db, "Fargo, ND")

	t := GeoCodeResult{10, 12.34, 56.24, sql.NullString{"200", true}, sql.NullString{"main", true}, sql.NullString{"ave", true}, sql.NullString{"fargo", true}, sql.NullString{"ND", true}, sql.NullString{"24542", true}}
	geo2json(t)
	/*r := geocode("Fargo, ND")
	fmt.Println(fmt.Sprintf("Fargo, ND: %.20f, %.20f", r[0].lon, r[0].lat))

	fmt.Println("Server listening on :8282")
	http.HandleFunc("/geocode/", http_geocoder)
	http.HandleFunc("/", http_root)
	http.HandleFunc("/status", http_status)
	log.Fatal(http.ListenAndServe(":8282", nil))*/
}
