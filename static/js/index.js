let map, infoWindow;
let app = {};
// import { MarkerClusterer } from "@googlemaps/markerclusterer";
let init = (app) =>{

  app.enumerate = (a) => {
    // This adds an _idx field to each element of the array.
    let k = 0;
    a.map((e) => {e._idx = k++;});
    return a;
};

  app.init = () => {
    window.initMap = initMap;
    // app.vue.get_observations();
    // console.log(app.vue.observations)
    // console.log("getobs")
    
    initMap();
    // console.log("done")
  };
  app.get_observations = function () {
    axios.get(observations_url)
      .then(function (r) {
        app.vue.observations = r.data.observations
     })
  };

  app.search = function () {
    if (app.vue.query.length > 1) {
      axios.get(search_url, {params: {q: app.vue.query}}).then(function(search_results){
        app.vue.search_results = search_results.data.search_results;
      });
    } else {
      app.vue.search_results = [];
    }
    
  };

  app.add_interest = function (result) {
    axios.post(add_interest_url, {species_id: result.id, species_name: result.common_name}).then(response => {
      console.log('Interest added successfully');
    })
    .catch(error => {
      console.error('Failed to add interest', error)
    });
  };

  app.clear_search = function () {
    this.query = "";
    app.vue.search_results = [];
  };

  app.data ={
    observations: [],
    search_results: [],
    query: "",
  };
  app.methods = {
    get_observations: app.get_observations,
    search: app.search,
    add_interest: app.add_interest,
    clear_search: app.clear_search,
  };
  app.vue = new Vue({
    el: "#vue-target",
    data: app.data,
    methods: app.methods
  });
  async function initMap() {
    const { Map } = await google.maps.importLibrary("maps");
    const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");
    // const { MarkerClusterer} = await google.maps.importLibrary("markerClusterer");
    map = new Map(document.getElementById("map"), {
      center: { lat: 37.0902, lng: -100},
      zoom: 5,
      streetViewControl: false,
      mapId: 'MainMap'
    });
    
    console.log("mapping")
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
    console.log("waiting points")
    await axios.get(observations_url)
    .then(function (r) {
      app.vue.observations = r.data.observations
 })

  // console.log(app.vue.observations)
  const markers =  app.vue.observations.map(obs => {
    const marker = new google.maps.Marker({
      position: { lat: obs['latitude'], lng: obs['longitude']},
      map: map,
    });
    marker.addListener("click", () => {
      infoWindow.setContent(obs['common_name']);
      infoWindow.open(map, marker);
    });
    return marker;
   });

   const markerCluster = new markerClusterer.MarkerClusterer({ markers, map });

  console.log("done obs")
    
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
  app.init()
};


init(app);