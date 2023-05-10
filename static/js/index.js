
let app = {};

let init = (app) => {
    app.data = {
        // Input for search bar
        userinput: "",
        // Results of species search in iNaturalist API
        results: []
    };

    // Function searches and extracts observations based on userinput
    app.search = function () {
      let url = `https://api.inaturalist.org/v1/observations?per_page=10&order=desc&order_by=created_at`;
      if (this.userinput !== "") {
        url += `&q=${this.userinput}`;
      }
      axios.get(url).then((response) => {
        this.results = response.data.results;
      });
    };

    // All methods can go here
    app.methods = {
      search: app.search
    };

    // Main vue for the project
    app.vue = new Vue({
        el: "#test",
        data: app.data,
        methods: app.methods
    });
    app.init()
};
init(app)