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
        fields: ['Arrival Terminal', 'Departure Terminal', 'Vessel', 'Arrival', 'Departing'],
        results: [],
        loading: false,
        dismissSecs: 10,
        dismissCountDown: 0,
        progressMessage: 'Searching BC Ferries',
        progressMessages: ['Searching BC Ferries','Entering dates', 'Selecting terminals', 'Entering passenger information', 'Entering driver information',
        'Parsing available sailings', 'Selecting available reservations for sailings'],
    };
  },
    methods: {
      countDownChanged: function(dismissCountDown) {
        this.dismissCountDown = dismissCountDown;
      },
      showAlert: function(counter) {
        this.dismissCountDown = this.dismissSecs;
        if (counter < 6){
            this.progressMessage = this.progressMessages[counter];
        } else {
            this.progressMessage = this.progressMessages[6];
        }
      },
      getReservationsFromJob: function(jobID){
            var timeout = "";
            var vm = this;
            var counter = 0;

            var poller = function() {
                // fire another request
                axios.get('/results/'+ jobID)
                    .then(function(data, status, headers, config) {
                        if(data.status === 202) {
                            //show progress message
                            counter += 1;
                            vm.showAlert(counter);
                        } else if (data.status === 200){
                            vm.loading = false;
                            vm.results.push(data.data);
                            var results = vm.results;
                            clearTimeout(timeout);
                            return false;
                        }
                        timeout = setTimeout(poller, 7000);
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
                  vm.getReservationsFromJob(jobId);
                  vm.loading = true;
              })
              .catch(function (error) {
                  console.log(error);
              });
            }
        },
    },

  template: `
    <div class="container">
        <br>
        <h2>Find a Ferry Reservation</h2>
        <br>
        <b-form id="app" @submit="checkForm" method="post">
          <b-form-group
            id="input-group-1"
            label="Departure Date:"
            label-for="input-1"
          >
            <b-form-input
              id="input-1"
              v-model="form.departing_date"
              type="date"
              required
              placeholder="enter Departure date"
            ></b-form-input>
          </b-form-group>
          <b-form-group
            id="input-group-2"
            label="Return Date:"
            label-for="input-2"
          >
            <b-form-input
              id="input-2"
              v-model="form.return_date"
              type="date"
              required
              placeholder="enter Return date"
            ></b-form-input>
          </b-form-group>
          <b-form-group
            id="input-group-3"
            label="Departure Terminal:"
            label-for="input-3"
          >
            <b-form-input
              id="input-3"
              v-model="form.depart_term"
              type="text"
              required
              placeholder="enter Departure Terminal"
            ></b-form-input>
          </b-form-group>
          <b-form-group
            id="input-group-4"
            label="Arrival Terminal:"
            label-for="input-4"
          >
            <b-form-input
              id="input-4"
              v-model="form.arrive_term"
              type="text"
              required
              placeholder="enter Arrival Terminal"
            ></b-form-input>
          </b-form-group>
          <button type="submit" class="btn btn-primary" @click="checkForm" v-if="!loading">Submit</button>
          <b-button variant="primary" disabled v-if="loading">
            <b-spinner small type="grow"></b-spinner>
            Loading...
          </b-button>
        <b-form>
        <br>
        <!--alert-->
         <b-alert
          :show="dismissCountDown"
          dismissible
          variant="info"
          @dismissed="dismissCountDown=0"
          @dismiss-count-down="countDownChanged"
        >
          <p>{{ progressMessage }}...</p>
          <b-progress
            variant="info"
            :max="dismissSecs"
            :value="dismissCountDown"
            height="4px"
          ></b-progress>
        </b-alert>
        
        <br>
        <div v-if="results.length > 0">
        <h3>Available Ferry Reservations</h3>
        <br>
            <b-table hover :items="results" :fields="fields"></b-table>
        </div>
    </div>
  `,
};