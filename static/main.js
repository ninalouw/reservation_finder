// new Vue({
//     el: '#app',
//     data: {
//         title: 'Hello from Vue',
//         data: function (){
//             return {
//                 quote: ''
//             }
//         }
//     },
//     methods: {
//         getReservations: function () {
//             console.log('hello');
//         },
//     }
// });
import App from './components/App.js';

new Vue({
  render: h => h(App),
}).$mount(`#app`);