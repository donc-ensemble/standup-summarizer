<template>
  <div class="project-detail">
    <div class="project-top">
      <div class="project-header">
        <button class="back-btn" @click="goBack">← Back to Projects</button>
        <h1>{{ project.name }}</h1>
        <p class="project-description">{{ project.description }}</p>
        <p class="project-created">Created at: {{ formatDate(project.created_at) }}</p>
      </div>
      
      <div class="project-actions">
        <button class="create-btn" @click="showCreateChannelModal = true">Create Channel</button>
        <button class="create-btn" @click="showSummarizeModal = true">Summarize Recording</button>
      </div>
    </div>
    <div class="channels-list">
      <ChannelCard 
        v-for="channel in project.channels" 
        :key="channel.id" 
        :channel="channel"
        @delete="deleteChannel"
      />
      <div v-if="project.channels.length === 0" class="no-channels">
        No channels yet. Create your first channel!
      </div>
    </div>
    
    <CreateChannelModal 
      :show="showCreateChannelModal" 
      :projectId="project.id"
      @close="showCreateChannelModal = false"
      @created="fetchProject"  
    />
    
    <SummarizeModal 
      :show="showSummarizeModal" 
      :channels="project.channels"
      @close="showSummarizeModal = false"
      @submit="handleFileUpload"
    />
  </div>
</template>

<script>
import ChannelCard from '@/components/ChannelCard.vue';
import CreateChannelModal from '@/components/CreateChannelModal.vue';
import SummarizeModal from '@/components/SummarizeModal.vue';
import api from '@/services/api';
import { useJobToast } from '@/composables/useToast'

export default {
  name: 'ProjectDetailView',
  components: {
    ChannelCard,
    CreateChannelModal,
    SummarizeModal
  },
  setup(){
    const { monitorJob } = useJobToast()
    return { monitorJob }
  },
  data() {
    return {
      showCreateChannelModal: false,
      showSummarizeModal: false,
      project: {
        id: null,
        name: '',
        description: '',
        created_at: '',
        channels: []
      },
    };
  },
  async created() {
    await this.fetchProject();
  },
  methods: {
    goBack() {
      this.$router.push(`/projects`);
    },
    async fetchProject() {
      try {
        const response = await api.getProject(this.$route.params.id)
        
        this.project = {
          ...response.data,
          channels: [...response.data.channels].sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        }
      } catch (error) {
        console.error('Error fetching project:', error);
        
      }
    },
    async handleFileUpload(data) {
      try {
        console.log('Received data:', data);
        
        if (!data || !data.channelId || !data.formData) {
          console.error('Invalid data received:', data);
          return;
        }
        
        console.log('Uploading with channel ID:', data.channelId);
        const response = await api.uploadAudio(data.formData, data.channelId);
        
        const res = this.monitorJob(response.data.job_id)
      } catch (error) {
        console.error('Upload failed:', error);
      }
    },
    async deleteChannel(channelId) {
      await api.deleteChannel(channelId)
      this.project.channels = this.project.channels.filter(channel => channel.id !== channelId);
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      });
    },
  }
};
</script>

<style scoped>

.back-btn {
  background: none;
  border: none;
  color: #2686BB;
  cursor: pointer;
  padding: 0.5rem 0;
  margin-bottom: 1rem;
  font-size: 1rem;
}

.back-btn:hover {
  text-decoration: underline;
}


.project-detail {
  /* max-width: 1200px; */
  /* margin: 0 auto; */
  padding: 2rem;
}
.project-top {
  display: flex;
  justify-content: space-between;
}
.project-header {
  margin-bottom: 2rem;
}

.project-header h1 {
  color: #182825;
  margin: 0 0 0.5rem 0;
}

.project-description {
  color: #555;
  margin-bottom: 0.5rem;
}

.project-created {
  color: #777;
  font-size: 0.9rem;
}

.project-actions {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  align-self: flex-start;
}

.create-btn {
  background-color: #2686BB;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
}

.create-btn:hover {
  background-color: #1d6e99;
}

.no-channels {
  text-align: center;
  padding: 3rem 0;
  color: #777;
  background-color: #f9f9f9;
  border-radius: 8px;
  border: 1px dashed #ddd;
}

.channels-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}
</style>