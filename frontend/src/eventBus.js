import { reactive } from 'vue'

export const eventBus = reactive({
  eventSources: {},
  baseURL: 'http://localhost:8000',
  
  setupSSEConnection(jobId) {
    if (this.eventSources[jobId]) {
      this.eventSources[jobId].close()
    }
    
    const eventSource = new EventSource(`${this.baseURL}/job-events/${jobId}`)
    this.eventSources[jobId] = eventSource
    
    return eventSource
  },
  
  closeAllConnections() {
    Object.values(this.eventSources).forEach(source => source.close())
    this.eventSources = {}
  },
  
  setBaseURL(url) {
    this.baseURL = url
  }
})