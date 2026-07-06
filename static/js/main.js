/* =========================================================================
   Gyan Pustak - Vanilla JS Logic
   ========================================================================= */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Dark Theme Toggle Logic
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    if (themeToggleBtn) {
        // Check local storage for preference
        const currentTheme = localStorage.getItem('theme');
        if (currentTheme === 'dark') {
            document.body.classList.add('dark-theme');
            themeToggleBtn.innerHTML = '<i class="fas fa-sun"></i>';
        } else {
            themeToggleBtn.innerHTML = '<i class="fas fa-moon"></i>';
        }
        
        themeToggleBtn.addEventListener('click', () => {
            document.body.classList.toggle('dark-theme');
            let theme = 'light';
            if (document.body.classList.contains('dark-theme')) {
                theme = 'dark';
                themeToggleBtn.innerHTML = '<i class="fas fa-sun"></i>';
            } else {
                themeToggleBtn.innerHTML = '<i class="fas fa-moon"></i>';
            }
            localStorage.setItem('theme', theme);
        });
    }

    // 2. Auto-close Toast Notifications after 4 seconds
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(toast => {
        setTimeout(() => {
            closeToast(toast);
        }, 4000);
    });

    // 3. Modal Opening/Closing Controls
    window.openModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'flex';
        }
    };

    window.closeModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
        }
    };
    
    // Close modal when clicking outside the card
    window.addEventListener('click', (e) => {
        const modalOverlays = document.querySelectorAll('.modal-overlay');
        modalOverlays.forEach(overlay => {
            if (e.target === overlay) {
                overlay.style.display = 'none';
            }
        });
    });

    // 4. Chart.js Initialization (Admin/SuperAdmin Dashboards)
    const categoryChartCanvas = document.getElementById('categoryChart');
    if (categoryChartCanvas) {
        fetch('/api/charts/books-by-category')
            .then(res => res.json())
            .then(data => {
                if (data.labels && data.values) {
                    new Chart(categoryChartCanvas, {
                        type: 'doughnut',
                        data: {
                            labels: data.labels,
                            datasets: [{
                                data: data.values,
                                backgroundColor: [
                                    '#0284c7', '#0d9488', '#b45309', '#be185d', '#4f46e5'
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
                                        color: getComputedStyle(document.body).getPropertyValue('--text-primary').strip || '#1e293b'
                                    }
                                }
                            }
                        }
                    });
                }
            })
            .catch(err => console.error("Error loading category chart:", err));
    }

    const trendsChartCanvas = document.getElementById('trendsChart');
    if (trendsChartCanvas) {
        fetch('/api/charts/borrowing-trends')
            .then(res => res.json())
            .then(data => {
                if (data.labels && data.values) {
                    new Chart(trendsChartCanvas, {
                        type: 'bar',
                        data: {
                            labels: data.labels,
                            datasets: [{
                                label: 'Borrow Counts',
                                data: data.values,
                                backgroundColor: 'rgba(14, 165, 233, 0.7)',
                                borderColor: '#0ea5e9',
                                borderWidth: 1
                            }]
                        },
                        options: {
                            responsive: true,
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    ticks: {
                                        stepSize: 1
                                    }
                                }
                            }
                        }
                    });
                }
            })
            .catch(err => console.error("Error loading trends chart:", err));
    }
});

// Toast Close Function
function closeToast(toastElement) {
    toastElement.style.opacity = '0';
    toastElement.style.transform = 'translateY(-20px)';
    toastElement.style.transition = 'all 0.3s ease-out';
    setTimeout(() => {
        toastElement.remove();
    }, 300);
}
