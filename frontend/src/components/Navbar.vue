<template>
  <nav class="navbar">
    <div class="navbar-left">
      <div class="site-name">Summarizer</div>
      <router-link to="/projects" class="nav-link">Projects</router-link>
      <router-link to="/channels" class="nav-link">Channels</router-link>
      <router-link to="/summaries" class="nav-link">Summaries</router-link>
    </div>
    <!-- FOR FUTURE LOGOUT ETC.. -->
    <!-- <div class="navbar-right">
      <div class="user-menu" @click="toggleDropdown">
        <div class="user-icon">
          <i class="fas fa-user"></i>
        </div>
        <div class="dropdown" v-if="showDropdown">
          <div class="dropdown-item" @click="logout">Logout</div>
        </div>
      </div>
    </div> -->
  </nav>
</template>

<script>
export default {
  name: 'Navbar',
  data() {
    return {
      showDropdown: false
    };
  },
  methods: {
    toggleDropdown() {
      this.showDropdown = !this.showDropdown;
    },
    logout() {
      console.log('Logging out...');
      this.showDropdown = false;
    }
  }
};
</script>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: #FFFFFF;
  border-bottom: 1px solid #e0e0e0;
}

.navbar-left {
  display: flex;
  align-items: center;
}

.site-name {
  font-size: 1.5rem;
  font-weight: bold;
  color: #2686BB;
  text-decoration: none;
  margin-right: 2rem;
}

.nav-link {
  margin-right: 1.5rem;
  color: #182825;
  text-decoration: none;
  font-size: 1.1rem;
}

.nav-link:hover {
  color: #2686BB;
}

.user-menu {
  position: relative;
  cursor: pointer;
}

.user-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #2686BB;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.dropdown {
  position: absolute;
  right: 0;
  top: 45px;
  width: 120px;
  background-color: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.dropdown-item {
  padding: 10px 15px;
  color: #182825;
}

.dropdown-item:hover {
  background-color: #f5f5f5;
}
</style>