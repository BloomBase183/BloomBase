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
  app.popup = (obs) =>{
    
    //Put the popup code in here
    app.vue.clicked_observation = obs;
    //As part of the popup we calculate the average density of the flower
    window.obsmapstart = obsmapstart;
  

    //Put the popup code in here
    obsmapstart(obs);
  
    app.average_density(obs.id);
    app.has_rated_density(obs.id);
    
    app.fnote(obs);
  }

  app.depop = () => {
    app.vue.clicked_observation = null;
    //clear the average density
    app.vue.observation_average = -1;
    app.vue.rated_density = false;
    app.vue.notes = [];
  };

  //function for grabbing field notes for 
  //clicked observation
  app.fnote = function (obs) {
    axios.post(field_note_url, {observation: obs})
      .then(response => {
        app.vue.notes = response.data.field_notes;
        
      })
      .catch(error => {
        console.error('Failed to retrieve notes', error);
      });
  };

  app.interest_list = function () {
    axios.get(interest_url)
      .then(function(l) {
        app.vue.interests = l.data.interests;
      });
  };

  app.init = () => {
    window.initMap = initMap;
    // app.vue.get_observations();
    // 
    // 
    app.interest_list();
    initMap();
    // 
  };

  app.get_observations = function () {
    axios.get(observations_url)
      .then(function (r) {
        app.vue.observations = r.data.observations;
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

  app.post_note = function (iNat_url, long, lat,obs) {
    var noteTitle = document.getElementById("noteTitle").value;
    var noteContent = document.getElementById("noteContent").value;
    axios.post(post_note_url, {title: noteTitle, noteContent: noteContent, iNat_url: iNat_url, long: long, lat: lat }) // Corrected variable name
      .then(response => {
        app.fnote(obs);
        document.getElementById("noteTitle").value = ''
        document.getElementById("noteContent").value = ''
      })
      .catch(error => {
        // Handle any errors
        console.error(error);
      });
  };

  app.show_observation = function (observation) {
    
    this.clicked_observation = observation;
  };

  app.add_interest = function (result) {
    axios.post(add_interest_url, {species_id: result.id, species_name: result.common_name, scientific_name: result.scientific_name, species_image: result.image_url})
    .then(response => {
      
      app.interest_list();
    })
    .catch(error => {
      console.error('Failed to add interest', error)
    });    
    //app.interest_list();
  };

  // Func drops the given interest in the db
  app.drop_interest = function (interest){
    axios.post(drop_interest_url, {interest_id: interest.id, user_email: interest.user_email})
      .then(response => {
        
        app.interest_list();
      })
      .catch(error => {
        console.error('Failed to drop interest', error);
      });
  };

  // displays the like number on ui
  app.like = function (fnote) {
    axios.post(like_post_url, {id: fnote.id})
    .then(response => {
      //will fill with get likes count function
      
      if (response.data === true) {
        fnote.like_count += 1;
      } 
      else if (response.data === false) {
        
      } else {
        fnote.like_count += 1;
        fnote.dislike_count -= 1;
        
        
      }
      
      app.update_like(response.data, fnote)
    })
    .catch(error => {
      console.error('Failed to like field note', error);
    });
  };


  app.rate_density = function (rating, obs_id, obs_date) {
    //Stores a user rating on a bloom
    
    axios.post(rate_density_url, {rating: rating, id: obs_id, date: obs_date}).then(response => {
      
      app.average_density(obs_id);
      app.has_rated_density(obs_id);
    })
    .catch(error => {
      console.error('Failed to rate observation Density', error)
    });
  };

  app.average_density = function(obs_id) {
    //
    axios.post(average_density_url, {id: obs_id}).then(response => {
      
      //set the average to the returned value
      app.vue.observation_average = response.data.average;
      return 1
    })
    .catch(error => {
      console.error('Failed to get average', error)
      //don't set the observation value so it stays at the default -1
      return -1;
    });
  };

  app.has_rated_density = function(obs_id) {
    
    axios.post(has_rated_density_url, {id: obs_id}).then(response => {
      //Sees if the user has rated it previously or not
      app.vue.rated_density = response.data.rated;
    })
    .catch(error => {
      console.error('Failed to check if the user has rated the observation before', error)
    });
  };


  app.delete_observation_rating = function (obs_id){
    axios.post(delete_observation_rating_url, {id: obs_id}).then(response =>{
      
      app.average_density(obs_id);
      app.has_rated_density(obs_id);
    });
  };

  app.edit_observation_rating = function (obs_rating, obs_id, obs_date){
    axios.post(update_observation_rating_url, {id: obs_id, rating: obs_rating, observed_on: obs_date}).then(response =>{
      
      app.average_density(obs_id);
    });
  };

  // updates the like count in field notes
  app.update_likes = function(response, fnote) {
    axios.post(update_likes_url, {response:response, note: fnote})
      .then(r => {
        
        
      });
  };

  // displays the dislike number on ui
  app.dislike = function (fnote) {
    axios.post(dislike_post_url, {id: fnote.id})
    .then(response => {
      //will fill with get dislikes count function
      
      if (response.data === true) {
        fnote.dislike_count += 1;
      } 
      else if (response.data === false){
        
      } else {
        fnote.like_count -= 1;
        fnote.dislike_count += 1;
        
        
      }
    
      app.update_dislikes(response.data, fnote)
      
    })
    .catch(error => {
      console.error('Failed to dislike field note', error);
    });
  };

  // updates the field note dislike field 
  app.update_dislikes = function(response, fnote) {
    axios.post(update_dislikes_url, {response:response, note: fnote})
      .then(r => {
      });
  };

  
  app.drop_interest = function (interest){
    axios.post(drop_interest_url, {interest_id: interest.id, user_email: interest.user_email})
      .then(response => {
        
        app.interest_list();
      })
      .catch(error => {
        console.error('Failed to drop interest', error)
      });
  };

  app.clear_search = function () {
    
    this.query = "";
    app.vue.search_results = [];
  };

  app.data ={
    iNat_url: "",
    long: "",
    lat: "",
    observations: [],
    markers: [],
    currentMarkers: [],
    map,
    search_results: [],
    query: "",
    clicked_observation: null,
    filterinterests: false,
    notes: [],
    noteContent: "",
    observation_average: -1,
    observation_rating: 0,
    rated_density: false,
    interests: [],
    clicked_search: null,
    loclist: [],
    imgl: [],
    sldshwind: 0,
    srchobs: [],  
  };

  app.methods = {
    post_note: app.post_note,
    get_observations: app.get_observations,
    search: app.search,
    add_interest: app.add_interest,
    clear_search: app.clear_search,
    show_observation: app.show_observation,
    interonly: app.interonly,
    popup: app.popup,
    depop: app.depop,
    fnote: app.fnote,
    rate_density: app.rate_density,
    average_density: app.average_density,
    has_rated_density: app.has_rated_density,
    delete_observation_rating: app.delete_observation_rating,
    edit_observation_rating: app.edit_observation_rating,
    interest_list: app.interest_list,
    drop_interest: app.drop_interest,
    like: app.like,
    update_likes: app.update_likes,
    dislike: app.dislike,
    update_dislikes: app.update_dislikes,
    srchpopup: app.srchpopup,
    desrchpop: app.desrchpop,
  };

  app.vue = new Vue({
    el: "#vue-target",
    data: app.data,
    methods: app.methods
  });

  async function initMap() {
    const { Map } = await google.maps.importLibrary("maps");
    const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");

    
    const map = new Map(document.getElementById("map"), {
      center: { lat: 37.0902, lng: -100},
      zoom: 10,
      streetViewControl: false,
      mapId: 'MainMap'
    });

    app.data.map = map

    
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
    

  
  // 

  let markers = [];
  let markers2 = [];
  let empty_markers = [];
  let markerCluster = new markerClusterer.MarkerClusterer({ empty_markers, map });
   google.maps.event.addListener(map, "idle", () => {
    let bounds = map.getBounds()
    let ne = bounds.getNorthEast();
    let sw = bounds.getSouthWest();
    axios.get(observations_url, {params: {
      lat_max: ne.lat(), lat_min: sw.lat(),
      lng_min: sw.lng(), lng_max: ne.lng(), filter: app.data.filterinterests,
    }})
    .then(function (r)  {

      app.vue.observations = []
      app.vue.observations = r.data.observations

      markers =  app.vue.observations.map(obs => {
        const marker = new google.maps.Marker({
          position: { lat: obs['latitude'], lng: obs['longitude']},
          map: map,
        });

        marker.addListener("click", () => {

          app.popup(obs);
        });

        return marker;
    })


    markerCluster.clearMarkers();
    
    
    markerCluster.addMarkers(markers);
    
    

    
  });


  })
   
    
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

app.interonly = function() {
  
  app.data.map.setZoom(app.data.map.getZoom());
  app.data.filterinterests = !app.data.filterinterests;
};
async function searchmapstart () {
  const { Map } = await google.maps.importLibrary("maps");
  app.vue.searchmap = new Map(document.getElementById("searchmap"), {
    center: { lat: 37.0902, lng: -100},
    zoom: 3,
    streetViewControl: false,
    mapId: 'searchmap'
  });
}
async function obsmapstart (obs) {

  const { Map } = await google.maps.importLibrary("maps");
  app.vue.obsmap = new Map(document.getElementById("obsmap"), {
    center: { lat: 37.0902, lng: -100},
    zoom: 3,
    streetViewControl: false,
    mapId: 'obsmap'
  });
  
  new google.maps.Marker({
    position: { lat: obs['latitude'], lng: obs['longitude']},
    map: app.vue.obsmap,
  });

}
app.srchpopup = (obs) =>{
  window.searchmapstart = searchmapstart;
  
  //Put the popup code in here
  app.vue.clicked_search = obs;
  
  app.vue.sldshwind = 0;
  
  let daname = obs.common_name
  searchmapstart();
  let markers = []
  axios.get(observations_by_name, {params: {
    obname: daname
  }})
  .then(function (r)  {

    app.vue.srchobs = []
    app.vue.srchobs = r.data.observations
    markers =  app.vue.srchobs.map(obs => {
      
      
      const marker = new google.maps.Marker({
        position: { lat: obs['latitude'], lng: obs['longitude']},
        map: app.vue.searchmap,
      });
      // 
      marker.addListener("click", () => {

        app.popup(obs);
      });

      return marker;
  })
  
});

}
app.popup = (obs) =>{
  window.obsmapstart = obsmapstart;
  

  //Put the popup code in here
  app.vue.clicked_observation = obs;
  obsmapstart(obs);

  
  app.fnote(obs);
};
app.desrchpop = () => {
  app.vue.clicked_search = null;
  app.vue.srchobs = [];
}
init(app);
