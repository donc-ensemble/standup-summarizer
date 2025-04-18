import { useToast } from 'vue-toastification'
import { eventBus } from '../eventBus'

export function useJobToast() {
  const toast = useToast()
  
  const monitorJob = (jobId, statusCallback = null) => {
    const eventSource = eventBus.setupSSEConnection(jobId)
    let toastId = null
    let processingToastShown = false
    let processingToastDismissed = false
    
    const createToast = (content, options = {}) => {
      const finalOptions = {
        timeout: 5000,
        ...options,
        onClose: () => {
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
          return toastId
        } catch (e) {
          console.debug(`[useJobToast] Failed to update toast ${toastId}, it was dismissed`, e)
          toastId = null
        }
      }
      
      if (!toastId && !(content.includes('Status: processing') && processingToastDismissed)) { 
        toastId = createToast(content, finalOptions)
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
      if (!event.data) {
        console.debug('[useJobToast] Empty event data received')
        return
      }
      
      const data = safeParse(event.data)
      console.debug('[useJobToast] Parsed event data:', data)
      
      if (data.status === 'processing') {
        if (statusCallback) statusCallback('processing', data);
        
        if (!processingToastShown && !processingToastDismissed) {
          updateOrCreateToast(`Status: ${data.status}`, {
            type: 'info',
            timeout: 5000 
          })
          processingToastShown = true;
        }
      } else if (data.status === 'completed') {
        console.debug(`[useJobToast] Job ${jobId} completed successfully`);
        if (statusCallback) statusCallback('completed', data);
        
        let toastMessage = 'Processing completed successfully!';
        let toastType = 'success';
        
        if (data.slack_notification_sent === false) {
          toastMessage = data.slack_error 
            ? `${data.slack_error}`
            : 'Processing completed and did not send to Slack';

          toastType = data.slack_error ? 'warning' : 'success';
        }

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