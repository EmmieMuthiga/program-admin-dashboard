/**
 * Main JavaScript file for Program Administration Assistant
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // Enable tooltips everywhere
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Enable popovers everywhere
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Handle file input display
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const fileNameDisplay = this.nextElementSibling;
            if (fileNameDisplay && fileNameDisplay.classList.contains('custom-file-label')) {
                if (this.files.length > 0) {
                    fileNameDisplay.textContent = this.files[0].name;
                } else {
                    fileNameDisplay.textContent = 'Choose file';
                }
            }
        });
    });
    
    // Format datetime inputs with current browser timezone
    const formatDatetimeInputs = () => {
        const datetimeInputs = document.querySelectorAll('input[type="datetime-local"]');
        datetimeInputs.forEach(input => {
            if (input.value) {
                // Keep the value as is, since the form expects the same format
                // Just ensure the value is not empty
            } else {
                // Set default to current time + 1 hour, rounded to nearest hour
                const now = new Date();
                now.setHours(now.getHours() + 1);
                now.setMinutes(0);
                now.setSeconds(0);
                
                // Format as YYYY-MM-DDThh:mm
                const year = now.getFullYear();
                const month = String(now.getMonth() + 1).padStart(2, '0');
                const day = String(now.getDate()).padStart(2, '0');
                const hours = String(now.getHours()).padStart(2, '0');
                const minutes = String(now.getMinutes()).padStart(2, '0');
                
                input.value = `${year}-${month}-${day}T${hours}:${minutes}`;
            }
        });
    };
    
    formatDatetimeInputs();
    
    // Handle confirmation dialogs
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm(this.dataset.confirm)) {
                e.preventDefault();
                return false;
            }
            return true;
        });
    });
    
    // Character counter for text areas
    const textareas = document.querySelectorAll('textarea[maxlength]');
    textareas.forEach(textarea => {
        const maxLength = textarea.getAttribute('maxlength');
        const counterDiv = document.createElement('div');
        counterDiv.className = 'small text-muted text-end mt-1';
        counterDiv.textContent = `0/${maxLength} characters`;
        textarea.parentNode.insertBefore(counterDiv, textarea.nextSibling);
        
        textarea.addEventListener('input', function() {
            const remaining = this.value.length;
            counterDiv.textContent = `${remaining}/${maxLength} characters`;
            
            if (remaining >= maxLength * 0.9) {
                counterDiv.classList.add('text-danger');
            } else {
                counterDiv.classList.remove('text-danger');
            }
        });
        
        // Initialize counter
        if (textarea.value) {
            textarea.dispatchEvent(new Event('input'));
        }
    });
    
    // Automatically show/hide password
    const passwordToggles = document.querySelectorAll('.password-toggle');
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const passwordInput = this.previousElementSibling;
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                this.innerHTML = '<i class="fas fa-eye-slash"></i>';
            } else {
                passwordInput.type = 'password';
                this.innerHTML = '<i class="fas fa-eye"></i>';
            }
        });
    });
    
    // Format date displays
    const formatDateElements = () => {
        const dateElements = document.querySelectorAll('.format-date');
        dateElements.forEach(element => {
            const date = new Date(element.textContent);
            if (!isNaN(date)) {
                const options = JSON.parse(element.dataset.options || '{}');
                element.textContent = date.toLocaleDateString(undefined, options);
            }
        });
    };
    
    formatDateElements();
    
    // Add confirm to delete buttons
    document.querySelectorAll('.btn-delete').forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
                return false;
            }
        });
    });
});

/**
 * Convert newlines to <br> elements
 * 
 * @param {string} str - The string to convert
 * @return {string} - Converted string with <br> elements
 */
function nl2br(str) {
    if (typeof str !== 'string') {
        return str;
    }
    return str.replace(/\n/g, '<br>');
}

/**
 * Format a date string
 * 
 * @param {string} dateStr - Date string to format
 * @param {object} options - Format options
 * @return {string} - Formatted date string
 */
function formatDate(dateStr, options = {}) {
    const date = new Date(dateStr);
    if (isNaN(date)) {
        return dateStr;
    }
    
    const defaultOptions = {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    };
    
    const formatOptions = {...defaultOptions, ...options};
    return date.toLocaleDateString(undefined, formatOptions);
}
