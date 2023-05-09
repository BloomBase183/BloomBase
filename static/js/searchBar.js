export default {
    data() {
      return {
        searchTerm: "",
      };
    },
    methods: {
      search() {
        alert(`Searching for: ${this.searchTerm}`);
      },
    },
    template: `
      <div>
        <input type="text" v-model="searchTerm">
        <button v-on:click="search">Search</button>
      </div>
    `,
};