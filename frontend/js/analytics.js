const API_BASE_URL = 'http://localhost:5000/api';
let currentUser = null;
let authToken = null;
let charts = {};
let analyticsData = {};

// Check authentication
function checkAuth() {
    authToken = localStorage.getItem('token');
    const userStr = localStorage.getItem('user');

    if (!authToken || !userStr) {
        window.location.href = 'login.html';
        return;
    }

    currentUser = JSON.parse(userStr);
    document.getElementById('user-name').textContent = currentUser.name;
    document.getElementById('user-district').textContent = currentUser.district_name || 'District';
}

// Logout
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = 'login.html';
}

// API call with auth
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`
        }
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);

    if (response.status === 401) {
        logout();
        return;
    }

    return await response.json();
}

// Load all analytics data
async function loadAnalytics() {
    try {
        // Load dashboard stats
        const dashboard = await apiCall('/analytics/dashboard');
        if (dashboard) {
            document.getElementById('stat-total').textContent = dashboard.total_complaints;
            document.getElementById('stat-resolution').textContent = dashboard.resolution_rate + '%';
            document.getElementById('stat-recent').textContent = dashboard.recent_complaints;
            document.getElementById('stat-rating').textContent = dashboard.average_rating;
        }

        // Load ministry data
        const ministryData = await apiCall('/analytics/complaints-by-ministry');
        if (ministryData) {
            analyticsData.ministry = ministryData;
            createMinistryChart(ministryData);
        }

        // Load district data
        const districtData = await apiCall('/analytics/complaints-by-district');
        if (districtData) {
            analyticsData.district = districtData;
            createDistrictChart(districtData);
            populateDistrictFilter(districtData);
        }

        // Load category data
        const categoryData = await apiCall('/analytics/complaints-by-category');
        if (categoryData) {
            analyticsData.category = categoryData;
            createCategoryChart(categoryData);
        }

        // Load timeline data
        const timelineData = await apiCall('/analytics/complaints-timeline');
        if (timelineData) {
            analyticsData.timeline = timelineData;
            createTimelineChart(timelineData);
        }

        // Load ministry performance
        const performanceData = await apiCall('/analytics/ministry-performance');
        if (performanceData) {
            analyticsData.performance = performanceData;
            loadMinistryPerformance(performanceData);
            populateMinistryFilter(performanceData);
        }

        // Load unresolved by ministry
        const unresolvedData = await apiCall('/analytics/unresolved-by-ministry');
        if (unresolvedData) {
            analyticsData.unresolved = unresolvedData;
            createUnresolvedChart(unresolvedData);
        }

        // Load top issues
        const topIssues = await apiCall('/analytics/top-issues');
        if (topIssues) {
            loadTopIssues(topIssues);
        }

        // Create status chart
        createStatusChart(dashboard);

    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

// Create Ministry Chart
function createMinistryChart(data) {
    const ctx = document.getElementById('ministryChart');
    
    if (charts.ministry) {
        charts.ministry.destroy();
    }

    charts.ministry = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.code),
            datasets: [
                {
                    label: 'Total',
                    data: data.map(d => d.total),
                    backgroundColor: 'rgba(102, 126, 234, 0.7)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Resolved',
                    data: data.map(d => d.resolved),
                    backgroundColor: 'rgba(16, 185, 129, 0.7)',
                    borderColor: 'rgba(16, 185, 129, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Complaint Distribution by Ministry'
                },
                tooltip: {
                    callbacks: {
                        afterLabel: function(context) {
                            const index = context.dataIndex;
                            const ministry = data[index];
                            return `Pending: ${ministry.pending}\nIn Progress: ${ministry.in_progress}`;
                        }
                    }
                }
            }
        }
    });
}

// Create Status Chart
function createStatusChart(dashboard) {
    const ctx = document.getElementById('statusChart');
    
    if (charts.status) {
        charts.status.destroy();
    }

    charts.status = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Pending', 'In Progress', 'Resolved'],
            datasets: [{
                data: [
                    dashboard.pending_complaints,
                    dashboard.in_progress_complaints,
                    dashboard.resolved_complaints
                ],
                backgroundColor: [
                    'rgba(251, 191, 36, 0.7)',
                    'rgba(59, 130, 246, 0.7)',
                    'rgba(16, 185, 129, 0.7)'
                ],
                borderColor: [
                    'rgba(251, 191, 36, 1)',
                    'rgba(59, 130, 246, 1)',
                    'rgba(16, 185, 129, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                title: {
                    display: true,
                    text: 'Status Distribution'
                }
            }
        }
    });
}

// Create District Chart
function createDistrictChart(data) {
    const ctx = document.getElementById('districtChart');
    
    if (charts.district) {
        charts.district.destroy();
    }

    // Get top 10 districts
    const topDistricts = data.slice(0, 10);

    charts.district = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: topDistricts.map(d => d.district),
            datasets: [{
                label: 'Complaints',
                data: topDistricts.map(d => d.total),
                backgroundColor: 'rgba(118, 75, 162, 0.7)',
                borderColor: 'rgba(118, 75, 162, 1)',
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    beginAtZero: true
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Top 10 Districts by Complaint Volume'
                }
            }
        }
    });
}

// Create Category Chart
function createCategoryChart(data) {
    const ctx = document.getElementById('categoryChart');
    
    if (charts.category) {
        charts.category.destroy();
    }

    charts.category = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.map(d => d.category),
            datasets: [{
                data: data.map(d => d.count),
                backgroundColor: [
                    'rgba(102, 126, 234, 0.7)',
                    'rgba(118, 75, 162, 0.7)',
                    'rgba(16, 185, 129, 0.7)',
                    'rgba(251, 191, 36, 0.7)',
                    'rgba(239, 68, 68, 0.7)',
                    'rgba(59, 130, 246, 0.7)',
                    'rgba(168, 85, 247, 0.7)',
                    'rgba(236, 72, 153, 0.7)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                title: {
                    display: true,
                    text: 'Complaints by Category'
                }
            }
        }
    });
}

// Create Timeline Chart
function createTimelineChart(data) {
    const ctx = document.getElementById('timelineChart');
    
    if (charts.timeline) {
        charts.timeline.destroy();
    }

    charts.timeline = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => d.month),
            datasets: [{
                label: 'Complaints',
                data: data.map(d => d.count),
                borderColor: 'rgba(102, 126, 234, 1)',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true,
                pointRadius: 5,
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Complaint Trends Over Time'
                }
            }
        }
    });
}

// Create Unresolved Chart
function createUnresolvedChart(data) {
    const ctx = document.getElementById('unresolvedChart');
    
    if (charts.unresolved) {
        charts.unresolved.destroy();
    }

    charts.unresolved = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.ministry),
            datasets: [{
                label: 'Unresolved Complaints',
                data: data.map(d => d.unresolved_count),
                backgroundColor: 'rgba(239, 68, 68, 0.7)',
                borderColor: 'rgba(239, 68, 68, 1)',
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    beginAtZero: true
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Unresolved Complaints by Ministry'
                }
            }
        }
    });
}

// Load Ministry Performance Table
function loadMinistryPerformance(data) {
    const tbody = document.getElementById('ministry-performance');

    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 30px;">No data available</td></tr>';
        return;
    }

    tbody.innerHTML = data.map(ministry => `
        <tr>
            <td><strong>${ministry.ministry}</strong></td>
            <td>${ministry.total_complaints}</td>
            <td>${ministry.resolved}</td>
            <td>
                <span class="status-badge ${ministry.resolution_rate >= 70 ? 'status-resolved' : ministry.resolution_rate >= 40 ? 'status-in-progress' : 'status-pending'}">
                    ${ministry.resolution_rate}%
                </span>
            </td>
            <td>${ministry.avg_resolution_days} days</td>
        </tr>
    `).join('');
}

// Load Top Issues
function loadTopIssues(data) {
    const container = document.getElementById('top-issues');

    if (data.length === 0) {
        container.innerHTML = '<p style="color: #666;">No issues identified yet</p>';
        return;
    }

    container.innerHTML = data.map(issue => `
        <div style="background: #f0f0f0; padding: 10px 15px; border-radius: 20px; display: flex; align-items: center; gap: 8px;">
            <span style="font-weight: 600;">${issue.keyword}</span>
            <span style="background: #667eea; color: white; padding: 3px 8px; border-radius: 10px; font-size: 0.85rem;">${issue.count}</span>
        </div>
    `).join('');
}

// Populate filter dropdowns
function populateMinistryFilter(data) {
    const select = document.getElementById('filter-ministry');
    const ministries = [...new Set(data.map(d => d.ministry))];
    
    ministries.forEach(ministry => {
        const option = document.createElement('option');
        option.value = ministry;
        option.textContent = ministry;
        select.appendChild(option);
    });
}

function populateDistrictFilter(data) {
    const select = document.getElementById('filter-district');
    const districts = [...new Set(data.map(d => d.district))];
    
    districts.forEach(district => {
        const option = document.createElement('option');
        option.value = district;
        option.textContent = district;
        select.appendChild(option);
    });
}

// Apply filters (simplified version - in production would filter actual data)
function applyFilters() {
    const ministry = document.getElementById('filter-ministry').value;
    const district = document.getElementById('filter-district').value;
    const status = document.getElementById('filter-status').value;

    console.log('Filters applied:', { ministry, district, status });
    
    // In production, this would fetch filtered data from API
    // For now, just log the filters
    alert(`Filters applied:\nMinistry: ${ministry || 'All'}\nDistrict: ${district || 'All'}\nStatus: ${status || 'All'}\n\nNote: Full filtering will be implemented with backend API.`);
}

// Reset filters
function resetFilters() {
    document.getElementById('filter-ministry').value = '';
    document.getElementById('filter-district').value = '';
    document.getElementById('filter-status').value = '';
    loadAnalytics();
}

// Generate Report
async function generateReport() {
    try {
        const response = await apiCall('/analytics/generate-report', 'POST', {
            generated_by: currentUser.id
        });

        if (response) {
            alert('Report generated successfully! Check the admin panel for details.');
        }
    } catch (error) {
        console.error('Error generating report:', error);
        alert('Failed to generate report. This feature requires admin access.');
    }
}

// Initialize
checkAuth();
loadAnalytics();