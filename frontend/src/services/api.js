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
  getProject(projectId){
    return api.get(`/projects/${projectId}`)
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
  getChannel(channelId) {
    return api.get(`/channels/${channelId}`)
  },
  createChannel(channelData) {
    return api.post('/channels', channelData)
  },
  deleteChannel(channelId) {
    return api.delete(`/channels/${channelId}`)
  },
  
  // Summaries
  createSummary(summaryData) {
    return api.post('/summaries', summaryData);
  },

  // In your api.js
  uploadAudio(formData, channelId) {
    console.log('API uploading with channel ID:', channelId); // Add this log
    return api.post(`/upload-audio/?channel_id=${channelId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },

  getJobStatus(jobId) {
    return api.get(`/job-status/${jobId}`);
  }

  
};