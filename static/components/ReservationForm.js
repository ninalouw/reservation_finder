const apiUrl = 'http://127.0.0.1:5000/';
// import Vue from '../../templates/index.html';
// import axios from '../components/static/templates/index.html';

export default {
  name: 'ReservationForm',
  data() {
    return {
        form: {
            departing_date: "",
            return_date: "",
            depart_term: "",
            arrive_term: "",
        },
        errors: [],
    };
  },
    methods: {
        submitForm: function(form) {
            this.form = form;
            console.log(this.form);
        },
        checkForm: function (e) {
            e.preventDefault();

            this.errors = [];

            if (this.form.departing_date === '') {
                this.errors.push('Departure date is required.');
            } else {
                axios.post('/', {
                form: this.form,
              })
              .then(function (response) {
                console.log(response);
              })
              .catch(function (error) {
                console.log(error);
              });
            }
        }
    },

  template: `
    <div class="container">
        <h2>Find a Ferry Reservation</h2>
        <form id="app" @submit="checkForm" method="post">
            <div class="form-group">
                <label>Departure Date</label>
                <input v-model="form.departing_date" placeholder="enter Departure date">
            </div>
            <div class="form-group">
                <label>Return Date</label>
                <input v-model="form.return_date" placeholder="enter Return date">
             </div>
            <div class="form-group">
                <label>Departure Terminal</label>
                <input v-model="form.depart_term" placeholder="enter Departure Terminal">
            </div>
            <div class="form-group">
                <label>Arrival Terminal</label>
                <input v-model="form.arrive_term" placeholder="enter arrival Terminal">
            </div>
            <button type="submit" class="btn btn-primary" @click="checkForm">Submit</button>
        </form>
    </div>
  `,
};