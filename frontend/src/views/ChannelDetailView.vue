<template>
  <div class="channel-detail">
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <template v-else>
      <div class="channel-header">
        <div class="channel-top">
          <button class="back-btn" @click="goBack">← Back to Project</button>
          <div class="channel-actions">
            <button class="create-btn summarize" @click="showSummarizeModal = true">Summarize</button>
          </div>
        </div>
        <div class="channel-meta">
          <div class="channel-title-row">
            <h1>{{ channel.label }}</h1>
            <button class="action-btn" @click.stop="showChannelDeleteModal = true">
              <font-awesome-icon icon="ellipsis-vertical" />
            </button>
          </div>
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
                {{ getAudioFileName(summary.original_filename) }}
              </h3>
              <div class="summary-actions">
                <span class="summary-date">{{ formatDate(summary.created_at) }}</span>
                <button class="action-btn" @click.stop="openSummaryDeleteModal(summary.id)">
                  ...
                </button>
              </div>
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

    <!-- Summary Delete Modal -->
    <div v-if="showSummaryDeleteModal" class="delete-modal" @click.stop>
      <div class="delete-modal-content">
        <p>Are you sure you want to delete this summary?</p>
        <div class="delete-modal-actions">
          <button @click="confirmDeleteSummary" class="delete-btn">Delete</button>
          <button @click="showSummaryDeleteModal = false" class="cancel-btn">Cancel</button>
        </div>
      </div>
    </div>
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
      error: null,
      showChannelDeleteModal: false,
      showSummaryDeleteModal: false,
      deletingSummaryId: null,
      summaryToDelete: null
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
    openSummaryDeleteModal(summaryId) {
      this.summaryToDelete = summaryId;
      this.showSummaryDeleteModal = true;
    },
    async confirmDeleteSummary() {
      if (this.summaryToDelete) {
        await this.deleteSummary(this.summaryToDelete);
        this.showSummaryDeleteModal = false;
        this.summaryToDelete = null;
      }
    },
    async deleteSummary(summaryId) {
      this.deletingSummaryId = summaryId;
      try {
        await api.deleteSummary(summaryId);
        this.channel.summaries = this.channel.summaries.filter(
          summary => summary.id !== summaryId
        );
      } catch (error) {
        console.error('Error deleting summary:', error);
        alert('Failed to delete summary');
      } finally {
        this.deletingSummaryId = null;
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

.channel-top {
  display: flex;
  justify-content: space-between;
}

.create-btn.summarize {
  background-color: #ff4d4e;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
}
.create-btn.summarize:hover {
  background-color: #e64647;
}

.channel-title-row {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.action-btn {
  background: none;
  border: none;
  color: #777;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  font-size: 1rem;
}

.action-btn:hover {
  color: #2686BB;
}

.delete-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.delete-modal-content {
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
  text-align: center;
  max-width: 400px;
  width: 90%;
}

.delete-modal-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 1.5rem;
}

.delete-btn {
  background-color: #ff4d4d;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  min-width: 80px;
}

.cancel-btn {
  background-color: #e0e0e0;
  color: #333;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  min-width: 80px;
}

/* Update existing styles */
.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

/* Keep all your existing styles below */
.loading, .error {
  padding: 2rem;
  text-align: center;
  font-size: 1.2rem;
}

.error {
  color: #ff4d4f;
}

.channel-detail {
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
}

.summary-title {
  margin: 0;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
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