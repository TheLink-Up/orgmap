# orgmap
Organizational Google Map

This map should work on any Ning network, but is specifically designed for [TheLink-Up.org](http://www.TheLink-Up.org)


# Setup

1. Head over to your network and click My Network
2. Click custom code
3. In the custom code box paste the contents of [orgmap.js](orgmap.js) into the custom code box
4. Follow the Obtaining an API Key tutorial from [here](https://developers.google.com/maps/documentation/javascript/tutorial) to get a google maps api key
5. Put the key in the APIKEY variable and also replace APIKEY in the url below that with your api key
6. Set the ORGPAGEURL to the url of your Ning page that contains your organizations
7. Create a new page in your network(Probably call it Organizational Map or similar)
8. Edit the page and switch the editor to the html view
9. Paste the following html code into the box which will be automatically replaced with your map
   
   ```
   <div id="map-canvas"></div>
   ```
