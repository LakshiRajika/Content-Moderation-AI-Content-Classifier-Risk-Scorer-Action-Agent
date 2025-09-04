document.addEventListener('DOMContentLoaded', function() {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const contentInput = document.getElementById('contentInput');
    const userIdInput = document.getElementById('userId');
    const resultsDiv = document.getElementById('results');
    const loadingDiv = document.getElementById('loading');
    const errorDiv = document.getElementById('error');
    const refreshBtn = document.getElementById('refreshStatsBtn');
    
    // Initialize
    loadTransparencyStats();
    
    // Event listeners
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', analyzeContent);
    }
    
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadTransparencyStats);
    }
    
    async function analyzeContent() {
        const content = contentInput.value.trim();
        const userId = userIdInput.value.trim() || 'anonymous';
        
        if (!content) {
            showError('Please enter some content to analyze.');
            return;
        }
        
        localStorage.setItem('lastModeratedContent', content);

        // Show loading, hide results and error
        loadingDiv.classList.remove('hidden');
        resultsDiv.classList.add('hidden');
        errorDiv.classList.add('hidden');
        
        try {
            const response = await fetch('/moderate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    content: content,
                    user_id: userId
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                displayResults(data);
                // Refresh stats after successful analysis
                setTimeout(loadTransparencyStats, 500);
            } else {
                showError(data.error || 'An error occurred during analysis.');
            }
        } catch (error) {
            showError('Network error. Please try again.');
        } finally {
            loadingDiv.classList.add('hidden');
        }
    }
    
    function displayResults(data) {
        // Display classification results
        const classificationContainer = document.getElementById('classificationResults');
        classificationContainer.innerHTML = '';
        
        for (const [category, confidence] of Object.entries(data.classification)) {
            const confidencePercent = (confidence * 100).toFixed(1);
            const classificationItem = document.createElement('div');
            classificationItem.className = 'classification-item';
            classificationItem.innerHTML = `
                <div>${category}</div>
                <div>${confidencePercent}%</div>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: ${confidencePercent}%"></div>
                </div>
            `;
            classificationContainer.appendChild(classificationItem);
        }
        
        // Display risk assessment
        const riskContainer = document.getElementById('riskResults');
        riskContainer.className = `results-container risk-level-${data.risk_score.level.toLowerCase()}`;
        riskContainer.innerHTML = `
            <div><strong>Score:</strong> ${(data.risk_score.score * 100).toFixed(1)}%</div>
            <div><strong>Level:</strong> ${data.risk_score.level}</div>
            ${data.risk_score.reasons && data.risk_score.reasons.length ? `
                <div style="margin-top: 10px;">
                    <strong>Reasons:</strong>
                    <ul>
                        ${data.risk_score.reasons.map(reason => `<li>${reason}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
        `;
        
        // Display actions
        const actionContainer = document.getElementById('actionResults');
        actionContainer.innerHTML = '';
        
        if (data.action && data.action.actions) {
            data.action.actions.forEach(action => {
                const actionItem = document.createElement('div');
                actionItem.className = 'action-item';
                actionItem.textContent = action;
                actionContainer.appendChild(actionItem);
            });
        }
        
        // Show results
        resultsDiv.classList.remove('hidden');
    }
    
    function showError(message) {
        errorDiv.textContent = message;
        errorDiv.classList.remove('hidden');
    }
    
    // Load transparency statistics
    async function loadTransparencyStats() {
        try {
            const response = await fetch('/api/audit-stats');
            const data = await response.json();
            
            if (response.ok) {
                // Update the transparency dashboard
                document.getElementById('totalDecisions').textContent = data.total_decisions;
                document.getElementById('highRiskPercent').textContent = data.high_risk_percentage + '%';
                document.getElementById('mediumRiskPercent').textContent = data.medium_risk_percentage + '%';
                document.getElementById('highRiskCount').textContent = '(' + data.high_risk_count + ')';
                document.getElementById('mediumRiskCount').textContent = '(' + data.medium_risk_count + ')';
                
                // Update debug info
                document.getElementById('debugInfo').textContent = JSON.stringify(data, null, 2);
            } else {
                console.error('Error loading stats:', data.error);
                document.getElementById('debugInfo').textContent = 'Error: ' + (data.error || 'Unknown error');
            }
        } catch (error) {
            console.error('Error loading transparency stats:', error);
            document.getElementById('debugInfo').textContent = 'Error: ' + error.message;
        }
    }
}); // ← END OF DOMContentLoaded

// MOVE THE submitFeedback FUNCTION OUTSIDE OF DOMContentLoaded
async function submitFeedback() {
    const accuracySelect = document.getElementById('feedbackAccuracy');
    const notesTextarea = document.getElementById('feedbackNotes');
    
    const accuracy = accuracySelect ? accuracySelect.value : '';
    const notes = notesTextarea ? notesTextarea.value : '';
    
    console.log('Submit feedback called:', accuracy, notes);
    
    if (!accuracy) {
        alert('Please select whether the analysis was accurate');
        return;
    }
    
    try {
        // Get the last moderated content from localStorage
        const lastContent = localStorage.getItem('lastModeratedContent') || 'Unknown content';
        const userId = document.getElementById('userId') ? document.getElementById('userId').value : 'anonymous';
        
        const response = await fetch('/api/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content: lastContent,
                user_id: userId,
                accurate: accuracy === 'accurate',
                notes: notes
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Thank you for your feedback! This helps improve our AI system.');
            
            // Reset the form
            if (accuracySelect) accuracySelect.value = '';
            if (notesTextarea) notesTextarea.value = '';
        } else {
            alert('Error submitting feedback: ' + (data.error || 'Please try again.'));
        }
    } catch (error) {
        console.error('Feedback error:', error);
        alert('Error submitting feedback. Please try again.');
    }
}