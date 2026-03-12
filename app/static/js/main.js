// Global configuration
const API_BASE = '/api';
const GOOGLE_MAPS_KEY = 'YOUR_GOOGLE_MAPS_KEY_HERE';

// Utility functions
async function fetchAPI(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Show notification
function showNotification(title, message, type = 'info') {
    const container = document.getElementById('notifications') || createNotificationsContainer();
    
    const notification = document.createElement('div');
    notification.className = `notification-item alert alert-${type}`;
    notification.innerHTML = `
        <strong>${title}</strong>
        <p>${message}</p>
    `;
    
    container.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

function createNotificationsContainer() {
    const container = document.createElement('div');
    container.id = 'notifications';
    container.className = 'notifications-container';
    document.body.appendChild(container);
    return container;
}

// Format date/time
function formatDateTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString();
}

function formatDate(isoString) {
    const date = new Date(isoString);
    return date.toLocaleDateString();
}

// Get geolocation
async function getUserLocation() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            reject(new Error('Geolocation not supported'));
        }
        
        navigator.geolocation.getCurrentPosition(
            position => {
                resolve({
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude
                });
            },
            error => reject(error)
        );
    });
}

// Initialize Leaflet Map
function initMap(elementId, options = {}) {
    const element = document.getElementById(elementId);
    
    if (!element) {
        console.error(`Map container '${elementId}' not found`);
        return null;
    }
    
    // Check if element has proper height
    if (element.offsetHeight === 0) {
        console.error(`Map container '${elementId}' has no height`);
        return null;
    }
    
    const defaultOptions = {
        zoom: 13,
        center: [28.6139, 77.2090], // Default to Delhi [lat, lng]
        ...options
    };
    
    try {
        console.log(`Initializing Leaflet map in container '${elementId}'`);
        
        // Initialize Leaflet map
        const map = L.map(elementId).setView(defaultOptions.center, defaultOptions.zoom);
        
        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(map);
        
        // Call invalidateSize to ensure map renders properly
        setTimeout(() => {
            map.invalidateSize();
        }, 100);
        
        console.log('Leaflet map initialized successfully');
        return map;
    } catch (error) {
        console.error('Error initializing map:', error);
        return null;
    }
}

// Add marker to Leaflet map
function addMarker(map, latitude, longitude, title = '') {
    if (!map) {
        return null;
    }
    
    try {
        const marker = L.marker([latitude, longitude]).addTo(map);
        if (title) {
            marker.bindPopup(title).openPopup();
        }
        return marker;
    } catch (error) {
        console.error('Error adding marker:', error);
        return null;
    }
}

// Calculate distance between two points
function calculateDistance(lat1, lon1, lat2, lon2) {
    return fetchAPI('/distance', {
        method: 'POST',
        body: JSON.stringify({
            lat1, lon1, lat2, lon2
        })
    });
}

// Load user status
async function loadUserStatus() {
    try {
        const response = await fetch('/api/user/status');
        const data = await response.json();
        
        const authBtn = document.getElementById('auth-btn');
        if (authBtn) {
            if (data.authenticated) {
                authBtn.innerHTML = `
                    <a href="/auth/profile">${data.full_name}</a> |
                    <a href="/auth/logout">Logout</a>
                `;
            } else {
                authBtn.innerHTML = `
                    <a href="/auth/login">Login</a> |
                    <a href="/auth/register">Register</a>
                `;
            }
        }
        
        return data;
    } catch (error) {
        console.error('Error loading user status:', error);
    }
}

// Load notifications
async function loadNotifications() {
    try {
        const data = await fetchAPI('/notifications/unread');
        return data;
    } catch (error) {
        console.error('Error loading notifications:', error);
        return [];
    }
}

// Mark notification as read
async function markNotificationRead(notificationId) {
    try {
        await fetchAPI(`/notifications/${notificationId}/read`, { method: 'POST' });
    } catch (error) {
        console.error('Error marking notification as read:', error);
    }
}

// Mark all notifications as read
async function markAllNotificationsRead() {
    try {
        await fetchAPI('/notifications/read-all', { method: 'POST' });
    } catch (error) {
        console.error('Error marking all notifications as read:', error);
    }
}

// Update user location
async function updateUserLocation() {
    try {
        const location = await getUserLocation();
        await fetchAPI('/user/location/update', {
            method: 'POST',
            body: JSON.stringify(location)
        });
    } catch (error) {
        console.error('Error updating location:', error);
    }
}

// Update the little red badges next to admin menu items
function updateNotificationBadges(notifications) {
    // compute counts per type
    const counts = {};
    notifications.forEach(n => {
        counts[n.type] = (counts[n.type] || 0) + 1;
    });

    // mapping from notification_type to badge element id
    const mapping = {
        'approval': 'manage-users',        // approvals affect users
        'donation': 'manage-donations',    // new donations for NGOs/adminds
        'request': 'manage-requests',      // food requests
        'delivery': 'manage-deliveries',   // delivery events
        'assignment': 'manage-deliveries', // assignments also count for deliveries
        'rejection': ''                    // we don't badge rejections
    };

    Object.entries(mapping).forEach(([type, elementId]) => {
        if (!elementId) return;
        const badge = document.getElementById(`badge-${elementId}`);
        if (!badge) return;
        const count = counts[type] || 0;
        if (count > 0) {
            badge.textContent = count;
            badge.style.display = 'inline-block';
        } else {
            badge.textContent = '';
            badge.style.display = 'none';
        }
    });

    // Update notification badges for donor/ngo/logistics (show total count of all notifications)
    const totalNotifications = notifications.length;
    ['donor-notifications', 'ngo-notifications', 'logistics-notifications'].forEach(elementId => {
        const badge = document.getElementById(`badge-${elementId}`);
        if (!badge) return;
        
        if (totalNotifications > 0) {
            badge.textContent = totalNotifications;
            badge.style.display = 'inline-block';
        } else {
            badge.textContent = '';
            badge.style.display = 'none';
        }
    });
}

// Poll for new notifications
function startNotificationPolling(interval = 30000) {
    async function poll() {
        try {
            const notifications = await loadNotifications();
            // show popup alerts and mark read as before
            if (notifications.length > 0) {
                updateNotificationBadges(notifications);
                notifications.forEach(notif => {
                    showNotification(notif.title, notif.message, 'info');
                    markNotificationRead(notif.id);
                });
            } else {
                // still clear badges if there are none
                updateNotificationBadges([]);
            }
        } catch (error) {
            console.error('Error polling notifications:', error);
        }
    }

    // run immediately then at interval
    poll();
    setInterval(poll, interval);
}

// Helper for counting animation
function animateCounters() {
    const counters = document.querySelectorAll('.stat-value');
    counters.forEach(counter => {
        const target = +counter.textContent.replace(/,/g, '') || 0;
        let count = 0;
        const step = target / 100;
        const update = () => {
            count += step;
            if (count < target) {
                counter.textContent = Math.floor(count).toLocaleString();
                requestAnimationFrame(update);
            } else {
                counter.textContent = target.toLocaleString();
            }
        };
        update();
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadUserStatus();
    startNotificationPolling();
    loadImpactStats().then(() => {
        animateCounters();
    });
});
