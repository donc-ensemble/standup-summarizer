import { createRouter, createWebHistory } from 'vue-router';
import ProjectsView from '@/views/ProjectsView.vue';
import ProjectDetailView from '@/views/ProjectDetailView.vue';
import ChannelDetailView from '@/views/ChannelDetailView.vue';

const routes = [
  {
    path: '/projects',
    name: 'Projects',
    component: ProjectsView
  },
  {
    path: '/projects/:id',
    name: 'ProjectDetail',
    component: ProjectDetailView,
    props: true
  },
  {
    path: '/channels/:id',
    name: 'ChannelDetail',
    component: ChannelDetailView,
    props: true
  }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
});

export default router;