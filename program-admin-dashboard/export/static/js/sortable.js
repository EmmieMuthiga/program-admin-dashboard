/**
 * Sortable.js implementation for drag-and-drop task board
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Sortable for each task list
    const taskLists = document.querySelectorAll('.task-list');
    
    taskLists.forEach(list => {
        new Sortable(list, {
            group: 'tasks',
            animation: 150,
            ghostClass: 'task-ghost',
            chosenClass: 'task-chosen',
            dragClass: 'task-drag',
            onEnd: function(evt) {
                const taskId = evt.item.getAttribute('data-task-id');
                const newStatus = evt.to.getAttribute('data-status');
                
                // Send AJAX request to update task status
                updateTaskStatus(taskId, newStatus);
                
                // Update empty messages
                updateEmptyMessages();
            }
        });
    });
    
    /**
     * Send AJAX request to update task status
     * 
     * @param {string} taskId - ID of the task to update
     * @param {string} status - New status value
     */
    function updateTaskStatus(taskId, status) {
        fetch(`/admin/tasks/${taskId}/update`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to update task status');
            }
            return response.json();
        })
        .then(data => {
            // Show success message
            const toastContainer = document.getElementById('toast-container');
            if (toastContainer) {
                const toast = document.createElement('div');
                toast.className = 'toast align-items-center text-white bg-success border-0';
                toast.setAttribute('role', 'alert');
                toast.setAttribute('aria-live', 'assertive');
                toast.setAttribute('aria-atomic', 'true');
                
                toast.innerHTML = `
                    <div class="d-flex">
                        <div class="toast-body">
                            Task status updated successfully!
                        </div>
                        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                    </div>
                `;
                
                toastContainer.appendChild(toast);
                const bsToast = new bootstrap.Toast(toast);
                bsToast.show();
                
                // Remove toast after it's hidden
                toast.addEventListener('hidden.bs.toast', function() {
                    toast.remove();
                });
            }
        })
        .catch(error => {
            console.error('Error updating task status:', error);
            
            // Show error message
            alert('Error updating task status. Please try again.');
            
            // Refresh the page to reset the UI
            window.location.reload();
        });
    }
    
    /**
     * Update empty message visibility based on task counts
     */
    function updateEmptyMessages() {
        taskLists.forEach(list => {
            const taskCards = list.querySelectorAll('.task-card');
            const emptyMessage = list.querySelector('.empty-message');
            
            if (emptyMessage) {
                if (taskCards.length === 0) {
                    emptyMessage.classList.remove('d-none');
                } else {
                    emptyMessage.classList.add('d-none');
                }
            }
        });
    }
    
    // Initial update of empty messages
    updateEmptyMessages();
    
    // Add counter badges to task columns
    function updateTaskCounters() {
        taskLists.forEach(list => {
            const status = list.getAttribute('data-status');
            const count = list.querySelectorAll('.task-card').length;
            const badge = document.querySelector(`.card-header .badge[data-status="${status}"]`);
            
            if (badge) {
                badge.textContent = count;
            }
        });
    }
    
    // Update counters initially
    updateTaskCounters();
    
    // Hook into Sortable's onAdd and onRemove events to update counters
    taskLists.forEach(list => {
        list._sortable.option('onAdd', function() {
            updateTaskCounters();
        });
        
        list._sortable.option('onRemove', function() {
            updateTaskCounters();
        });
    });
    
    // Enable changing task priority
    const priorityButtons = document.querySelectorAll('.change-priority');
    priorityButtons.forEach(button => {
        button.addEventListener('click', function() {
            const taskId = this.closest('.task-card').getAttribute('data-task-id');
            const newPriority = this.getAttribute('data-priority');
            
            fetch(`/admin/tasks/${taskId}/update`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ priority: newPriority }),
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to update task priority');
                }
                return response.json();
            })
            .then(data => {
                // Update the UI
                const badge = this.closest('.task-card').querySelector('.badge');
                if (badge) {
                    badge.className = `badge ${priorityClass(newPriority)}`;
                    badge.textContent = newPriority;
                }
            })
            .catch(error => {
                console.error('Error updating task priority:', error);
                alert('Error updating task priority. Please try again.');
            });
        });
    });
    
    /**
     * Get the appropriate Bootstrap badge class for a priority level
     * 
     * @param {string} priority - Priority level (high, medium, low)
     * @return {string} - Bootstrap badge class
     */
    function priorityClass(priority) {
        switch (priority) {
            case 'high':
                return 'bg-danger';
            case 'medium':
                return 'bg-warning';
            case 'low':
                return 'bg-info';
            default:
                return 'bg-secondary';
        }
    }
});
