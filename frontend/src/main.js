import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import './assets/main.css';

// Add FontAwesome for the user icon
import { library } from '@fortawesome/fontawesome-svg-core';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faTrash } from '@fortawesome/free-solid-svg-icons'


import Toast from 'vue-toastification'
import 'vue-toastification/dist/index.css'

library.add(faTrash)

const app = createApp(App);
app.component('font-awesome-icon', FontAwesomeIcon);
app.use(Toast, {
  position: 'top-right',
  timeout: 5000,
  closeOnClick: true,
  pauseOnFocusLoss: true,
  pauseOnHover: true,
  draggable: true,
  draggablePercent: 0.6,
  showCloseButtonOnHover: false,
  hideProgressBar: false,
  closeButton: 'button',
  icon: true,
  rtl: false
})

app.use(router);
app.mount('#app');
