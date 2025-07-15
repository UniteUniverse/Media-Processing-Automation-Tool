document.addEventListener("DOMContentLoaded", () => {
  const startBtn = document.getElementById("start-btn");
  const folderInput = document.getElementById("folder-path");
  const uploadForm = document.getElementById("upload-form");
  const resultsTable = document.getElementById("results-table");
  
  let pollInterval;
  let isPolling = false;
  
  // Start polling for status updates
  function startPolling() {
    if (isPolling) return;
    isPolling = true;
    
    pollInterval = setInterval(async () => {
      try {
        const response = await fetch('/api/status');
        const data = await response.json();
        updateResultsTable(data.results, data.processing);
      } catch (error) {
        console.error('Error polling status:', error);
      }
    }, 2000); // Poll every 2 seconds
  }
  
  // Update results table dynamically
  function updateResultsTable(results, processing) {
    const tbody = resultsTable.querySelector('tbody');
    tbody.innerHTML = '';
    
    // Add completed results
    results.forEach((item, index) => {
      const row = createResultRow(index, item, null);
      tbody.appendChild(row);
    });
    
    // Add processing jobs
    Object.entries(processing).forEach(([jobId, status]) => {
      const row = createResultRow('...', { file: status.file || jobId }, status);
      tbody.appendChild(row);
    });
  }
  
  // Create table row with progress indicator
  function createResultRow(index, item, processingStatus) {
    const row = document.createElement('tr');
    
    if (processingStatus) {
      // Processing row with progress bar
      row.innerHTML = `
        <td>${index}</td>
        <td>${item.file}</td>
        <td>
          <div class="progress mb-1">
            <div class="progress-bar progress-bar-striped progress-bar-animated" 
                 role="progressbar" 
                 style="width: ${processingStatus.progress}%">
              ${processingStatus.progress}%
            </div>
          </div>
          <small class="text-muted">${processingStatus.stage}</small>
        </td>
        <td>—</td>
      `;
    } else {
      // Completed row
      const summaryLink = item.status === 'completed' ? 
        `<a href="/static/${item.summary_file.split('static/')[1]}" 
           class="btn btn-sm btn-success">Download</a>` : '—';
      
      row.innerHTML = `
        <td>${index}</td>
        <td>${item.file}</td>
        <td><span class="badge bg-success">${item.status}</span></td>
        <td>${summaryLink}</td>
      `;
    }
    
    return row;
  }
  
  // Enhanced upload handler with progress feedback
  uploadForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const submitBtn = uploadForm.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    
    // Show loading state
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Uploading...';
    
    try {
      const formData = new FormData(uploadForm);
      const res = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });
      
      const data = await res.json();
      
      if (res.ok) {
        startPolling();
        showNotification(data.message, 'success');
        uploadForm.reset();
      } else {
        showNotification(data.error, 'error');
      }
    } catch (error) {
      showNotification('Upload failed: ' + error.message, 'error');
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
    }
  });
  
  // Enhanced start monitoring handler
  startBtn.addEventListener("click", async () => {
    const folder = folderInput.value.trim();
    if (!folder) {
      showNotification("Enter a valid path.", 'error');
      return;
    }
    
    startBtn.disabled = true;
    startBtn.textContent = 'Starting...';
    
    try {
      const res = await fetch("/api/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ folder }),
      });
      
      const data = await res.json();
      
      if (res.ok) {
        startPolling();
        showNotification(data.message, 'success');
        startBtn.textContent = 'Monitoring Active';
        startBtn.className = 'btn btn-success';
      } else {
        showNotification(data.error, 'error');
        startBtn.disabled = false;
        startBtn.textContent = 'Start Monitoring';
      }
    } catch (error) {
      showNotification('Failed to start monitoring: ' + error.message, 'error');
      startBtn.disabled = false;
      startBtn.textContent = 'Start Monitoring';
    }
  });
  
  // Notification system
  function showNotification(message, type) {
    const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert ${alertClass} alert-dismissible fade show`;
    alertDiv.innerHTML = `
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.querySelector('.container').insertBefore(alertDiv, document.querySelector('h2'));
    
    setTimeout(() => {
      if (alertDiv.parentNode) {
        alertDiv.remove();
      }
    }, 5000);
  }
  function updateMonitoringStatus(isActive, folder = '') {
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn'); // Add stop button
    
    if (isActive) {
        startBtn.textContent = `Monitoring: ${folder}`;
        startBtn.className = 'btn btn-success';
        startBtn.disabled = true;
        stopBtn.disabled = false;
    } else {
        startBtn.textContent = 'Start Monitoring';
        startBtn.className = 'btn btn-outline-primary';
        startBtn.disabled = false;
        stopBtn.disabled = true;
    }
}

  
  // Start polling on page load
  startPolling();
});

