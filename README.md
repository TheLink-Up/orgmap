# orgmap
Organizational Google Map

This map should work on any Ning network, but is specifically designed for [TheLink-Up.org](http://www.TheLink-Up.org)


# Setup

1. Create a new page in your network to hold organizations and note the url to this new page
2. Head over to your network and click My Network
3. Click custom code
4. In the custom code box paste the contents of [orgmap.js](orgmap.js) into the custom code box
5. Follow the Obtaining an API Key tutorial from [here](https://developers.google.com/maps/documentation/javascript/tutorial) to get a google maps api key
6. Put the key in the APIKEY variable and also replace APIKEY in the url below that with your api key
7. You can customize the map slightly by modifying MAPCENTER and MAPZOOMLEVEL if you want. By default it is set to show all of North America and centered just around Calgary, CA
8. Set the ORGPAGEURL to the url of your Ning page that contains your organizations
9. Click save
10. Create a new page in your network that will hold your map
11. Edit the page and switch the editor to the html view
12. Paste the following html code into the box which will be automatically replaced with your map
   
   ```
   <div id="map-canvas"></div>
   ```

# Organization Page

Your organization's page just needs to have links that follow a specific format. The orgmap.js will automatically find them all and put them on the map for you.

The format is as follows:

```
<a href="http://www.example.com#city,state">Org Name</a>
```

The link will then be parsed as follows:

* Url: http://www.example.com
* City: city
* State: state
* Name: Org Name

Then a query to Google's Geolocation service will be made for every link found using

```
city,state
```

as the address query.

The result from that query will determine the location of the marker.
The title(roll-over text) of the marker will be the Name and the url will be placed inside of the pop-up box

## Install orgmap cacher

For bluehost

1. Ensure you have python 2.7+ installed
2. git clone repo under ~/
3. cd orgmap
4. configure production.ini
5. setup virtualenv under env
6. source env/bin/activate
7. python setup.py install
8. pip install -r requirements-dev.txt
9. mkdir ~/public_html/orgmap
10. Edit orgmap.fcgi to have correct paths
11. cp .htaccess orgmap.fcgi ~/public_html/orgmap
12. chmod 755 ~/public_html/orgmap
