// Setup All Forms
function setupForms() {
    setupFeedbackForm();
    setupComplaintForm();
    setupTrackForm();
    setupRatingForm();
}

// Feedback Form
function setupFeedbackForm() {
    const form = document.getElementById('feedback-form');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const submitBtn = form.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="loading"></span> Submitting...';
        
        try {
            const name = document.getElementById('feedback-name').value;
            const phone = document.getElementById('feedback-phone').value;
            const policyId = document.getElementById('feedback-policy').value;
            const feedbackText = document.getElementById('feedback-text').value;
            
            // Get or create citizen
            const citizen = await getOrCreateCitizen(name, phone);
            
            // Submit feedback
            const result = await api.post('/feedback/policy', {
                policy_id: policyId,
                citizen_id: citizen.id,
                feedback_text: feedbackText
            });
            
            const message = `
                <h4>✅ Feedback Submitted Successfully!</h4>
                <p><strong>Sentiment Analysis:</strong> ${result.analysis.sentiment.toUpperCase()}</p>
                <p><strong>Themes Identified:</strong> ${result.analysis.themes.join(', ')}</p>
                <p>Thank you for your participation in policy-making!</p>
            `;
            
            showResult('feedback-result', 'success', message);
            form.reset();
            loadStats();
            
        } catch (error) {
            showResult('feedback-result', 'error', 
                '<h4>❌ Error</h4><p>Failed to submit feedback. Please try again.</p>');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Feedback';
        }
    });
}

// Complaint Form
function setupComplaintForm() {
    const form = document.getElementById('complaint-form');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const submitBtn = form.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="loading"></span> Submitting...';
        
        try {
            const name = document.getElementById('complaint-name').value;
            const phone = document.getElementById('complaint-phone').value;
            const category = document.getElementById('complaint-category').value;
            const location = document.getElementById('complaint-location').value;
            const description = document.getElementById('complaint-description').value;
            
            // Get or create citizen
            const citizen = await getOrCreateCitizen(name, phone, location);
            
            // Submit complaint
            const result = await api.post('/feedback/complaint', {
                citizen_id: citizen.id,
                category: category,
                location: location,
                description: description
            });
            
            const message = `
                <h4>✅ Complaint Submitted Successfully!</h4>
                <p><strong>Tracking Number:</strong> ${result.tracking_number}</p>
                <p><strong>Priority:</strong> ${result.complaint.priority}</p>
                <p><strong>Category:</strong> ${result.complaint.category}</p>
                <p>Please save your tracking number to check the status of your complaint.</p>
            `;
            
            showResult('complaint-result', 'success', message);
            form.reset();
            
        } catch (error) {
            showResult('complaint-result', 'error', 
                '<h4>❌ Error</h4><p>Failed to submit complaint. Please try again.</p>');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Complaint';
        }
    });
}

// Track Complaint Form
function setupTrackForm() {
    const form = document.getElementById('track-form');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const submitBtn = form.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="loading"></span> Tracking...';
        
        try {
            const trackingNumber = document.getElementById('track-number').value.trim().toUpperCase();
            
            const result = await api.get(`/feedback/complaint/${trackingNumber}`);
            
            const statusColor = result.status === 'Resolved' ? 'success' : 
                              result.status === 'In Progress' ? 'info' : 'info';
            
            const message = `
                <h4>📋 Complaint Status</h4>
                <p><strong>Tracking Number:</strong> ${result.tracking_number}</p>
                <p><strong>Status:</strong> ${result.status}</p>
                <p><strong>Category:</strong> ${result.category}</p>
                <p><strong>Priority:</strong> ${result.priority}</p>
                <p><strong>Location:</strong> ${result.location}</p>
                <p><strong>Submitted:</strong> ${new Date(result.created_at).toLocaleString()}</p>
                ${result.resolved_at ? `<p><strong>Resolved:</strong> ${new Date(result.resolved_at).toLocaleString()}</p>` : ''}
            `;
            
            showResult('track-result', statusColor, message);
            
        } catch (error) {
            showResult('track-result', 'error', 
                '<h4>❌ Not Found</h4><p>Tracking number not found. Please check and try again.</p>');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Track Status';
        }
    });
}

// Rating Form
function setupRatingForm() {
    const form = document.getElementById('rating-form');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const ratingValue = document.getElementById('rating-value').value;
        
        if (ratingValue === '0') {
            showResult('rating-result', 'error', 
                '<h4>⚠️ Please Select Rating</h4><p>Click on the stars to rate the service.</p>');
            return;
        }
        
        const submitBtn = form.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="loading"></span> Submitting...';
        
        try {
            const name = document.getElementById('rating-name').value;
            const phone = document.getElementById('rating-phone').value;
            const serviceType = document.getElementById('rating-service-type').value;
            const location = document.getElementById('rating-location').value;
            const comment = document.getElementById('rating-comment').value;
            
            // Get or create citizen
            const citizen = await getOrCreateCitizen(name, phone);
            
            // Submit rating
            const result = await api.post('/feedback/rating', {
                citizen_id: citizen.id,
                service_type: serviceType,
                service_location: location,
                rating: parseInt(ratingValue),
                comment: comment
            });
            
            const message = `
                <h4>✅ Rating Submitted Successfully!</h4>
                <p><strong>Service:</strong> ${serviceType}</p>
                <p><strong>Location:</strong> ${location}</p>
                <p><strong>Rating:</strong> ${'⭐'.repeat(parseInt(ratingValue))}</p>
                <p>Thank you for helping improve public services!</p>
            `;
            
            showResult('rating-result', 'success', message);
            form.reset();
            document.getElementById('rating-value').value = '0';
            document.querySelectorAll('#rating-stars span').forEach(s => s.classList.remove('active'));
            
        } catch (error) {
            showResult('rating-result', 'error', 
                '<h4>❌ Error</h4><p>Failed to submit rating. Please try again.</p>');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Rating';
        }
    });
}