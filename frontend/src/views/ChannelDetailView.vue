<template>
  <div class="channel-detail">
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <template v-else>
      <div class="channel-header">
        <button class="back-btn" @click="goBack">← Back to Project</button>
        <div class="channel-meta">
          <h1>{{ channel.label }}</h1>
          <div class="meta-row">
            <span class="channel-id">ID: {{ channel.channel_id }}</span>
            <span class="channel-created">Created: {{ formatDate(channel.created_at) }}</span>
          </div>
        </div>
      </div>
      <div class="summaries-container">
        <div class="summaries-list">
          <div v-for="summary in channel.summaries" :key="summary.id" class="summary-card">
            <div class="summary-header">
              <h3 class="summary-title">
                {{ getAudioFileName(summary.audio_file_path) }}
              </h3>
              <span class="summary-date">{{ formatDate(summary.created_at) }}</span>
            </div>
            <div class="summary-content">
              <div class="text-content" :class="{ 'collapsed': summary.collapsed }">
                <template v-if="summary.summary">
                  <p v-for="(paragraph, idx) in splitSummary(summary.summary)" :key="idx">
                    {{ paragraph }}
                  </p>
                </template>
                <p v-else class="no-summary">No summary text available</p>
              </div>
              <button 
                v-if="shouldShowToggle(summary.summary)" 
                @click="summary.collapsed = !summary.collapsed"
                class="toggle-btn"
              >
                {{ summary.collapsed ? 'Show more' : 'Show less' }}
              </button>
            </div>
          </div>
          <div v-if="channel.summaries.length === 0" class="no-summaries">
            <div class="empty-state">
              <img src="@/assets/no-summaries.svg" alt="No summaries" class="empty-icon">
              <p>No summaries yet</p>
              <button class="upload-btn" @click="openUploadModal">
                Upload Audio to Generate Summary
              </button>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import api from '@/services/api';

export default {
  name: 'ChannelDetailView',
  data() {
    return {
      channel: {
        id: null,
        project_id: null,
        label: '',
        channel_id: '',
        created_at: '',
        summaries: []
      },
      loading: false,
      error: null
    };
  },
  async created() {
    await this.fetchChannel();
  },
  methods: {
    goBack() {
      if (this.channel.project_id) {
        this.$router.push(`/projects/${this.channel.project_id}`);
      } else {
        this.$router.push('/projects');
      }
    },
    async fetchChannel() {
      this.loading = true;
      this.error = null;
      try {
        const response = await api.getChannel(this.$route.params.id);
        this.channel = {
          ...response.data,
          summaries: [...response.data.summaries]
            .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
            .map(summary => ({
            ...summary,
            collapsed: this.shouldShowToggle(summary.summary)
          }))
        };
      } catch (error) {
        console.error('Error fetching channel:', error);
        this.error = 'Failed to load channel details';
      } finally {
        this.loading = false;
      }
    },
    formatDate(dateString) {
      if (!dateString) return 'Unknown date';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    getAudioFileName(path) {
      if (!path) return 'Untitled Recording';
      return path.split('/').pop() || 'Recording';
    },
    splitSummary(text) {
      if (!text) return [];
      return text.split('\n').filter(p => p.trim().length > 0);
    },
    shouldShowToggle(text) {
      return text && text.length > 300;
    },
    openUploadModal() {
      console.log('Upload modal would open now');
    }
  }
};
</script>

<style scoped>
.loading, .error {
  padding: 2rem;
  text-align: center;
  font-size: 1.2rem;
}

.error {
  color: #ff4d4f;
}

.channel-detail {
  /* max-width: 900px; */
  /* margin: 0 auto; */
  padding: 2rem 1.5rem;
}

.channel-header {
  margin-bottom: 2rem;
}

.back-btn {
  background: none;
  border: none;
  color: #2686BB;
  cursor: pointer;
  padding: 0.5rem 0;
  margin-bottom: 1rem;
  font-size: 1rem;
  display: flex;
  align-items: center;
}

.back-btn:hover {
  text-decoration: underline;
}

.channel-meta h1 {
  color: #182825;
  margin: 0 0 0.25rem 0;
  font-size: 1.8rem;
}

.meta-row {
  display: flex;
  gap: 1rem;
  color: #666;
  font-size: 0.9rem;
}

.summaries-container {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
}

.summaries-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.summary-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  overflow: hidden;
}

.summary-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-title {
  margin: 0;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.audio-icon {
  font-size: 1.2rem;
}

.summary-date {
  color: #666;
  font-size: 0.85rem;
}

.summary-content {
  padding: 1.5rem;
}

.text-content {
  line-height: 1.6;
  color: #333;
}

.text-content.collapsed {
  max-height: 150px;
  overflow: hidden;
  position: relative;
}

.text-content.collapsed::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 50px;
  background: linear-gradient(to bottom, rgba(255,255,255,0), rgba(255,255,255,1));
}

.toggle-btn {
  background: none;
  border: none;
  color: #2686BB;
  cursor: pointer;
  padding: 0.5rem 0;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.toggle-btn:hover {
  text-decoration: underline;
}

.no-summaries {
  text-align: center;
  padding: 3rem 0;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.empty-icon {
  width: 120px;
  opacity: 0.7;
  margin-bottom: 1rem;
}

.upload-btn {
  background-color: #2686BB;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  margin-top: 1rem;
}

.upload-btn:hover {
  background-color: #1d6e99;
}

@media (max-width: 768px) {
  .channel-detail {
    padding: 1.5rem 1rem;
  }
  
  .summary-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}
</style>