<template>
  <div v-if="show" class="modal-overlay" @click.self="cancel">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Summarize Recording</h2>
        <button class="close-btn" @click="cancel">&times;</button>
      </div>

      <form @submit.prevent="handleSubmit">
        <div class="form-group" v-if="!hideChannelDropdown">
          <label for="channel">Channel *</label>
          <select
            id="channel"
            v-model="selectedChannelId"
            required
            class="form-control"
            v-if="channels.length > 0"
          >
            <option value="" disabled>Select a channel</option>
            <option
              v-for="channel in channels"
              :key="channel.id"
              :value="channel.id"
            >
              {{ channel.label }} (ID: {{ channel.id }})
            </option>
          </select>
          <p v-else class="no-channels">No channels available</p>
        </div>

        <div class="form-group">
          <label for="audioFile">Audio/Video File *</label>
          <div class="file-upload-container">
            <input
              type="file"
              id="audioFile"
              ref="audioFile"
              accept="audio/*,video/mp4,video/x-m4v"
              required
              @change="handleFileChange"
              class="file-input"
            >
            <label for="audioFile" class="file-upload-label">
              <span v-if="!audioFile">Choose file...</span>
              <span v-else class="file-name">{{ audioFile.name }}</span>
            </label>
          </div>
          <p class="file-hint">Supported formats: WAV, MP4 (Max 50MB)</p>
        </div>

        <div v-if="error" class="alert error-message">
          <span class="alert-icon">⚠️</span>
          {{ error }}
        </div>

        <div class="form-group">
          <label>Send to Slack</label>
          <div class="toggle-switch">
            <input 
              type="checkbox" 
              id="slackToggle"
              v-model="sendToSlack"
              :disabled="isLoading"
              class="toggle-input"
            >
            <label for="slackToggle" class="toggle-label"></label>
            <span class="toggle-text">{{ sendToSlack ? 'Yes' : 'No' }}</span>
          </div>
        </div>

        <div class="form-actions">
          <button type="button" class="btn cancel-btn" @click="cancel">
            Cancel
          </button>
          <button
            type="submit"
            class="btn submit-btn"
            :disabled="!isFormValid || isLoading"
          >
            <span v-if="isLoading" class="loading-spinner"></span>
            {{ isLoading ? 'Processing...' : 'Summarize' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SummarizeModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    channels: {
      type: Array,
      default: () => [],
      validator: value => value.every(ch => ch.id && ch.label)
    },
    hideChannelDropdown: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      selectedChannelId: '',
      audioFile: null,
      isLoading: false,
      error: null,
      hasSubmitted: false,
      sendToSlack: true,
    };
  },
  computed: {
    isFormValid() {
      if (this.hideChannelDropdown) {
        return !!this.audioFile;
      }
      return !!this.selectedChannelId && !!this.audioFile;
    }
  },
  methods: {
    handleFileChange(event) {
      const file = event.target.files[0];
      if (!file) return;

      const validTypes = ['audio/wav', 'video/mp4'];
      
      if (!validTypes.some(type => file.type.includes(type))) {
        this.error = 'Unsupported file type. Please use WAV, MP4';
        this.resetForm();
        return;
      }

      if (file.size > 50 * 1024 * 1024) {
        this.error = 'File too large. Maximum size is 50MB.';
        this.resetForm();
        return;
      }

      this.error = null;
      this.audioFile = file;
    },
    async handleSubmit(event) {
      event?.preventDefault();
      
      if (this.hasSubmitted || !this.isFormValid) return;

      this.isLoading = true;
      this.error = null;
      this.hasSubmitted = true;

      try {
        const formData = new FormData();
        formData.append('audio_file', this.audioFile);
        formData.append('send_to_slack', this.sendToSlack.toString());

        if (!this.hideChannelDropdown) {
          this.$emit('submit', {
            formData: formData,
            channelId: this.selectedChannelId
          });
        } else {
          this.$emit('submit', formData);
        }
        
        this.$emit('close');
      } catch (err) {
        this.error = err.message || 'Failed to upload file. Please try again.';
      } finally {
        this.isLoading = false;
        this.hasSubmitted = false;
      }
    },
    cancel() {
      this.resetForm();
      this.$emit('close');
    },
    resetForm() {
      this.selectedChannelId = '';
      this.audioFile = null;
      this.error = null;
      this.hasSubmitted = false;
      if (this.$refs.audioFile) {
        this.$refs.audioFile.value = '';
      }
    }
  },
  watch: {
    show(newVal) {
      if (!newVal) {
        this.resetForm();
      }
    }
  }
};
</script>

<style scoped>
.toggle-switch {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.toggle-input {
  height: 0;
  width: 0;
  visibility: hidden;
  position: absolute;
}

.toggle-label {
  cursor: pointer;
  width: 50px;
  height: 26px;
  background: #e0e0e0;
  display: block;
  border-radius: 50px;
  position: relative;
  transition: background-color 0.2s;
}

.toggle-label:after {
  content: '';
  position: absolute;
  top: 3px;
  left: 3px;
  width: 20px;
  height: 20px;
  background: #fff;
  border-radius: 20px;
  transition: 0.2s;
}

.toggle-input:checked + .toggle-label {
  background: #2686BB;
}

.toggle-input:checked + .toggle-label:after {
  left: calc(100% - 3px);
  transform: translateX(-100%);
}

.toggle-input:disabled + .toggle-label {
  opacity: 0.6;
  cursor: not-allowed;
}

.toggle-text {
  font-size: 0.95rem;
  color: #333;
}

.modal-overlay {
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
  backdrop-filter: blur(2px);
}

.modal-content {
  background-color: white;
  padding: 2rem;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  position: relative;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

h2 {
  color: #182825;
  margin: 0;
  font-size: 1.5rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
  padding: 0.5rem;
  line-height: 1;
}

.close-btn:hover {
  color: #333;
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: #333;
  font-weight: 500;
  font-size: 0.95rem;
}

.form-control {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-control:focus {
  border-color: #2686BB;
  outline: none;
}

.file-upload-container {
  position: relative;
}

.file-input {
  position: absolute;
  width: 0.1px;
  height: 0.1px;
  opacity: 0;
  overflow: hidden;
  z-index: -1;
}

.file-upload-label {
  display: block;
  padding: 0.75rem;
  border: 1px dashed #ddd;
  border-radius: 6px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.file-upload-label:hover {
  border-color: #2686BB;
  background-color: #f8fafb;
}

.file-name {
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  vertical-align: middle;
}

.file-hint {
  font-size: 0.8rem;
  color: #666;
  margin-top: 0.5rem;
}

.no-channels {
  color: #666;
  font-style: italic;
  padding: 0.5rem 0;
}

.alert {
  padding: 0.75rem 1rem;
  border-radius: 6px;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.error-message {
  background-color: #fff0f0;
  color: #ff4d4f;
  border: 1px solid #ffd6d6;
}

.alert-icon {
  font-size: 1.1rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.cancel-btn {
  background-color: #f0f0f0;
  color: #666;
}

.cancel-btn:hover {
  background-color: #e0e0e0;
}

.submit-btn {
  background-color: #2686BB;
  color: white;
}

.submit-btn:hover:not(:disabled) {
  background-color: #1d6e99;
}

.submit-btn:disabled {
  background-color: #93c5e4;
  cursor: not-allowed;
  opacity: 0.8;
}

.loading-spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 600px) {
  .modal-content {
    padding: 1.5rem;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>