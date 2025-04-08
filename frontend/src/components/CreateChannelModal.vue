<template>
  <div v-if="show" class="modal-overlay">
    <div class="modal-content">
      <h2>Create Channel</h2>
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
      <form @submit.prevent="submitChannel">
        <div class="channel-form">
          <div class="form-group">
            <label for="channelId">Channel ID *</label>
            <input 
              type="text" 
              id="channelId" 
              v-model="channel.channelId" 
              required 
              placeholder="Enter channel ID"
            >
          </div>
          <div class="form-group">
            <label for="label">Label *</label>
            <input 
              type="text" 
              id="label" 
              v-model="channel.label" 
              required 
              placeholder="Enter channel label"
            >
          </div>
        </div>
        
        <div class="form-actions">
          <button type="button" class="cancel-btn" @click="cancel">Cancel</button>
          <button 
            type="submit" 
            class="submit-btn" 
            :disabled="!isFormValid || isLoading"
          >
            {{ isLoading ? 'Creating...' : 'Create Channel' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'; 

export default {
  name: 'CreateChannelModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    projectId: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      channel: {
        channelId: '',
        label: ''
      },
      isLoading: false,
      error: null,
    };
  },
  computed: {
    isFormValid() {
      return this.channel.channelId.trim() && this.channel.label.trim();
    }
  },
  methods: {
    async submitChannel() {
      if (!this.isFormValid) return;
      
      this.isLoading = true;
      this.error = null;
      
      try {
        const channelToCreate = {
          project_id: this.projectId,
          channel_id: this.channel.channelId,
          label: this.channel.label
        };
        
        await api.createChannel(channelToCreate);
        
        this.$emit('created');
        this.resetForm();
        this.$emit('close');
      } catch (error) {
        console.error('Error creating channel:', error);
        this.error = error.response?.data?.message || 'Failed to create channel';
      } finally {
        this.isLoading = false;
      }
    },
    cancel() {
      this.resetForm();
      this.$emit('close');
    },
    resetForm() {
      this.channel = {
        channelId: '',
        label: ''
      };
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

.error-message {
  color: #ff4d4d;
  margin-bottom: 1rem;
  padding: 0.5rem;
  background-color: #ffeeee;
  border-radius: 4px;
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

.channel-form {
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: #333;
  font-weight: 500;
}

input {
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