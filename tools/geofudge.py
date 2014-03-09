#!/usr/bin/env python2.7

"""
TESTING RESULTS
	LATITUDE IS SOLID TO A +/- 1 PERCENT THRESHOLD
	LONGITUDE IS SOLIDTO A +/- 4 PERCENT THRESHOLD

REQUIREMENTS:
	Block Numbers may only be integer types
	Road ONLY allows AVE/ST
	Road suffix ONLY allows N/S
"""

import math
import geocoder

latFloor = 46.919749  # Top of Fargo - North oriented
latMid = 46.876153  # 'Middle' of Fargo - Main & 45th
latCeiling = 46.803665  # Bottom of Fargo - North oriented

lonFloor = -96.785670  # Left of Fargo - North oriented
lonCeiling = -96.900340  # Right of Fargo - North oriented

latIncrement = (latFloor - latCeiling) / 52
lonIncrement = (abs(lonFloor) - abs(lonCeiling)) / 85


def geofudge(blockNum, roadNum, roadType, suffix):

    # Break hard and fast
    assert type(blockNum) is int
    #assert type(roadNum) is int
    assert type(roadType) is str
    assert type(suffix) is str

    success = True

    numBlocks = (blockNum / 100)
    roadType = roadType.upper()

    if roadType == "AVE":

        LONGITUDE = lonFloor + (lonIncrement * numBlocks)

        if suffix == "N":
            LATITUDE = latMid + (latIncrement * roadNum)

        elif suffix == "S":
            LATITUDE = latMid - (latIncrement * roadNum)

        else:
            success = False

    # Transform road to Longitude
    elif roadType == "ST":

        LONGITUDE = lonFloor + (lonIncrement * roadNum)
        if suffix == "N":
            LATITUDE = latMid + (latIncrement * numBlocks)
        elif suffix == "S":
            LATITUDE = latMid - (latIncrement * numBlocks)

        else:
            success = False

    else:
        success = False

    # if geofudge fails...go geocode
    if success == False:
        try:
            # return (blockNum, roadNum, roadType, suffix)
            return geocode(blockNum, roadNum, roadType, suffix).latlng
        except OVER_QUERY_LIMIT:
            raise Exception("!!!OVER_QUERY_LIMIT!!!")
        except:
            raise Exception("Even Google didn't figure this sh*t out...")

    return (LATITUDE, LONGITUDE)

# This is the real deal...also, real expensive.


def geocode(blockNum, roadNum, roadType, roadSuffix):
    g = geocoder.google("{0} {1} {2} {3}, Fargo, ND".format(blockNum, roadNum, roadType, roadSuffix))

    return g


def fudgetest(fake, real):

    # Lat/Lon Side by Side comparison
    #print("R Lat: %f F Lat: %f" % (real[0], fake[0]))
    #print("R Lon: %f F Lon: %f" % (real[1], fake[1]))

    # Lat/Lon Top by Bottom comparison
    #print("R Lat: %f R Lon: %f" % (real[0], real[1]))
    #print("F Lat: %f F Lon: %f" % (fake[1], fake[1]))

    lat = (real[0] * 0.99) < fake[0] < (real[0] * 1.01)
    lon = (real[1] * 0.98) < fake[1] < (real[1] * 1.5)

    # Lat/Lon DIFF
    print("lat diff: {0:6}%".format((real[0] / fake[0]) - 1))
    print("lon diff: {0}%".format((real[0] / fake[0]) - 1))

    # Range T/F Test
    # print(lat,lon)

if __name__ == '__main__':
    print("-------------------------")
    print("latFloor: %f" % latFloor)
    print("latCeiling %f" % latCeiling)
    print("lonFloor: %f" % lonFloor)
    print("lonCeiling: %f" % lonCeiling)
    print("-------------------------")
    print("latInc: %f" % latIncrement)
    print("lonInc: %f" % lonIncrement)
    print("-------------------------")

    '''TESTING FOR ACCEPTABLE RANGES'''
    # AVE S Testing
    fake1 = geofudge(2500, 23, "AVE", "S")
    real1 = (46.844215, -96.819778)
    fudgetest(fake1, real1)

    fake2 = geofudge(3300, 17, "AVE", "S")
    real2 = (46.854281, -96.833027)
    fudgetest(fake2, real2)

    fake3 = geofudge(600, 30, "AVE", "S")
    real3 = (46.844765, -96.770336)
    fudgetest(fake3, real3)

    # AVE N Testing
    fake4 = geofudge(1100, 13, "AVE", "N")
    real4 = (46.892776, -96.795156)
    fudgetest(fake4, real4)

    fake5 = geofudge(3200, 13, "AVE", "N")
    real5 = (46.890448, -96.829894)
    fudgetest(fake5, real5)

    fake6 = geofudge(800, 2, "AVE", "N")
    real6 = (46.878396, -96.792521)
    fudgetest(fake6, real6)

    # ST S Testing
    fake7 = geofudge(2600, 15.5, "ST", "S")
    real7 = (46.840624, -96.802558)
    fudgetest(fake7, real7)

    # ST N Testing
    fake9 = geofudge(700, 4, "ST", "N")
    real9 = (46.883132, -96.784711)
    fudgetest(fake9, real9)

    fake10 = geofudge(900, 26, "ST", "N")
    real10 = (46.885916, -96.821144)
    fudgetest(fake10, real10)

    fake11 = geofudge(1000, 18, "ST", "N")
    real11 = (46.887350, -96.809209)
    fudgetest(fake11, real11)

    fake11 = geofudge(0, 0, "ST", "N")
    real11 = (46.887350, -96.809209)
    fudgetest(fake11, real11)

    fake11 = geofudge(0, 0, "ST", "S")
    real11 = (46.887350, -96.809209)
    fudgetest(fake11, real11)

    fake11 = geofudge(0, 0, "AVE", "N")
    real11 = (46.887350, -96.809209)
    fudgetest(fake11, real11)

    fake11 = geofudge(0, 0, "AVE", "S")
    real11 = (46.887350, -96.809209)
    fudgetest(fake11, real11)

    fake11 = geofudge(0000, 0.5, "AVE", "N")
    real11 = (46.887350, -96.809209)
    fudgetest(fake11, real11)

    print geofudge(1400, "ALBRECHT", "BLVD", "N")
