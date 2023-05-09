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