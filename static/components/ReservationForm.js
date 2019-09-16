const apiUrl = 'http://127.0.0.1:5000/';


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
        results: [],
    };
  },
    methods: {
      getReservationsFromJob: function(jobID){
            var timeout = "";
            var vm = this;

            var poller = function() {
                // fire another request
                axios.get('/results/'+ jobID)
                    .then(function(data, status, headers, config) {
                        if(data.status === 202) {
                            console.log(data, data.status);
                        } else if (data.status === 200){
                            vm.results.push(data.data);
                            console.log(vm.results);
                            clearTimeout(timeout);
                            return false;
                        }
                        timeout = setTimeout(poller, 2000);
                    })
                    .catch(function (error) {
                        console.log(error);
                    })

            };
            poller();
        },

        checkForm: function(e){
            e.preventDefault();

            this.errors = [];
            var vm = this;

            if (this.form.departing_date === '') {
                this.errors.push('Departure date is required.');
            } else {
                axios.post('/reservations', {
                form: this.form,
              })
              .then(function (response) {
                  var jobId = response.data;
                  console.log(jobId);
                  vm.getReservationsFromJob(jobId);
              })
              .catch(function (error) {
                    console.log(error);
              });
            }
        },
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
        <div v-if="results.length > 0">
            <ul id="example-1">
              <li v-for="result in results">
                {{ result }}
              </li>
            </ul>
        </div>
    </div>
  `,
};