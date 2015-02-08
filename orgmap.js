<script type="text/javascript">
/* 
  Google Maps Javascript API Key
  I don't know how to get this to dynamically get
  inserted into the url below so put in both places(replace APIKEY below)
*/
var APIKEY = "";
/* Page url to fetch organizations from */
var ORGPAGEURL = "";
/* The div id to put the map into */
var MAPCANVASDIV = "map-canvas";
</script>
<script type="text/javascript"
  src="https://maps.googleapis.com/maps/api/js?key=APIKEY">
</script>
<script type="text/javascript"
  src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js">
</script>
<script type="text/javascript">
  function createMap(divid, map_options) {
    var map = new google.maps.Map(
        document.getElementById(divid),
        map_options
    );
    return map;
  }

  /*
  Fills in the org_markers with the created marker based on the org_link
  Places each created marker onto orgmap(global variable at this time because
   apparently I don't understand closures correctly yet)

  org_link is just an array
  [0] -> garbage
  [1] -> url
  [2] -> City
  [3] -> State
  [4] -> Link name
  */
  var org_markers = [];
  function make_org_marker(org_link) {
    var geo = new google.maps.Geocoder();
    var citystate = org_link[2] + ',' + org_link[3];
    console.log(citystate);
    geo.geocode(
      {address: citystate},
      function(georesult, geostatus) {
        console.log(geostatus);
        console.log(georesult[0]);
        var latlng = georesult[0].geometry.location;
        console.log(org_link[4]);
        console.log(latlng);
        /*
        var attribution = new google.maps.Attribution({
          source: org_link[4],
          webUrl: org_link[1]
        });
        */
        var orgmarker = new google.maps.Marker({
          map: orgmap,
          position: latlng,
          title: org_link[4]
          /*attribution: attribution*/
        });
        org_markers.push(orgmarker);
        google.maps.event.addListener(orgmarker, 'click', function() {
          var iw = new google.maps.InfoWindow({
            content: "<a href=\""+ org_link[1] + "\">" + org_link[4] + "</a>"
          });
          iw.open(orgmap, orgmarker);
        });
      }
    )
  }

  /*
  Parses html from organization page looking for any links in the form of
  <a href="url#city,state">Organization Name</a>
  
  Creates markers on the map from the parsed links and fills in 
  Org links are arrays of:
    [0] -> ignore
    [1] -> url to linkup page
    [2] -> city
    [3] -> state
    [4] -> org name
  */
  var ph = null;
  function get_org_links(orgpagehtml) {
      ph = orgpagehtml;
      var phlines = orgpagehtml.split('\n');
      var orglinks = [];
      for(i=0; i<ph.length; i++) {
        m = /href="(\S+)#(\w+),(\w+)".*>(.*)<\/a>/.exec(phlines[i]);
        if(m) {
          orglinks.push(m);
          make_org_marker(m);
        }
      }
      return orglinks;
  }

  /*
  Loads html from a given url and fills in the
  orglinks array with parsed links from the page
  */
  var orglinks = null;
  function load_org_links(pageurl) {
    $.get(pageurl, function(orgpagehtml){
      orglinks = get_org_links(orgpagehtml);
    })
  }

  /*
  Loads the organization google map
  Creates orgmap which is a google map instance with all
  organizations and places the map into map_div
  */
  var orgmap = null;
  function load_org_map(map_div) {
    var mapdivel = document.getElementById(map_div);
    if( mapdivel == null ) return;
    mapdivel.style.height = '1024px';
    var map_options = {
      center: { lat: 39.5, lng: -98.35},
      zoom: 3
    };
    orgmap = createMap(map_div, map_options);
    load_org_links(ORGPAGEURL);
  }
</script>
<script type="text/javascript">
  google.maps.event.addDomListener(window, 'load', function(){
    load_org_map(MAPCANVASDIV);
  });
</script>
