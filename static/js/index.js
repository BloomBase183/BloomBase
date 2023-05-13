let map, infoWindow;
let app = {};

let init = (app) =>{

  app.enumerate = (a) => {
    // This adds an _idx field to each element of the array.
    let k = 0;
    a.map((e) => {e._idx = k++;});
    return a;
};

  app.init = () => {
    window.initMap = initMap;
    app.vue.get_observations();
    console.log("getobs")
    initMap();
  };
  app.get_observations = function () {
    axios.get(observations_url)
      .then(function (r) {
        app.vue.observations = r.data.observations
     })
  };
  app.data ={
    observations: [],
  };
  app.methods = {
    get_observations: app.get_observations,
  };
  app.vue = new Vue({
    el: "#vue-target",
    data: app.data,
    methods: app.methods
  });
  app.init()
};
async function initMap(observations) {

  
  const { Map } = await google.maps.importLibrary("maps");
  const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");
  map = new Map(document.getElementById("map"), {
    center: { lat: 37.0902, lng: -100},
    zoom: 5,
    streetViewControl: false,
    mapId: 'MainMap'
  });
  infoWindow = new google.maps.InfoWindow();
 {
    // Try HTML5 geolocation.
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const pos = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          };

          infoWindow.setPosition(pos);
          infoWindow.setContent("You are here");
          infoWindow.open(map);
          map.setCenter(pos);
          map.setZoom(10);
        },
        () => {
          handleLocationError(true, infoWindow, map.getCenter());
        }
      );
    } else {
      handleLocationError(false, infoWindow, map.getCenter());
    }
  };
  const marker = new AdvancedMarkerElement({
    map: map,
    position: { lat: 36.96091408818179, lng:  -122.01768110588586},
    title: "Test ",
  });
};

function handleLocationError(browserHasGeolocation, infoWindow, pos) {
  infoWindow.setPosition(pos);
  infoWindow.setContent(
    browserHasGeolocation
      ? "Allow access to current location to get local data"
      : "Error: Your browser doesn't support geolocation."
  );
  infoWindow.open(map);
};

init(app);