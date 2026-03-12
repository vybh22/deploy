// Donor functions
class DonorUtils {
    static async initializeMapPicker(elementId) {
        const map = initMap(elementId, {
            zoom: 15,
            center: [28.6139, 77.2090]
        });
        
        // If map initialization failed, return early
        if (!map) {
            console.error('Map initialization failed');
            return null;
        }
        
        let marker;
        
        // Check if location is already set (for profile editing)
        const latInput = document.getElementById('latitude');
        const lngInput = document.getElementById('longitude');
        if (latInput && lngInput && latInput.value && lngInput.value) {
            const lat = parseFloat(latInput.value);
            const lng = parseFloat(lngInput.value);
            if (!isNaN(lat) && !isNaN(lng)) {
                map.setView([lat, lng], 15);
                marker = L.marker([lat, lng]).addTo(map).bindPopup('Location').openPopup();
            }
        } else {
            // Try to get user location for new entries
            try {
                const location = await getUserLocation();
                if (map) {
                    map.setView([location.latitude, location.longitude], 15);
                }
            } catch (error) {
                console.error('Error getting location:', error);
            }
        }
        
        // Add click listener
        map.on('click', (event) => {
            const lat = event.latlng.lat;
            const lng = event.latlng.lng;
            
            // Update hidden form fields
            if (latInput) latInput.value = lat;
            if (lngInput) lngInput.value = lng;
            
            // Remove previous marker
            if (marker) {
                map.removeLayer(marker);
            }
            
            // Add new marker
            marker = L.marker([lat, lng]).addTo(map).bindPopup('Location').openPopup();
        });
        
        return map;
    }
    
    static async createListing(formData) {
        try {
            // Validate form data
            const errors = [];
            
            if (!formData.get('food_type')) errors.push('Food type is required');
            if (!formData.get('quantity')) errors.push('Quantity is required');
            if (!formData.get('expiry_time')) errors.push('Expiry time is required');
            if (!formData.get('latitude')) errors.push('Location is required');
            
            if (errors.length > 0) {
                showNotification('Validation Error', errors.join(', '), 'danger');
                return false;
            }
            
            // Form will auto-submit
            return true;
        } catch (error) {
            showNotification('Error', error.message, 'danger');
            return false;
        }
    }
    
    static async deleteListing(listingId) {
        if (!confirm('Are you sure you want to delete this listing?')) {
            return;
        }
        
        try {
            const response = await fetch(`/donor/listing/${listingId}/delete`, {
                method: 'POST'
            });
            
            if (response.ok) {
                showNotification('Success', 'Listing deleted', 'success');
                setTimeout(() => window.location.reload(), 1500);
            } else {
                showNotification('Error', 'Failed to delete listing', 'danger');
            }
        } catch (error) {
            showNotification('Error', error.message, 'danger');
        }
    }
}

// NGO functions
class NGOUtils {
    static async requestFood(donationId, quantity) {
        try {
            const response = await fetch('/ngo/request/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    donation_id: donationId,
                    quantity: parseInt(quantity)
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showNotification('Success', data.message || 'Request created successfully', 'success');
                setTimeout(() => window.location.reload(), 1500);
                return true;
            } else {
                showNotification('Error', data.error || 'Failed to create request', 'danger');
                return false;
            }
        } catch (error) {
            showNotification('Error', error.message || 'Failed to create request', 'danger');
            return false;
        }
    }
    
    static async confirmDelivery(deliveryId) {
        try {
            const response = await fetch(`/ngo/delivery/${deliveryId}/confirm`, {
                method: 'POST'
            });
            
            if (response.ok) {
                showNotification('Success', 'Delivery confirmed', 'success');
                setTimeout(() => window.location.reload(), 1500);
            } else {
                showNotification('Error', 'Failed to confirm delivery', 'danger');
            }
        } catch (error) {
            showNotification('Error', error.message, 'danger');
        }
    }
    
    static async submitFeedback(deliveryId, feedbackType, rating, comment) {
        try {
            const response = await fetch(`/ngo/feedback/${deliveryId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    feedback_type: feedbackType,
                    rating: parseInt(rating),
                    comment: comment
                })
            });

            const data = await response.json();
            if (response.ok) {
                showNotification('Success', 'Feedback submitted', 'success');
                setTimeout(() => window.location.reload(), 1500);
            } else {
                showNotification('Error', data.error || 'Failed to submit feedback', 'danger');
            }
        } catch (error) {
            showNotification('Error', error.message, 'danger');
        }
    }
}

// Logistics functions
class LogisticsUtils {
    static async initializeDeliveryMap(deliveryId) {
        try {
            const response = await fetch(`/logistics/api/delivery/${deliveryId}/location`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            const data = await response.json();
            
            const map = initMap('delivery-map', {
                zoom: 13
            });
            
            if (!map) {
                showNotification('Error', 'Failed to initialize map', 'danger');
                return null;
            }
            
            const markers = [];
            
            // Add pickup location marker if coordinates are available
            if (data.pickup_location.latitude !== null && data.pickup_location.longitude !== null) {
                const pickupMarker = L.marker(
                    [data.pickup_location.latitude, data.pickup_location.longitude]
                ).addTo(map).bindPopup(`<strong>Pickup: ${data.pickup_location.name}</strong><br>${data.pickup_location.address}`);
                markers.push(pickupMarker);
            } else {
                console.warn('Pickup location coordinates are missing');
                showNotification('Warning', 'Pickup location coordinates are not available', 'warning');
            }
            
            // Add delivery location marker if coordinates are available
            if (data.delivery_location.latitude !== null && data.delivery_location.longitude !== null) {
                const deliveryMarker = L.marker(
                    [data.delivery_location.latitude, data.delivery_location.longitude]
                ).addTo(map).bindPopup(`<strong>Delivery: ${data.delivery_location.name}</strong><br>${data.delivery_location.address}`);
                markers.push(deliveryMarker);
            } else {
                console.warn('Delivery location coordinates are missing');
                showNotification('Warning', 'Delivery location coordinates are not available', 'warning');
            }
            
            // Fit bounds to show markers if any exist
            if (markers.length > 0) {
                const group = new L.featureGroup(markers);
                map.fitBounds(group.getBounds(), { padding: [50, 50] });
            } else {
                showNotification('Error', 'No valid location coordinates available for mapping', 'danger');
            }
            
            // Calculate and display distance between pickup and delivery
            if (data.pickup_location.latitude !== null && data.pickup_location.longitude !== null &&
                data.delivery_location.latitude !== null && data.delivery_location.longitude !== null) {
                try {
                    const distResult = await calculateDistance(
                        data.pickup_location.latitude, data.pickup_location.longitude,
                        data.delivery_location.latitude, data.delivery_location.longitude
                    );
                    const distEl = document.getElementById('delivery-distance');
                    if (distEl && distResult && distResult.distance_km !== undefined) {
                        distEl.textContent = distResult.distance_km.toFixed(2) + ' km';
                        distEl.parentElement.style.display = '';
                    }
                    // Draw a dashed line between the two points
                    L.polyline(
                        [[data.pickup_location.latitude, data.pickup_location.longitude],
                         [data.delivery_location.latitude, data.delivery_location.longitude]],
                        { color: '#e74c3c', weight: 2, dashArray: '8, 8' }
                    ).addTo(map);
                } catch (e) {
                    console.error('Distance calculation failed:', e);
                }
            }
            
            return map;
        } catch (error) {
            console.error('Error loading delivery map:', error);
            showNotification('Error', 'Failed to load delivery map', 'danger');
        }
    }
    
    static async confirmPickup(deliveryId, otp) {
        try {
            const response = await fetch(`/logistics/delivery/${deliveryId}/pickup`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ otp: otp || '' })
            });
            const data = await response.json();
            if (response.ok) {
                showNotification('Success', 'Pickup confirmed', 'success');
                setTimeout(() => window.location.reload(), 1500);
            } else {
                showNotification('Error', data.error || 'Failed to confirm pickup', 'danger');
            }
        } catch (error) {
            showNotification('Error', error.message, 'danger');
        }
    }
    
    static async confirmDelivery(deliveryId, otp) {
        try {
            const response = await fetch(`/logistics/delivery/${deliveryId}/deliver`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ otp: otp || '' })
            });
            const data = await response.json();
            if (response.ok) {
                showNotification('Success', 'Delivery confirmed', 'success');
                setTimeout(() => window.location.reload(), 1500);
            } else {
                showNotification('Error', data.error || 'Failed to confirm delivery', 'danger');
            }
        } catch (error) {
            showNotification('Error', error.message, 'danger');
        }
    }
}

// Admin functions
class AdminUtils {
    static async approveDonation(donationId, notes = '') {
        try {
            const response = await fetch(`/admin/donation/${donationId}/approve`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ notes })
            });
            
            if (response.ok) {
                showNotification('Success', 'Donation approved', 'success');
                setTimeout(() => window.location.reload(), 1500);
            } else {
                showNotification('Error', 'Failed to approve donation', 'danger');
            }
        } catch (error) {
            showNotification('Error', error.message, 'danger');
        }
    }
    
    static async rejectDonation(donationId, reason) {
        try {
            const response = await fetch(`/admin/donation/${donationId}/reject`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ reason })
            });
            
            if (response.ok) {
                showNotification('Success', 'Donation rejected', 'success');
                setTimeout(() => window.location.reload(), 1500);
            } else {
                showNotification('Error', 'Failed to reject donation', 'danger');
            }
        } catch (error) {
            showNotification('Error', error.message, 'danger');
        }
    }
    
    static async approveUser(userId) {
        try {
            const response = await fetch(`/admin/user/${userId}/approve`, {
                method: 'POST'
            });
            
            if (response.ok) {
                showNotification('Success', 'User approved', 'success');
                setTimeout(() => window.location.reload(), 1500);
            } else {
                showNotification('Error', 'Failed to approve user', 'danger');
            }
        } catch (error) {
            showNotification('Error', error.message, 'danger');
        }
    }
    
    static async deactivateUser(userId, reason) {
        try {
            const response = await fetch(`/admin/user/${userId}/deactivate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ reason })
            });
            
            if (response.ok) {
                showNotification('Success', 'User deactivated', 'success');
                setTimeout(() => window.location.reload(), 1500);
            } else {
                showNotification('Error', 'Failed to deactivate user', 'danger');
            }
        } catch (error) {
            showNotification('Error', error.message, 'danger');
        }
    }
    
    static async approveRequest(requestId, notes = '') {
        try {
            const response = await fetch(`/admin/request/${requestId}/approve`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ notes })
            });
            
            if (response.ok) {
                showNotification('Success', 'Request approved', 'success');
                setTimeout(() => window.location.reload(), 1500);
            } else {
                showNotification('Error', 'Failed to approve request', 'danger');
            }
        } catch (error) {
            showNotification('Error', error.message, 'danger');
        }
    }
    
    static async rejectRequest(requestId, reason) {
        try {
            const response = await fetch(`/admin/request/${requestId}/reject`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ reason })
            });
            
            if (response.ok) {
                showNotification('Success', 'Request rejected', 'success');
                setTimeout(() => window.location.reload(), 1500);
            } else {
                showNotification('Error', 'Failed to reject request', 'danger');
            }
        } catch (error) {
            showNotification('Error', error.message, 'danger');
        }
    }
    
    static async assignLogistics(deliveryId, logisticsId) {
        try {
            const response = await fetch(`/admin/delivery/${deliveryId}/assign`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ logistics_id: parseInt(logisticsId) })
            });
            
            if (response.ok) {
                showNotification('Success', 'Logistics assigned', 'success');
                setTimeout(() => window.location.reload(), 1500);
            } else {
                showNotification('Error', 'Failed to assign logistics', 'danger');
            }
        } catch (error) {
            showNotification('Error', error.message, 'danger');
        }
    }
}

// Feedback utilities for star rating and submission
class FeedbackUtils {
    static initStarRating(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        const stars = container.querySelectorAll('.star-btn');
        const ratingInput = container.querySelector('.feedback-rating-input');
        if (!ratingInput) return;

        stars.forEach(star => {
            star.addEventListener('click', () => {
                const val = parseInt(star.dataset.value);
                ratingInput.value = val;
                stars.forEach(s => {
                    const active = parseInt(s.dataset.value) <= val;
                    s.classList.toggle('active', active);
                    s.textContent = active ? '★' : '☆';
                });
            });
            star.addEventListener('mouseenter', () => {
                const val = parseInt(star.dataset.value);
                stars.forEach(s => {
                    const hovered = parseInt(s.dataset.value) <= val;
                    s.classList.toggle('hover', hovered);
                    s.textContent = hovered ? '★' : (s.classList.contains('active') ? '★' : '☆');
                });
            });
            star.addEventListener('mouseleave', () => {
                stars.forEach(s => {
                    s.classList.remove('hover');
                    s.textContent = s.classList.contains('active') ? '★' : '☆';
                });
            });
        });
    }

    static async submitDonorFeedback(listingId, feedbackType, containerId, deliveryId) {
        const container = document.getElementById(containerId);
        const rating = container.querySelector('.feedback-rating-input').value;
        const comment = container.querySelector('.feedback-comment').value;

        if (!rating || parseInt(rating) < 1) {
            showNotification('Error', 'Please select a rating', 'danger');
            return;
        }

        try {
            const body = { feedback_type: feedbackType, rating: parseInt(rating), comment };
            if (deliveryId) body.delivery_id = deliveryId;
            const response = await fetch(`/donor/feedback/${listingId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            const data = await response.json();
            if (response.ok) {
                showNotification('Success', 'Feedback submitted!', 'success');
                setTimeout(() => window.location.reload(), 1500);
            } else {
                showNotification('Error', data.error || 'Failed to submit feedback', 'danger');
            }
        } catch (error) {
            showNotification('Error', error.message, 'danger');
        }
    }

    static async submitNGOFeedback(deliveryId, feedbackType, containerId) {
        const container = document.getElementById(containerId);
        const rating = container.querySelector('.feedback-rating-input').value;
        const comment = container.querySelector('.feedback-comment').value;

        if (!rating || parseInt(rating) < 1) {
            showNotification('Error', 'Please select a rating', 'danger');
            return;
        }

        try {
            const response = await fetch(`/ngo/feedback/${deliveryId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ feedback_type: feedbackType, rating: parseInt(rating), comment })
            });
            const data = await response.json();
            if (response.ok) {
                showNotification('Success', 'Feedback submitted!', 'success');
                setTimeout(() => window.location.reload(), 1500);
            } else {
                showNotification('Error', data.error || 'Failed to submit feedback', 'danger');
            }
        } catch (error) {
            showNotification('Error', error.message, 'danger');
        }
    }

    static async submitVolunteerFeedback(deliveryId, feedbackType, containerId) {
        const container = document.getElementById(containerId);
        const rating = container.querySelector('.feedback-rating-input').value;
        const comment = container.querySelector('.feedback-comment').value;

        if (!rating || parseInt(rating) < 1) {
            showNotification('Error', 'Please select a rating', 'danger');
            return;
        }

        try {
            const response = await fetch(`/logistics/feedback/${deliveryId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ feedback_type: feedbackType, rating: parseInt(rating), comment })
            });
            const data = await response.json();
            if (response.ok) {
                showNotification('Success', 'Feedback submitted!', 'success');
                setTimeout(() => window.location.reload(), 1500);
            } else {
                showNotification('Error', data.error || 'Failed to submit feedback', 'danger');
            }
        } catch (error) {
            showNotification('Error', error.message, 'danger');
        }
    }
}

// Geocode address to coordinates using Google Maps API
async function geocodeAddress(address, city = '') {
    if (!GOOGLE_MAPS_KEY || GOOGLE_MAPS_KEY === 'YOUR_GOOGLE_MAPS_KEY_HERE') {
        console.warn('Google Maps API key not configured, skipping geocoding');
        return null;
    }
    
    try {
        const fullAddress = city ? `${address}, ${city}` : address;
        const response = await fetch(`https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(fullAddress)}&key=${GOOGLE_MAPS_KEY}`);
        const data = await response.json();
        
        if (data.status === 'OK' && data.results.length > 0) {
            const location = data.results[0].geometry.location;
            return {
                latitude: location.lat,
                longitude: location.lng
            };
        } else {
            console.warn('Geocoding failed:', data.status);
            return null;
        }
    } catch (error) {
        console.error('Geocoding error:', error);
        return null;
    }
}

// Reverse geocode coordinates to address using Google Maps API
async function reverseGeocode(lat, lng) {
    try {
        const response = await fetch(`https://maps.googleapis.com/maps/api/geocode/json?latlng=${lat},${lng}&key=${GOOGLE_MAPS_KEY}`);
        const data = await response.json();
        
        if (data.status === 'OK' && data.results.length > 0) {
            const result = data.results[0];
            
            // Extract address components
            let address = '';
            let city = '';
            let state = '';
            let country = '';
            
            for (const component of result.address_components) {
                if (component.types.includes('street_number')) {
                    address = component.long_name + ' ';
                }
                if (component.types.includes('route')) {
                    address += component.long_name;
                }
                if (component.types.includes('locality')) {
                    city = component.long_name;
                }
                if (component.types.includes('administrative_area_level_1')) {
                    state = component.long_name;
                }
                if (component.types.includes('country')) {
                    country = component.long_name;
                }
            }
            
            return {
                full_address: result.formatted_address,
                address: address.trim(),
                city: city,
                state: state,
                country: country
            };
        } else {
            console.error('Reverse geocoding failed:', data.status);
            return null;
        }
    } catch (error) {
        console.error('Reverse geocoding error:', error);
        return null;
    }
}
