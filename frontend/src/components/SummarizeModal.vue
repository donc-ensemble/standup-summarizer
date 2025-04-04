<template>
  <div v-if="show" class="modal-overlay">
    <div class="modal-content">
      <h2>Summarize Recording</h2>
      <form @submit.prevent="submitSummary">
        <div class="form-group">
          <label for="channel">Channel *</label>
          <select 
            id="channel" 
            v-model="selectedChannelId" 
            required
          >
            <option value="" disabled>Select a channel</option>
            <option 
              v-for="channel in channels" 
              :key="channel.id" 
              :value="channel.id"
            >
              {{ channel.label }} ({{ channel.channelId }})
            </option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="audioFile">Audio File *</label>
          <input 
            type="file" 
            id="audioFile" 
            ref="audioFile" 
            accept="audio/*" 
            required
            @change="handleFileChange"
          >
        </div>
        
        <div class="form-actions">
          <button type="button" class="cancel-btn" @click="cancel">Cancel</button>
          <button 
            type="submit" 
            class="submit-btn" 
            :disabled="!isFormValid"
          >
            Summarize
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
      default: () => []
    }
  },
  data() {
    return {
      selectedChannelId: '',
      audioFile: null
    };
  },
  computed: {
    isFormValid() {
      return this.selectedChannelId && this.audioFile;
    }
  },
  methods: {
    handleFileChange(event) {
      this.audioFile = event.target.files[0];
    },
    submitSummary() {
      if (!this.isFormValid) return;
      
      this.$emit('submit', {
        channelId: this.selectedChannelId,
        audioFile: this.audioFile
      });
      this.resetForm();
    },
    cancel() {
      this.resetForm();
      this.$emit('close');
    },
    resetForm() {
      this.selectedChannelId = '';
      this.audioFile = null;
      if (this.$refs.audioFile) {
        this.$refs.audioFile.value = '';
      }
    }
  }
};
</script>

<style scoped>
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
}

.modal-content {
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
}

h2 {
  color: #182825;
  margin-top: 0;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: #333;
  font-weight: 500;
}

select, input[type="file"] {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.cancel-btn {
  background-color: #e0e0e0;
  color: #333;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.submit-btn {
  background-color: #2686BB;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.submit-btn:disabled {
  background-color: #93c5e4;
  cursor: not-allowed;
}
</style>