#########################################################################################
### p717epsg.py
###
### Functions to get data from EPSG dataset to do some checks in p717checker and p72000top717.py
###   To be included in p717checker program as: from p717records import *
### 
###
### File contains
###   1) Dicts with constants 
###   2) Helper functions for reading, writing, comparing (parsing is done in class)
###
### v1: draft based on v0.9 of user spec
### This code is sample code, provided AS-IS.  Do with it whatever you want, but make sure to check.
###
### Bert Kampes, 2017-12-25
#########################################################################################

COMMON_PROJPARAMETER_NAMES = [
    'Latitude of natural origin', 'Longitude of natural origin', 'Scale factor at natural origin', 'False easting', 'False northing',  # most Mercator variants
    'Latitude of projection centre', 'Longitude of projection centre', 'Azimuth of initial line', 'Angle from Rectified to Skew Grid', 'Scale factor on initial line', 'False easting', 'False northing', # Hotine
    'Latitude of false origin', 'Longitude of false origin', 'Latitude of 1st standard parallel', 'Latitude of 2nd standard parallel', 'Easting at false origin', 'Northing at false origin' # Albers and LCC 2SP
    'Latitude of natural origin', 'Longitude of natural origin', 'Scale factor at natural origin', 'False easting', 'False northing' # LCC 1SP
    ] # from www.epsg-registry.org



#####################################################################
### Helper functions to check, read, write data records.  
### Also see p717classes for constructors using rows of data indicated with asterisk
#####################################################################
import logging
import urllib.request, urllib.error


#####################################################################
### WKT = get_epsg_wkt(EPSG_CRS_CODE)
#####################################################################
# Get response from EPSG dataset as WKT.  Following url should work in an internet browser and show the ISO WKT:
#    url = http://www.epsg-registry.org//export.htm?wkt=urn:ogc:def:crs:EPSG::32065
# In python this is as simple as:
#    response = urllib.request.urlopen(url)
#    wkt = response.read()
# to get the string.  However, we have to deal with proxy settings. You may have to add your proxy.
#
### Bert Kampes 2017-12-23
#####################################################################
### put this in a module EPSGdataset.py
def get_epsg_wkt(epsg_crs_code):
    url = 'http://www.epsg-registry.org/export.htm?wkt=urn:ogc:def:crs:EPSG::'+ str(epsg_crs_code)
    logging.debug("Trying to GET %s", url)
    ### First try without proxy, should work if not behind a firewall
    do_proxy=False
    try:
        response = urllib.request.urlopen(url)
    except urllib.error.URLError as e:
        # returns error code e.g., 404, 501, ...
        logging.debug("simple url request returned error code %s", e)
        logging.debug("trying with proxy.  You may have to configure this is you are behind a firewall")
        do_proxy=True
    except urllib.error.URLError as e:
        # not an HTTP specific error (e.g., connection refused)
        logging.debug("simple url request returned URL error %s", e.reason)
        logging.debug("trying with proxy")
        do_proxy=True
    if do_proxy==True:
        try:
            # do a try/ check if on Shell network to get proxy
            proxy_support = urllib.request.ProxyHandler({'http' : 'http://houic-cc-31001.americas.shell.com:8080'})
            request       = urllib.request.Request(url)
            opener        = urllib.request.build_opener(proxy_support)
            urllib.request.install_opener(opener)
            response      = urllib.request.urlopen(request)
        except urllib.error.URLError as e:
            logging.debug("proxy url request returned error code %s", e.code)
        except urllib.error.URLError as e:
            logging.debug("proxy url request returned URL error %s", e.reason)
        else:
            logging.info("proxy worked")
            
    wkt = response.read()
    logging.debug("WKT: %s", wkt)
    return wkt


#try:
#    get_epsg_wkt(32065)
#except:
#    print('epsg lookup failed')

#test:
#get_epsg_wkt(32065)
#exit()



### EOF.