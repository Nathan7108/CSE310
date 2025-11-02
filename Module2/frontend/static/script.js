// SpaceX Tracker - JavaScript Functions

function showLoading() {
    document.getElementById('loadingIndicator').style.display = 'block';
    document.getElementById('errorMessage').style.display = 'none';
    document.getElementById('launchData').style.display = 'none';
    document.getElementById('recentLaunches').style.display = 'none';
}

function hideLoading() {
    document.getElementById('loadingIndicator').style.display = 'none';
}

function showError(message) {
    hideLoading();
    document.getElementById('errorText').textContent = message;
    document.getElementById('errorMessage').style.display = 'block';
    document.getElementById('launchData').style.display = 'none';
    document.getElementById('recentLaunches').style.display = 'none';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        timeZoneName: 'short'
    });
}

function displayLaunchData(launch) {
    const launchDataDiv = document.getElementById('launchData');
    
    // Get core information
    let coreInfo = '';
    if (launch.cores && launch.cores.length > 0) {
        const core = launch.cores[0];
        const landingStatus = core.landing_success ? 'Success' : 'Failed';
        const landingType = core.landing_type || 'Unknown';
        coreInfo = `Landing: ${landingStatus} (${landingType})`;
        if (core.reused) {
            coreInfo += ' - Reused Core';
        }
    }

    // Get links
    const links = launch.links || {};
    const webcast = links.webcast || '';
    const article = links.article || '';
    const wikipedia = links.wikipedia || '';

    launchDataDiv.innerHTML = `
        <div class="launch-card">
            <div class="row">
                <div class="col-md-9">
                    <h4 class="text-primary mb-2">${launch.name || 'Unknown Mission'}</h4>
                    <p class="mb-1"><strong>Flight:</strong> ${launch.flight_number || 'Unknown'}</p>
                    <p class="mb-1"><strong>Date:</strong> ${formatDate(launch.date_utc)}</p>
                    ${coreInfo ? `<p class="mb-1"><strong>Core:</strong> ${coreInfo}</p>` : ''}
                </div>
                <div class="col-md-3 text-end">
                    <i class="fas fa-rocket rocket-icon"></i>
                </div>
            </div>
            
            ${launch.details ? `
            <div class="mission-details mt-3">
                <h6><i class="fas fa-info-circle"></i> Details</h6>
                <p class="mb-0">${launch.details}</p>
            </div>
            ` : ''}
            
            ${(webcast || article || wikipedia) ? `
            <div class="links-section mt-3">
                <h6><i class="fas fa-link"></i> Links</h6>
                ${webcast ? `<a href="${webcast}" target="_blank" class="link-item"><i class="fab fa-youtube"></i> Webcast</a>` : ''}
                ${article ? `<a href="${article}" target="_blank" class="link-item"><i class="fas fa-newspaper"></i> Article</a>` : ''}
                ${wikipedia ? `<a href="${wikipedia}" target="_blank" class="link-item"><i class="fab fa-wikipedia-w"></i> Wikipedia</a>` : ''}
            </div>
            ` : ''}
        </div>
    `;
    
    hideLoading();
    launchDataDiv.style.display = 'block';
    document.getElementById('recentLaunches').style.display = 'none';
}

function displayRecentLaunches(launches) {
    const recentLaunchesDiv = document.getElementById('recentLaunches');
    
    let html = '<h5><i class="fas fa-list"></i> Recent Launches</h5>';
    html += '<div class="row">';
    
    launches.forEach((launch, index) => {
        const launchDate = formatDate(launch.date_utc);
        
        html += `
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="launch-card" onclick="loadLaunchById('${launch.id}')">
                    <h6 class="text-primary mb-2">${launch.name || 'Unknown Mission'}</h6>
                    <p class="mb-1"><strong>Flight:</strong> ${launch.flight_number || 'Unknown'}</p>
                    <p class="mb-1"><strong>Date:</strong> ${launchDate}</p>
                    <p class="mb-0 text-muted"><small>Click for details</small></p>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    recentLaunchesDiv.innerHTML = html;
    
    hideLoading();
    recentLaunchesDiv.style.display = 'block';
    document.getElementById('launchData').style.display = 'none';
}

async function loadRecentLaunches() {
    showLoading();
    try {
        const response = await fetch('/api/launches');
        const result = await response.json();
        
        if (result.success) {
            displayRecentLaunches(result.data);
        } else {
            showError(result.error || 'Failed to load recent launches');
        }
    } catch (error) {
        showError('Network error: ' + error.message);
    }
}

async function loadLatestLaunch() {
    showLoading();
    try {
        const response = await fetch('/api/latest');
        const result = await response.json();
        
        if (result.success) {
            displayLaunchData(result.data);
        } else {
            showError(result.error || 'Failed to load latest launch');
        }
    } catch (error) {
        showError('Network error: ' + error.message);
    }
}

async function loadLaunchById(launchId = null) {
    if (!launchId) {
        launchId = document.getElementById('launchIdInput').value.trim();
        if (!launchId) {
            showError('Please enter a launch ID');
            return;
        }
    }

    showLoading();
    try {
        const response = await fetch(`/api/launch/${launchId}`);
        const result = await response.json();
        
        if (result.success) {
            displayLaunchData(result.data);
        } else {
            showError(result.error || 'Launch not found');
        }
    } catch (error) {
        showError('Network error: ' + error.message);
    }
}

// Load latest launch on page load
document.addEventListener('DOMContentLoaded', function() {
    loadLatestLaunch();
});
