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
        <!-- TODO: 
          - Update this so that we can summarize from project detail view
          - Bug: when uploading from here, the channel detail view summary must display generating summary and auto updates once complete
          - Possible solution: Check the event bus and create an event emitter
        -->
        <!-- <button class="create-btn summarize" @click="showSummarizeModal = true">Summarize</button> -->
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
import { useJobToast } from '@/composables/useToast';
import { eventBus } from '@/eventBus';

export default {
  name: 'ProjectDetailView',
  components: {
    ChannelCard,
    CreateChannelModal,
    SummarizeModal
  },
  setup() {
    const { monitorJob } = useJobToast();
    return { monitorJob };
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
      processingJobs: []
    };
  },
  async created() {
    await this.fetchProject();
    // eventBus.$on('summary-completed', this.handleSummaryCompleted);
  },
  beforeDestroy() {
    // eventBus.$off('summary-completed', this.handleSummaryCompleted);
  },
  methods: {
    goBack() {
      this.$router.push('/projects');
    },
    async fetchProject() {
      try {
        const response = await api.getProject(this.$route.params.id);
        
        this.project = {
          ...response.data,
          channels: [...response.data.channels]
            .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
            .map(channel => ({
              ...channel,
              summaries: channel.summaries?.map(summary => ({
                ...summary,
                status: summary.status === 'processing' ? 'completed' : summary.status
              })) || []
            }))
        };

        // Clean up processing jobs for completed summaries
        this.processingJobs = this.processingJobs.filter(job => {
          const channel = this.project.channels.find(c => c.id === job.channelId);
          return !channel?.summaries?.some(s => 
            s.original_filename?.includes(job.filename)
          );
        });
      } catch (error) {
        console.error('Error fetching project:', error);
      }
    },
    async handleFileUpload(data) {
      try {
        if (!data?.channelId || !data?.formData) {
          console.error('Invalid upload data:', data);
          return;
        }

        const response = await api.uploadAudio(data.formData, data.channelId);
        const filename = data.formData.get('audio_file').name;
        const jobId = response.data.job_id;

        this.processingJobs.push({
          id: jobId,
          filename,
          channelId: data.channelId
        });

        const cleanup = this.monitorJob(jobId, (status, eventData) => {
          if (status === 'completed') {
            this.processingJobs = this.processingJobs.filter(job => job.id !== jobId);
            // eventBus.$emit('summary-completed', {
            //   channelId: data.channelId,
            //   summaryId: eventData.summary_id
            // });
            this.fetchProject();
          } else if (status === 'failed') {
            this.processingJobs = this.processingJobs.filter(job => job.id !== jobId);
          }
        });

        this.$once('hook:beforeDestroy', cleanup);
      } catch (error) {
        console.error('Upload failed:', error);
      }
    },
    handleSummaryCompleted({ channelId }) {
      // eventBus.$emit('refresh-channel', channelId);
    },
    async deleteChannel(channelId) {
      try {
        await api.deleteChannel(channelId);
        this.project.channels = this.project.channels.filter(
          channel => channel.id !== channelId
        );
      } catch (error) {
        console.error('Error deleting channel:', error);
      }
    },
    formatDate(dateString) {
      if (!dateString) return 'Unknown date';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      });
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

.create-btn.summarize {
  background-color: #ff4d4e;
}

.create-btn:hover {
  background-color: #1d6e99;
}

.create-btn.summarize:hover {
  background-color: #e64647;
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