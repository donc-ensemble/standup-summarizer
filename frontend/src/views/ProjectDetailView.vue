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
        v-for="channel in channels" 
        :key="channel.id" 
        :channel="channel"
        @delete="deleteChannel"
      />
      <div v-if="channels.length === 0" class="no-channels">
        No channels yet. Create your first channel!
      </div>
    </div>
    
    <CreateChannelModal 
      :show="showCreateChannelModal" 
      @close="showCreateChannelModal = false"
      @create="createChannels"
    />
    
    <SummarizeModal 
      :show="showSummarizeModal" 
      :channels="channels"
      @close="showSummarizeModal = false"
      @submit="createSummary"
    />
  </div>
</template>

<script>
import ChannelCard from '@/components/ChannelCard.vue';
import CreateChannelModal from '@/components/CreateChannelModal.vue';
import SummarizeModal from '@/components/SummarizeModal.vue';

export default {
  name: 'ProjectDetailView',
  components: {
    ChannelCard,
    CreateChannelModal,
    SummarizeModal
  },
  data() {
    return {
      showCreateChannelModal: false,
      showSummarizeModal: false,
      project: {
        id: this.$route.params.id,
        name: '',
        description: '',
        created_at: ''
      },
      channels: [
        // Sample data, would be replaced with API calls
        {
          id: '1',
          projectId: this.$route.params.id,
          label: 'General',
          channelId: 'general',
          created_at: '2025-03-10T09:00:00Z'
        },
        {
          id: '2',
          projectId: this.$route.params.id,
          label: 'Development',
          channelId: 'dev',
          created_at: '2025-03-15T14:30:00Z'
        }
      ],
      summaries: []
    };
  },
  created() {
    // In a real app, fetch project details from API
    this.fetchProject();
  },
  methods: {
    goBack() {
      // Navigate back to the project detail page
      this.$router.push(`/projects`);
    },
    fetchProject() {
      // Simulate API call
      // This would be replaced with actual API call
      const projects = [
        {
          id: '1',
          name: 'Team Alpha Standups',
          description: 'Daily standup recordings for the Alpha team',
          created_at: '2025-03-10T09:00:00Z'
        },
        {
          id: '2',
          name: 'Project Beta Planning',
          description: 'Planning sessions for the Beta project launch',
          created_at: '2025-03-15T14:30:00Z'
        }
      ];
      
      const foundProject = projects.find(p => p.id === this.$route.params.id);
      if (foundProject) {
        this.project = foundProject;
      }
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      });
    },
    createChannels(channels) {
      // In a real application, make an API call here
      channels.forEach(channel => {
        const newChannel = {
          ...channel,
          id: Date.now().toString(), // Temporary ID generation
          projectId: this.project.id,
          created_at: new Date().toISOString()
        };
        this.channels.unshift(newChannel);
      });
      this.showCreateChannelModal = false;
    },
    deleteChannel(channelId) {
      // In a real application, make an API call here
      this.channels = this.channels.filter(channel => channel.id !== channelId);
    },
    createSummary({ channelId, audioFile }) {
      // In a real application, make an API call here
      const channel = this.channels.find(c => c.id === channelId);
      if (!channel) return;
      
      // Simulate summary creation
      const newSummary = {
        id: Date.now().toString(),
        channelId: channelId,
        channelLabel: channel.label,
        audioFileName: audioFile.name,
        summary: "This is a sample summary of the audio recording. In a real application, this would be generated by the backend service.",
        created_at: new Date().toISOString()
      };
      
      this.summaries.unshift(newSummary);
      this.showSummarizeModal = false;
    }
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