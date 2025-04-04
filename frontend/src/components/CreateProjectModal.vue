<template>
  <div v-if="show" class="modal-overlay">
    <div class="modal-content">
      <h2>Create Project</h2>
      <form @submit.prevent="submitProject">
        <div class="form-group">
          <label for="projectName">Project Name *</label>
          <input 
            type="text" 
            id="projectName" 
            v-model="projectName" 
            required 
            placeholder="Enter project name"
          >
        </div>
        <div class="form-group">
          <label for="projectDescription">Description (optional)</label>
          <textarea 
            id="projectDescription" 
            v-model="projectDescription" 
            placeholder="Enter project description"
          ></textarea>
        </div>
        <div class="form-actions">
          <button type="button" class="cancel-btn" @click="cancel">Cancel</button>
          <button type="submit" class="submit-btn" :disabled="!projectName">Create</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CreateProjectModal',
  props: {
    show: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      projectName: '',
      projectDescription: ''
    };
  },
  methods: {
    submitProject() {
      if (!this.projectName) return;
      
      const newProject = {
        name: this.projectName,
        description: this.projectDescription,
        createdAt: new Date().toISOString()
      };
      
      this.$emit('create', newProject);
      this.resetForm();
    },
    cancel() {
      this.resetForm();
      this.$emit('close');
    },
    resetForm() {
      this.projectName = '';
      this.projectDescription = '';
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

input, textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

textarea {
  min-height: 100px;
  resize: vertical;
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
