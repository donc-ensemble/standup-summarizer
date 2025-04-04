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
        @delete="deleteProject"
      />
      <div v-if="projects.length === 0" class="no-projects">
        No projects yet. Create your first project!
      </div>
    </div>
    
    <CreateProjectModal 
      :show="showCreateModal" 
      @close="showCreateModal = false"
      @create="createProject"
    />
  </div>
</template>

<script>
import ProjectCard from '@/components/ProjectCard.vue';
import CreateProjectModal from '@/components/CreateProjectModal.vue';

export default {
  name: 'ProjectsView',
  components: {
    ProjectCard,
    CreateProjectModal
  },
  data() {
    return {
      showCreateModal: false,
      projects: [
        // Sample data, would be replaced with API calls
        {
          id: '1',
          name: 'Team Alpha Standups',
          description: 'Daily standup recordings for the Alpha team',
          createdAt: '2025-03-10T09:00:00Z'
        },
        {
          id: '2',
          name: 'Project Beta Planning',
          description: 'Planning sessions for the Beta project launch',
          createdAt: '2025-03-15T14:30:00Z'
        }
      ]
    };
  },
  methods: {
    createProject(project) {
      // In a real application, make an API call here
      const newProject = {
        ...project,
        id: Date.now().toString() // Temporary ID generation
      };
      
      this.projects.unshift(newProject);
      this.showCreateModal = false;
    },
    deleteProject(projectId) {
      // In a real application, make an API call here
      this.projects = this.projects.filter(project => project.id !== projectId);
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
  padding: 3rem 0;
  color: #777;
  background-color: #f9f9f9;
  border-radius: 8px;
  border: 1px dashed #ddd;
}
</style>