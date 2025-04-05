import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  }
});


export default {
  // Projects
  getProjects() {
    return api.get('/projects');
  },
  createProject(projectData) {
    return api.post('/projects', projectData);
  },
  deleteProject(projectId) {
    return api.delete(`/projects/${projectId}`)
  },

  // Channels
  getChannels(projectId) {
    return api.get(`/projects/${projectId}/channels`);
  },
  
  // Summaries
  createSummary(summaryData) {
    return api.post('/summaries', summaryData);
  }
};