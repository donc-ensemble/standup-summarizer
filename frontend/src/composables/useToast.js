import { useToast } from 'vue-toastification'
import { eventBus } from '../eventBus'

export function useJobToast() {
  const toast = useToast()
  
  const monitorJob = (jobId, statusCallback = null) => {
    console.debug(`[useJobToast] Setting up monitoring for job ${jobId}`)
    const eventSource = eventBus.setupSSEConnection(jobId)
    let toastId = null
    let hasProcessingToast = false
    
    const createToast = (content, options = {}) => {
      console.debug(`[useJobToast] Creating new toast for job ${jobId}`, { content, options })
      return toast.info(content, {
        ...options,
        onClose: () => {
          console.debug(`[useJobToast] Toast for job ${jobId} was closed`)
          toastId = null
          hasProcessingToast = false
        }
      })
    }

    const updateOrCreateToast = (content, options = {}) => {
      console.debug(`[useJobToast] Attempting to update/create toast for job ${jobId}`, {
        content,
        options,
        toastExists: !!toastId
      })

      if (toastId) {
        try {
          toast.update(toastId, { 
            content, 
            ...options 
          })
          console.debug(`[useJobToast] Successfully updated toast ${toastId}`)
          return toastId
        } catch (e) {
          console.debug(`[useJobToast] Failed to update toast ${toastId}, it was dismissed`, e)
          toastId = null
          hasProcessingToast = false
        }
      }
      
      if (!toastId) {
        toastId = createToast(content, options)
        console.debug(`[useJobToast] Created new toast with ID ${toastId}`)
      }
      
      return toastId
    }

    const safeParse = (data) => {
      try {
        return JSON.parse(data)
      } catch (e) {
        console.error('[useJobToast] Failed to parse event data:', data, e)
        return { error: 'Invalid server response' }
      }
    }

    eventSource.addEventListener('open', () => {
      console.debug(`[useJobToast] SSE connection opened for job ${jobId}`)
    })

    eventSource.onmessage = (event) => {
      console.debug(`[useJobToast] Received message for job ${jobId}:`, event.data)
      if (!event.data) {
        console.debug('[useJobToast] Empty event data received')
        return
      }
      
      const data = safeParse(event.data)
      console.debug('[useJobToast] Parsed event data:', data)
      
      if (data.status === 'processing') {
        if (statusCallback) statusCallback('processing', data);
        if (!hasProcessingToast) {
          updateOrCreateToast(`Status: ${data.status}`, {
            timeout: false,
            closeOnClick: false
          })
          hasProcessingToast = true
        }
      }  else if (data.status === 'completed') {
        console.debug(`[useJobToast] Job ${jobId} completed successfully`);
        if (statusCallback) statusCallback('completed', data);
        
        if (toastId && hasProcessingToast) {
          // Clear the existing toast first to ensure proper styling
          toast.dismiss(toastId);
          // Create new success toast
          toastId = toast.success('Processing completed successfully!', {
            timeout: 5000,
            onClose: () => {
              toastId = null;
              hasProcessingToast = false;
            }
          });
        } else {
          toastId = toast.success('Processing completed successfully!', {
            timeout: 5000,
            onClose: () => {
              toastId = null;
              hasProcessingToast = false;
            }
          });
        }
        eventSource.close();
        delete eventBus.eventSources[jobId];
      } else if (data.status === 'failed') {
        console.error(`[useJobToast] Job ${jobId} failed:`, data.error)
        if (statusCallback) statusCallback('failed', data);
        
        if (toastId && hasProcessingToast) {
          updateOrCreateToast(`Processing failed: ${data.error || 'Unknown error'}`, {
            type: 'error',
            timeout: 5000
          })
        } else {
          toastId = toast.error(`Processing failed: ${data.error || 'Unknown error'}`, {
            timeout: 5000,
            onClose: () => {
              toastId = null
              hasProcessingToast = false
            }
          })
        }
        
        eventSource.close()
        delete eventBus.eventSources[jobId]
      } else if (data.status) {
        if (statusCallback) statusCallback(data.status, data);
        console.debug(`[useJobToast] Job ${jobId} non-standard status update:`, data.status)
        updateOrCreateToast(`Status: ${data.status}`, {
          timeout: false,
          closeOnClick: false
        })
      }
    }
    
    eventSource.onerror = (error) => {
      console.error(`[useJobToast] SSE error for job ${jobId}:`, error)
      if (statusCallback) statusCallback('error', { error });
      
      if (toastId) {
        updateOrCreateToast('Connection to updates server lost', {
          type: 'error',
          timeout: 5000
        })
      } else {
        toastId = toast.error('Connection to updates server lost', {
          timeout: 5000,
          onClose: () => {
            toastId = null
            hasProcessingToast = false
          }
        })
      }
      
      eventSource.close()
      delete eventBus.eventSources[jobId]
    }

    return () => {
      console.debug(`[useJobToast] Cleaning up monitoring for job ${jobId}`)
      if (eventSource) {
        eventSource.close()
      }
      if (toastId) {
        try {
          toast.dismiss(toastId)
          toastId = null
          hasProcessingToast = false
        } catch (e) {
          console.debug('[useJobToast] Error dismissing toast during cleanup:', e)
        }
      }
      delete eventBus.eventSources[jobId]
    }
  }
  
  return {
    monitorJob
  }
}