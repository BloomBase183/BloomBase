/*
import searchBar from "./searchBar.js";

const app = new Vue({
  el: "#app",
  components: {
    searchBar,
  },
});
*/
let app = {};

let init = (app) => {
    app.data = {
        userinput: ""
    };

    app.vue = new Vue({
        el: "#test",
        data: app.data,
    });
};
init(app)