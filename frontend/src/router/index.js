import { createRouter, createWebHistory } from 'vue-router';
import ProjectsView from '@/views/ProjectsView.vue';
// import ChannelsView from '@/views/ChannelsView.vue';
// import SummariesView from '@/views/SummariesView.vue';
// import HomeView from '@/views/HomeView.vue';

const routes = [
  // {
  //   path: '/',
  //   name: 'Home',
  //   component: HomeView
  // },
  {
    path: '/projects',
    name: 'Projects',
    component: ProjectsView
  },
  // {
  //   path: '/channels',
  //   name: 'Channels',
  //   component: ChannelsView
  // },
  // {
  //   path: '/summaries',
  //   name: 'Summaries',
  //   component: SummariesView
  // }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
});

export default router;