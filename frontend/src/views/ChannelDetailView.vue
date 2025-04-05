<template>

  
  <div class="channel-detail">
    <div class="channel-header">
      <button class="back-btn" @click="goBack">← Back to Channel</button>
      <h1>{{ channel.label }}</h1>
      <p class="channel-id">ID: {{ channel.channelId }}</p>
      <p class="channel-created">Created at: {{ formatDate(channel.created_at) }}</p>
    </div>
    
    <div class="summaries-list">
      <div v-for="summary in summaries" :key="summary.id" class="summary-card">
        <h3 class="summary-title">{{ summary.audioFileName }}</h3>
        <p class="summary-date">Created at: {{ formatDate(summary.created_at) }}</p>
        <div class="summary-content">
          <p>{{ summary.summary }}</p>
        </div>
      </div>
      
      <div v-if="summaries.length === 0" class="no-summaries">
        No summaries yet. Upload an audio file to generate your first summary!
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ChannelDetailView',
  data() {
    return {
      channel: {
        id: this.$route.params.id,
        label: '',
        channelId: '',
        created_at: ''
      },
      summaries: []
    };
  },
  created() {
    // In a real app, fetch channel details and summaries from API
    this.fetchChannel();
    this.fetchSummaries();
  },
  methods: {
    goBack() {
      // Navigate back to the project detail page
      this.$router.push(`/projects/${this.channel.projectId}`);
    },
    fetchChannel() {
      // Simulate API call
      // This would be replaced with actual API call
      const channels = [
        {
          id: '1',
          projectId: '1',
          label: 'General',
          channelId: 'general',
          created_at: '2025-03-10T09:00:00Z'
        },
        {
          id: '2',
          projectId: '1',
          label: 'Development',
          channelId: 'dev',
          created_at: '2025-03-15T14:30:00Z'
        }
      ];
      
      const foundChannel = channels.find(c => c.id === this.$route.params.id);
      if (foundChannel) {
        this.channel = foundChannel;
      }
    },
    fetchSummaries() {
      // Simulate API call
      // This would be replaced with actual API call
      this.summaries = [
        {
          id: '1',
          channelId: this.$route.params.id,
          channelLabel: this.channel.label,
          audioFileName: 'standup_20250315.mp3',
          summary: "This is a sample summary of the audio recording. The team discussed the progress on the current sprint, with John completing the login page and Sarah working on the API integration. The main blockers were the authentication service delays.",
          created_at: '2025-03-15T14:30:00Z'
        },
        {
          id: '2',
          channelId: this.$route.params.id,
          channelLabel: this.channel.label,
          audioFileName: 'planning_20250320.mp3',
          summary: "This is another sample summary. The team planned the next sprint, deciding to focus on the user dashboard and notification system. Estimated completion time is 2 weeks with all hands on deck.",
          created_at: '2025-03-20T10:15:00Z'
        }
      ];
    },
    formatDate(dateString) {
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

.channel-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.channel-header {
  margin-bottom: 2rem;
}

.channel-header h1 {
  color: #182825;
  margin: 0 0 0.5rem 0;
}

.channel-id {
  color: #555;
  margin-bottom: 0.5rem;
  font-family: monospace;
}

.channel-created {
  color: #777;
  font-size: 0.9rem;
}

.summaries-list {
  display: grid;
  gap: 1.5rem;
}

.summary-card {
  background-color: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.summary-title {
  color: #182825;
  margin-top: 0;
  margin-bottom: 0.5rem;
}

.summary-date {
  color: #777;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.summary-content {
  color: #333;
  line-height: 1.6;
}

.no-summaries {
  text-align: center;
  padding: 3rem 0;
  color: #777;
  background-color: #f9f9f9;
  border-radius: 8px;
  border: 1px dashed #ddd;
}
</style>
[file content end]