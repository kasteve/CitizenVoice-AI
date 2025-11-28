// Load and Display Policies
async function loadPolicies() {
    try {
        const policies = await api.get('/policies/?status=Active');
        const policiesList = document.getElementById('policies-list');
        const feedbackPolicySelect = document.getElementById('feedback-policy');
        
        // Clear existing content
        policiesList.innerHTML = '';
        feedbackPolicySelect.innerHTML = '<option value="">Choose a policy...</option>';
        
        if (policies.length === 0) {
            policiesList.innerHTML = '<p>No active policies for consultation at the moment.</p>';
            return;
        }
        
        // Display each policy
        for (const policy of policies) {
            // Get policy details with feedback
            const details = await api.get(`/policies/${policy.id}`);
            
            const policyCard = document.createElement('div');
            policyCard.className = 'policy-card';
            
            const totalFeedback = details.feedback_count || 0;
            const sentiment = details.sentiment_distribution || {positive: 0, neutral: 0, negative: 0};
            
            policyCard.innerHTML = `
                <h3>${policy.title}</h3>
                <div>
                    <span class="policy-category">${policy.category || 'General'}</span>
                    <span class="policy-status ${policy.status.toLowerCase()}">${policy.status}</span>
                </div>
                <p class="policy-description">${policy.description || 'No description available'}</p>
                <div class="policy-meta">
                    <span>📅 Deadline: ${policy.deadline ? new Date(policy.deadline).toLocaleDateString() : 'Ongoing'}</span>
                    <span>💬 ${totalFeedback} Feedback</span>
                </div>
                <div class="sentiment-bar">
                    <span class="sentiment-item sentiment-positive">👍 ${sentiment.positive}</span>
                    <span class="sentiment-item sentiment-neutral">😐 ${sentiment.neutral}</span>
                    <span class="sentiment-item sentiment-negative">👎 ${sentiment.negative}</span>
                </div>
            `;
            
            policiesList.appendChild(policyCard);
            
            // Add to feedback select
            const option = document.createElement('option');
            option.value = policy.id;
            option.textContent = policy.title;
            feedbackPolicySelect.appendChild(option);
        }
        
    } catch (error) {
        console.error('Error loading policies:', error);
        document.getElementById('policies-list').innerHTML = 
            '<p style="color: red;">Error loading policies. Please try again later.</p>';
    }
}