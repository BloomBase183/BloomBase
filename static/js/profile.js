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

  app.fnotepopup = (fnote) => {
    app.data.currentnote = fnote;
  }
  app.close = (fnote) => {
    app.data.currentnote = null;
  }

  app.edit_field_note = function (note) {
    var noteTitle = document.getElementById("noteTitle").value;
    var noteContent = document.getElementById("noteContent").value;
    axios.post(edit_field_note_url, {content: noteContent, id: note.id, title: noteTitle})
      .then(response => {
        app.get_field_notes()
      })
      .catch(error => {
        console.error('Failed to edit field note!', error);
      });
  };

  app.delete_note = function (note_id) {
    axios.post(delete_field_note_url, {note_id: note_id})
      .then(response => {
        app.get_field_notes()
      })
      .catch(error => {
        console.error('Failed to delete field note!', error);
      });
  };

  app.get_field_notes = function () {
    axios.get(getfieldnotes_url) .then(function (r)  {
      app.data.field_notes = r.data.field_notes
      app.data.field_notes = app.enumerate(app.data.field_notes)
    });
  }


  app.data ={
    notes: [],
    field_notes: [],
    currentnote: null,
    obs4note: null,
  };

    app.methods = {
    close: app.close,
    fnotepopup: app.fnotepopup,
    edit_field_note: app.edit_field_note,
    get_field_notes: app.get_field_notes,
    delete_note: app.delete_note,
  };
  app.init = () => {
    app.get_field_notes()
    window.initMap = initMap;
    // app.vue.get_observations();
    // console.log(app.vue.observations)
    // console.log("getobs")
    initMap();
    // console.log("done")
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
    

    const map2 = new Map(document.getElementById("map2"), {
      center: { lat: 37.0902, lng: -100},
      zoom: 10,
      streetViewControl: false,
      mapId: 'FnoteMap'
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

            map2.setCenter(pos);
            map2.setZoom(10);
          },

        );
      } else {
        console.log("nolocation")
      }
    };
    console.log("waiting points")

console.log('got the points')
  // console.log(app.vue.observations)

  let markers = [];
  let markers2 = [];
  let empty_markers = [];
  // let markerCluster = new markerClusterer.MarkerClusterer({markers, map});
  
  // markerCluster.addMarkers(markers)
  axios.get(getfieldnotes_url).then(function (r)  {
    app.data.notes = r.data.field_notes
    markers2 =  app.vue.notes.map(obs => {
      console.log(obs)
      const marker2 = new google.maps.Marker({
        position: { lat: obs['latitude'], lng: obs['longitude']},
        map: map2,
      });
        marker2.addListener("click", () => {
        app.fnotepopup(obs);
        console.log('note click')
      });
      // markerCluster.addMarkers([marker]);
      return marker2;
  })
  // markers.splice(0,markers.length)
  });
  // console.log("done obs")
    
  };
  

  app.init()
};

init(app);