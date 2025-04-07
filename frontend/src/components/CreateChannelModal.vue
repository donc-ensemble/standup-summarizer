<template>
  <div v-if="show" class="modal-overlay">
    <div class="modal-content">
      <h2>Create Channels</h2>
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
      <form @submit.prevent="submitChannels">
        <div class="channels-form">
          <div v-for="(channel, index) in channels" :key="index" class="channel-row">
            <div class="form-group">
              <label :for="'channelId' + index">Channel ID *</label>
              <input 
                type="text" 
                :id="'channelId' + index" 
                v-model="channel.channelId" 
                required 
                placeholder="Enter channel ID"
              >
            </div>
            <div class="form-group">
              <label :for="'label' + index">Label *</label>
              <input 
                type="text" 
                :id="'label' + index" 
                v-model="channel.label" 
                required 
                placeholder="Enter channel label"
              >
            </div>
            <button 
              v-if="index > 0" 
              type="button" 
              class="remove-btn" 
              @click="removeChannel(index)"
            >
              ×
            </button>
          </div>
        </div>
        
        <!-- <button type="button" class="add-btn" @click="addChannel">
          + Add Another Channel
        </button> -->
        
        <div class="form-actions">
          <button type="button" class="cancel-btn" @click="cancel">Cancel</button>
          <button 
            type="submit" 
            class="submit-btn" 
            :disabled="!isFormValid"
          >
            Create Channels
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
      channels: [
        { channelId: '', label: '' },
      ],
      isLoading: false,
      error: null,
    };
  },
  computed: {
    isFormValid() {
      return this.channels.every(channel => 
        channel.channelId.trim() && channel.label.trim()
      );
    }
  },
  methods: {
    addChannel() {
      this.channels.push({ channelId: '', label: '' });
    },
    removeChannel(index) {
      this.channels.splice(index, 1);
    },
    async submitChannels() {
      if (!this.isFormValid) return;
      
      this.isLoading = true;
      this.error = null;
      
      try {
        //TODO: allow for bulk create of channels.
        const channelsToCreate = this.channels.map(channel => ({
          project_id: this.projectId,
          channel_id: channel.channelId,
          label: channel.label
        }));
        
        await Promise.all(
          channelsToCreate.map(channel => api.createChannel(channel))
        );
        
        this.$emit('created');
        this.resetForm();
        this.$emit('close');
      } catch (error) {
        console.error('Error creating channels:', error);
        this.error = error.response?.data?.message || 'Failed to create channels';
      } finally {
        this.isLoading = false;
      }
    },
    cancel() {
      this.resetForm();
      this.$emit('close');
    },
    resetForm() {
      this.channels = [
        { channelId: '', label: '' },
        { channelId: '', label: '' }
      ];
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
  max-width: 600px;
}

h2 {
  color: #182825;
  margin-top: 0;
  margin-bottom: 1.5rem;
}

.channels-form {
  margin-bottom: 1.5rem;
}

.channel-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  align-items: flex-end;
  position: relative;
}

.channel-row > .form-group {
  flex: 1;
}

.remove-btn {
  background: none;
  border: none;
  color: #ff4d4d;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0 0.5rem;
  margin-bottom: 0.5rem;
}

.add-btn {
  background: none;
  border: none;
  color: #2686BB;
  cursor: pointer;
  padding: 0.5rem 1rem;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
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