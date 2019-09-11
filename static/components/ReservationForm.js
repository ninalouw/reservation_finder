
export default {
  name: 'ReservationForm',
  data() {
    return {
      form: {
          departureDate: "",
          returnDate: "",
          departureTerminal: "",
          arrivalTerminal: "",
      },
    };
  },
    methods: {
        submitForm: function() {
          console.log(this.form);
        }
    },

  template: `
    <form>
        <input v-model="form.departureDate" placeholder="enter Departure date">
        <input v-model="form.returnDate" placeholder="enter Return date">
        <input v-model="form.departureTerminal" placeholder="enter Departure Terminal">
        <input v-model="form.arrivalTerminal" placeholder="enter arrival Terminal">
        <button type="submit" class="btn btn-primary" @click="submitForm"></button>
    </form>
  `,
};