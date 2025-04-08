import { useToast } from 'vue-toastification'
import { eventBus } from '../eventBus'

export function useJobToast() {
  const toast = useToast()
  
  const monitorJob = (jobId, statusCallback = null) => {
    console.debug(`[useJobToast] Setting up monitoring for job ${jobId}`)
    const eventSource = eventBus.setupSSEConnection(jobId)
    let toastId = null
    let processingToastShown = false
    let processingToastDismissed = false
    
    const createToast = (content, options = {}) => {
      console.debug(`[useJobToast] Creating new toast for job ${jobId}`, { content, options })
      // Set default timeout to 5 seconds for all toasts
      const finalOptions = {
        timeout: 5000,
        ...options,
        onClose: () => {
          console.debug(`[useJobToast] Toast for job ${jobId} was closed`)
          if (options.type === 'info' || !options.type) {
            processingToastDismissed = true;
          }
          if (options.onClose) options.onClose();
          toastId = null;
        }
      };
      
      return toast.info(content, finalOptions);
    }

    const updateOrCreateToast = (content, options = {}) => {
      console.debug(`[useJobToast] Attempting to update/create toast for job ${jobId}`, {
        content,
        options,
        toastExists: !!toastId
      })

      // Set default timeout to 5 seconds
      const finalOptions = {
        timeout: 5000,
        ...options
      };

      if (toastId) {
        try {
          toast.update(toastId, { 
            content, 
            ...finalOptions 
          })
          console.debug(`[useJobToast] Successfully updated toast ${toastId}`)
          return toastId
        } catch (e) {
          console.debug(`[useJobToast] Failed to update toast ${toastId}, it was dismissed`, e)
          toastId = null
        }
      }
      
      // Only create new toast if it's not a processing toast that was previously dismissed
      if (!toastId && !(content.includes('Status: processing') && processingToastDismissed)) { 
        toastId = createToast(content, finalOptions)
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
      // Reset for new connections, but keep processingToastDismissed status
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
        
        // Only show processing toast if it hasn't been dismissed before
        if (!processingToastShown && !processingToastDismissed) {
          updateOrCreateToast(`Status: ${data.status}`, {
            type: 'info',
            timeout: 5000  // Auto-dismiss after 5 seconds
          })
          processingToastShown = true;
        }
      } else if (data.status === 'completed') {
        console.debug(`[useJobToast] Job ${jobId} completed successfully`);
        if (statusCallback) statusCallback('completed', data);
        
        let toastMessage = 'Processing completed successfully!';
        let toastType = 'success';
        
        // Handle Slack notification failure
        if (data.slack_notification_sent === false) {
          toastMessage = data.slack_error 
            ? `Processing completed but failed to send to Slack: ${data.slack_error}`
            : 'Processing completed but failed to send to Slack';
          toastType = 'warning';
        }

        // Always show completion toast, regardless of previous toast status
        if (toastId) {
          toast.dismiss(toastId);
          toastId = null;
        }
        
        toastId = toast[toastType](toastMessage, {
          timeout: 5000,
          onClose: () => {
            toastId = null;
          }
        });
        
        eventSource.close();
        delete eventBus.eventSources[jobId];
      } else if (data.status === 'failed') {
        console.error(`[useJobToast] Job ${jobId} failed:`, data.error)
        if (statusCallback) statusCallback('failed', data);
        
        const errorMessage = data.error || 'Unknown error';
        const slackError = data.slack_error ? ` (Slack error: ${data.slack_error})` : '';
        
        // Always show error toast
        if (toastId) {
          toast.dismiss(toastId);
          toastId = null;
        }
        
        toastId = toast.error(`Processing failed: ${errorMessage}${slackError}`, {
          timeout: 5000,
          onClose: () => {
            toastId = null;
          }
        });
        
        eventSource.close();
        delete eventBus.eventSources[jobId];
      } else if (data.status) {
        if (statusCallback) statusCallback(data.status, data);
        console.debug(`[useJobToast] Job ${jobId} non-standard status update:`, data.status);
        
        // Only show if it's not a processing toast that was previously dismissed
        if (!processingToastDismissed) {
          updateOrCreateToast(`Status: ${data.status}`, {
            type: 'info',
            timeout: 5000  // Auto-dismiss after 5 seconds
          });
        }
      }
    }
    
    eventSource.onerror = (error) => {
      console.error(`[useJobToast] SSE error for job ${jobId}:`, error)
      if (statusCallback) statusCallback('error', { error });
      
      if (toastId) {
        toast.dismiss(toastId);
        toastId = null;
      }
      
      toastId = toast.error('Connection to updates server lost', {
        timeout: 5000,
        onClose: () => {
          toastId = null;
        }
      });
      
      eventSource.close();
      delete eventBus.eventSources[jobId];
    }

    return () => {
      console.debug(`[useJobToast] Cleaning up monitoring for job ${jobId}`)
      if (eventSource) {
        eventSource.close();
      }
      if (toastId) {
        try {
          toast.dismiss(toastId);
          toastId = null;
        } catch (e) {
          console.debug('[useJobToast] Error dismissing toast during cleanup:', e);
        }
      }
      delete eventBus.eventSources[jobId];
    }
  }
  
  return {
    monitorJob
  }
}