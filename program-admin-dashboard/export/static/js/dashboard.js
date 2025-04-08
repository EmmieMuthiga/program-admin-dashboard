document.addEventListener('DOMContentLoaded', function() {
    // Initialize program status chart (Pie chart)
    if (document.getElementById('programStatusChart')) {
        const statusCtx = document.getElementById('programStatusChart').getContext('2d');
        const programStatusChart = new Chart(statusCtx, {
            type: 'pie',
            data: {
                labels: programStatusData.labels,
                datasets: [{
                    data: programStatusData.data,
                    backgroundColor: [
                        'rgba(40, 167, 69, 0.7)',  // Active - green
                        'rgba(23, 162, 184, 0.7)', // Completed - info
                        'rgba(108, 117, 125, 0.7)', // Draft - secondary
                        'rgba(220, 53, 69, 0.7)'   // Cancelled - danger
                    ],
                    borderColor: [
                        'rgba(40, 167, 69, 1)',
                        'rgba(23, 162, 184, 1)',
                        'rgba(108, 117, 125, 1)',
                        'rgba(220, 53, 69, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#ccc'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = context.dataset.data.reduce((acc, val) => acc + val, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    // Initialize faculty load chart (Horizontal bar chart)
    if (document.getElementById('facultyLoadChart') && facultyLoadData.labels.length > 0) {
        const facultyCtx = document.getElementById('facultyLoadChart').getContext('2d');
        const facultyLoadChart = new Chart(facultyCtx, {
            type: 'bar',
            data: {
                labels: facultyLoadData.labels,
                datasets: [{
                    label: 'Programs Assigned',
                    data: facultyLoadData.data,
                    backgroundColor: 'rgba(255, 193, 7, 0.7)',
                    borderColor: 'rgba(255, 193, 7, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: {
                            color: '#ccc',
                            stepSize: 1
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    y: {
                        ticks: {
                            color: '#ccc'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    } else if (document.getElementById('facultyLoadChart')) {
        document.getElementById('facultyLoadChart').parentNode.innerHTML = 
            '<div class="text-center text-muted">No faculty data available</div>';
    }

    // Initialize program timeline chart (Line chart)
    if (document.getElementById('programTimelineChart') && programTimelineData.labels.length > 0) {
        const timelineCtx = document.getElementById('programTimelineChart').getContext('2d');
        const programTimelineChart = new Chart(timelineCtx, {
            type: 'line',
            data: {
                labels: programTimelineData.labels,
                datasets: [{
                    label: 'Upcoming Programs',
                    data: programTimelineData.data,
                    backgroundColor: 'rgba(13, 110, 253, 0.2)',
                    borderColor: 'rgba(13, 110, 253, 1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3,
                    pointBackgroundColor: 'rgba(13, 110, 253, 1)',
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        ticks: {
                            color: '#ccc'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: '#ccc',
                            stepSize: 1
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: '#ccc'
                        }
                    }
                }
            }
        });
    } else if (document.getElementById('programTimelineChart')) {
        document.getElementById('programTimelineChart').parentNode.innerHTML = 
            '<div class="text-center text-muted">No timeline data available</div>';
    }

    // Program status filter functionality
    const statusFilter = document.getElementById('program-status-filter');
    const programCounter = document.getElementById('program-counter');
    
    if (statusFilter) {
        statusFilter.addEventListener('change', function() {
            const selectedStatus = this.value;
            const programItems = document.querySelectorAll('.program-item');
            let visibleCount = 0;
            
            programItems.forEach(item => {
                const itemStatus = item.getAttribute('data-status');
                
                if (selectedStatus === 'all' || itemStatus === selectedStatus) {
                    item.style.display = 'block';
                    visibleCount++;
                } else {
                    item.style.display = 'none';
                }
            });
            
            // Update counter
            if (programCounter) {
                programCounter.textContent = visibleCount + (visibleCount === 1 ? ' program' : ' programs');
            }
        });
    }
});
