// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// Utility Functions
const api = {
    async get(endpoint) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`);
            if (!response.ok) throw new Error('Network response was not ok');
            return await response.json();
        } catch (error) {
            console.error('GET Error:', error);
            throw error;
        }
    },

    async post(endpoint, data) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error('Network response was not ok');
            return await response.json();
        } catch (error) {
            console.error('POST Error:', error);
            throw error;
        }
    }
};

// Citizen Management
async function getOrCreateCitizen(name, phone, district = null) {
    try {
        // Try to get existing citizen
        const existing = await api.get(`/citizens/phone/${phone}`);
        return existing;
    } catch (error) {
        // Create new citizen
        const newCitizen = await api.post('/citizens/register', {
            name,
            phone,
            district
        });
        return newCitizen.citizen;
    }
}

// Load Dashboard Stats
async function loadStats() {
    try {
        const policies = await api.get('/policies/');
        const activePolicies = policies.filter(p => p.status === 'Active');
        document.getElementById('policy-count').textContent = activePolicies.length;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Show Result Message
function showResult(elementId, type, message) {
    const resultBox = document.getElementById(elementId);
    resultBox.className = `result-box ${type}`;
    resultBox.innerHTML = message;
    resultBox.style.display = 'block';
    
    // Auto hide after 5 seconds
    setTimeout(() => {
        resultBox.style.display = 'none';
    }, 5000);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    loadPolicies();
    setupForms();
    setupRatingStars();
});

// Rating Stars Setup
function setupRatingStars() {
    const stars = document.querySelectorAll('#rating-stars span');
    const ratingInput = document.getElementById('rating-value');
    
    stars.forEach(star => {
        star.addEventListener('click', () => {
            const value = star.getAttribute('data-value');
            ratingInput.value = value;
            
            // Update star display
            stars.forEach(s => {
                const starValue = parseInt(s.getAttribute('data-value'));
                if (starValue <= value) {
                    s.classList.add('active');
                } else {
                    s.classList.remove('active');
                }
            });
        });
    });
}