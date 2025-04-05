<template>
  <div class="channel-card" @click="navigateToChannel">
    <div class="channel-content">
      <h3 class="channel-label">{{ channel.label }}</h3>
      <p class="channel-id">ID: {{ channel.channelId }}</p>
      <p class="channel-created">Created at: {{ formatDate(channel.created_at) }}</p>
    </div>
    <div class="channel-actions">
      <button class="action-btn" @click.stop="showDeleteConfirm = true">...</button>
    </div>
    
    <!-- Delete confirmation modal -->
    <div v-if="showDeleteConfirm" class="delete-modal" @click.stop>
      <div class="delete-modal-content">
        <p>Are you sure you want to delete this channel?</p>
        <div class="delete-modal-actions">
          <button @click="deleteChannel" class="delete-btn">Delete</button>
          <button @click="showDeleteConfirm = false" class="cancel-btn">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ChannelCard',
  props: {
    channel: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      showDeleteConfirm: false
    };
  },
  methods: {
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      });
    },
    deleteChannel() {
      this.$emit('delete', this.channel.id);
      this.showDeleteConfirm = false;
    },
    navigateToChannel() {
      this.$router.push(`/channels/${this.channel.id}`);
    }
  }
};
</script>

<style scoped>
.channel-card {
  position: relative;
  background-color: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  cursor: pointer;
}

.channel-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.channel-content {
  flex-grow: 1;
}

.channel-label {
  color: #182825;
  margin-top: 0;
  margin-bottom: 0.5rem;
  font-size: 1.2rem;
}

.channel-id {
  color: #555;
  margin-bottom: 1rem;
  font-family: monospace;
}

.channel-created {
  color: #777;
  font-size: 0.9rem;
  margin-bottom: 0;
}

.channel-actions {
  position: absolute;
  top: 1rem;
  right: 1rem;
}

.action-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #777;
  cursor: pointer;
  padding: 0 0.5rem;
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
}

.cancel-btn {
  background-color: #e0e0e0;
  color: #333;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}
</style>