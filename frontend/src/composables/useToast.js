import { useToast } from 'vue-toastification'
import { eventBus } from '../eventBus'

export function useJobToast() {
  const toast = useToast()
  
  const monitorJob = (jobId) => {
    const eventSource = eventBus.setupSSEConnection(jobId)

    eventSource.addEventListener('open', () => {
      console.log(`SSE connection opened for job ${jobId}`)
    })
    
    const toastId = toast.info('Processing started...', {
      timeout: false,
      closeOnClick: false
    })
    
    const safeParse = (data) => {
      try {
        return JSON.parse(data)
      } catch (e) {
        console.error('Failed to parse event data:', data, e)
        return { error: 'Invalid server response' }
      }
    }

    eventSource.onmessage = (event) => {
      if (!event.data) return
      
      const data = safeParse(event.data)
      
      if (data.status === 'completed') {
        toast.update(toastId, {
          content: 'Processing completed successfully!',
          options: {
            type: 'success',
            timeout: 5000
          }
        })
        eventSource.close()
        delete eventBus.eventSources[jobId]
      } else if (data.status === 'failed') {
        toast.update(toastId, {
          content: `Processing failed: ${data.error || 'Unknown error'}`,
          options: {
            type: 'error',
            timeout: 5000
          }
        })
        eventSource.close()
        delete eventBus.eventSources[jobId]
      } else if (data.status) {
        toast.update(toastId, {
          content: `Status: ${data.status}`,
          options: {
            timeout: false
          }
        })
      }
    }
    
    eventSource.onerror = () => {
      toast.update(toastId, {
        content: 'Connection to updates server lost',
        options: {
          type: 'error',
          timeout: 5000
        }
      })
      eventSource.close()
      delete eventBus.eventSources[jobId]
    }
  }
  
  return {
    monitorJob
  }
}