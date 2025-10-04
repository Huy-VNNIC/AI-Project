// Enhanced UI interactions for the Software Effort Estimation Tool

document.addEventListener('DOMContentLoaded', function() {
    // Rating stars functionality
    initRatingStars();
    
    // Enhanced result display
    enhanceResultDisplay();
    
    // Initialize feedback form
    initFeedbackForm();
});

// Initialize rating stars functionality
function initRatingStars() {
    const stars = document.querySelectorAll('.rating-star');
    const ratingInput = document.getElementById('accuracyRating');
    
    if (!stars.length || !ratingInput) return;
    
    stars.forEach(star => {
        star.addEventListener('click', function() {
            const rating = parseInt(this.getAttribute('data-rating'));
            ratingInput.value = rating;
            
            // Update active stars
            stars.forEach(s => {
                const starRating = parseInt(s.getAttribute('data-rating'));
                if (starRating <= rating) {
                    s.classList.remove('bi-star');
                    s.classList.add('bi-star-fill');
                    s.classList.add('active');
                } else {
                    s.classList.remove('bi-star-fill');
                    s.classList.remove('active');
                    s.classList.add('bi-star');
                }
            });
        });
        
        star.addEventListener('mouseover', function() {
            const rating = parseInt(this.getAttribute('data-rating'));
            
            // Preview active stars
            stars.forEach(s => {
                const starRating = parseInt(s.getAttribute('data-rating'));
                if (starRating <= rating) {
                    s.classList.remove('bi-star');
                    s.classList.add('bi-star-fill');
                } else {
                    s.classList.remove('bi-star-fill');
                    s.classList.add('bi-star');
                }
            });
        });
        
        star.addEventListener('mouseout', function() {
            const currentRating = parseInt(ratingInput.value) || 0;
            
            // Restore to actual rating
            stars.forEach(s => {
                const starRating = parseInt(s.getAttribute('data-rating'));
                if (starRating <= currentRating) {
                    s.classList.remove('bi-star');
                    s.classList.add('bi-star-fill');
                } else {
                    s.classList.remove('bi-star-fill');
                    s.classList.add('bi-star');
                }
            });
        });
    });
}

// Enhanced result display
function enhanceResultDisplay() {
    // Update confidence level display
    const confidenceLevel = document.getElementById('confidenceLevel');
    if (confidenceLevel) {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'characterData' || mutation.type === 'childList') {
                    const text = confidenceLevel.textContent;
                    if (text.includes('%')) {
                        const percent = parseInt(text);
                        let confidenceClass = '';
                        let confidenceText = '';
                        
                        if (percent < 50) {
                            confidenceClass = 'confidence-low';
                            confidenceText = 'Low';
                        } else if (percent < 75) {
                            confidenceClass = 'confidence-medium';
                            confidenceText = 'Medium';
                        } else {
                            confidenceClass = 'confidence-high';
                            confidenceText = 'High';
                        }
                        
                        confidenceLevel.innerHTML = `<span class="confidence-indicator ${confidenceClass}">${confidenceText} (${percent}%)</span>`;
                    }
                }
            });
        });
        
        observer.observe(confidenceLevel, { 
            characterData: true, 
            childList: true, 
            subtree: true 
        });
    }
    
    // Add animation to result cards
    const resultCards = document.querySelectorAll('.result-card');
    if (resultCards.length) {
        resultCards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            
            // Stagger the animations
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 100 * (index + 1));
        });
    }
}

// Initialize feedback form
function initFeedbackForm() {
    const feedbackForm = document.getElementById('feedbackForm');
    
    if (!feedbackForm) return;
    
    feedbackForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const rating = document.getElementById('accuracyRating').value;
        const comment = document.getElementById('feedbackComment').value;
        
        // Validate rating
        if (rating === '0') {
            showToast('Please provide a rating', 'warning');
            return;
        }
        
        // Prepare feedback data
        const feedbackData = {
            rating: parseInt(rating),
            comment: comment,
            timestamp: new Date().toISOString()
        };
        
        // Submit feedback to API
        fetch('/api/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(feedbackData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            showToast('Thank you for your feedback!', 'success');
            resetFeedbackForm();
        })
        .catch(error => {
            console.error('Error submitting feedback:', error);
            showToast('Error submitting feedback. Please try again.', 'danger');
        });
    });
}

// Reset feedback form
function resetFeedbackForm() {
    document.getElementById('accuracyRating').value = '0';
    document.getElementById('feedbackComment').value = '';
    
    const stars = document.querySelectorAll('.rating-star');
    stars.forEach(star => {
        star.classList.remove('bi-star-fill');
        star.classList.remove('active');
        star.classList.add('bi-star');
    });
}

// Get color for model type
function getModelColor(modelName) {
    const colors = {
        // COCOMO models
        cocomo: '#4361ee',
        organic: '#3a86ff',
        semidetached: '#4895ef',
        embedded: '#4cc9f0',
        
        // Function point models
        function_point: '#3f37c9',
        fp: '#5e60ce',
        
        // Use case models
        use_case: '#7209b7',
        ucp: '#b5179e',
        
        // LOC models
        loc: '#480ca8',
        sloc: '#560bad',
        
        // ML models
        ml_regression: '#f72585',
        ml_neural: '#f25c54',
        ml_ensemble: '#fb6f92',
        
        // Other
        fallback: '#6c757d',
        custom: '#212529',
        default: '#495057'
    };
    
    // Convert to lowercase for matching
    const model = modelName.toLowerCase();
    
    // Find matching color
    for (const [key, color] of Object.entries(colors)) {
        if (model.includes(key)) {
            return color;
        }
    }
    
    // Default color
    return colors.default;
}

// Show toast notification
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    
    // Create toast container if it doesn't exist
    if (!toastContainer) {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(container);
    }
    
    // Create toast element
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.id = toastId;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    // Create toast content
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    // Add toast to container
    document.getElementById('toastContainer').appendChild(toast);
    
    // Initialize and show the toast
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: 5000
    });
    bsToast.show();
    
    // Remove toast after hidden
    toast.addEventListener('hidden.bs.toast', function() {
        document.getElementById(toastId).remove();
    });
}