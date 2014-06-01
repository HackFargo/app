#!/bin/sh

cd api/data-api
echo "executing forever index.js on data api..."
forever index.js &

echo "executing geocoder api..."
cd ../geocoder/
#./geocode &