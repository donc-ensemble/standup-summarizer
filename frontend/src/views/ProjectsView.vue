<template>
  <div class="projects-page">
    <div class="projects-header">
      <h1>Projects</h1>
      <button class="create-btn" @click="showCreateModal = true">Create Project</button>
    </div>
    
    <div class="projects-list">
      <ProjectCard 
        v-for="project in projects" 
        :key="project.id" 
        :project="project"
        @delete="handleDeleteProject"
      />
      <div v-if="projects.length === 0" class="no-projects">
        No projects yet. Create your first project!
      </div>
    </div>
    
    <CreateProjectModal 
      :show="showCreateModal" 
      @close="showCreateModal = false"
      @create="handleCreateProject"
    />
  </div>
</template>

<script>
import ProjectCard from '@/components/ProjectCard.vue';
import CreateProjectModal from '@/components/CreateProjectModal.vue';
import api from '@/services/api';

export default {
  name: 'ProjectsView',
  components: {
    ProjectCard,
    CreateProjectModal
  },
  data() {
    return {
      showCreateModal: false,
      projects: []
    };
  },
  async created() {
    await this.fetchProjects();
  },
  methods: {
    async fetchProjects() {
      try {
        const response = await api.getProjects();
        this.projects = response.data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      } catch (error) {
        console.error('Error fetching projects:', error);
      }
    },
    async handleCreateProject(projectData) {
      try {
        const response = await api.createProject(projectData);
        this.projects.unshift(response.data);
        this.showCreateModal = false;
      } catch (error) {
        console.error('Error creating project:', error);
      }
    },
    async handleDeleteProject(projectId) {
      try {
        console.log("🚀 ~ handleDeleteProject ~ projectId:", projectId)
        
        await api.deleteProject(projectId);
        this.projects = this.projects.filter(project => project.id !== projectId);
      } catch (error) {
        console.error('Error deleting project:', error);
      }
    }
  }
};
</script>


<style scoped>
.projects-page {
  /* max-width: 1200px; */
  /* margin: 0 auto; */
  padding: 2rem;
}

.projects-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.projects-list {
  display: flex;
  gap: 1rem;
}

h1 {
  color: #182825;
  margin: 0;
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

.create-btn:hover {
  background-color: #1d6e99;
}

.no-projects {
  text-align: center;
  padding: 3rem;
  color: #777;
  background-color: #f9f9f9;
  border-radius: 8px;
  border: 1px dashed #ddd;
}
</style>