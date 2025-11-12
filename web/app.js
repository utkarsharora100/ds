// Global state
let currentUser = null;
let authToken = null;
let currentBooking = null;

// API Base URL - Change this to your server IP when needed
const API_BASE = 'http://127.0.0.1:9000';

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

function showPage(pageId) {
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    document.getElementById(pageId).classList.add('active');
}

function generateRequestId() {
    return 'req-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
}

// ============================================================================
// NAVIGATION
// ============================================================================

function showLogin() {
    showPage('loginPage');
}

function showRegister() {
    showPage('registerPage');
}

function logout() {
    currentUser = null;
    authToken = null;
    showLogin();
    showToast('Logged out successfully', 'info');
}

// ============================================================================
// AUTHENTICATION
// ============================================================================

document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            currentUser = username;
            authToken = data.token;
            
            if (username === 'admin') {
                showPage('adminPage');
                refreshAdminMovies();
                refreshAdminBookings();
            } else {
                document.getElementById('userWelcome').textContent = `Welcome, ${username}! 🎬`;
                showPage('userPage');
                refreshUserMovies();
                refreshBookings();
            }
            
            showToast(`Welcome back, ${username}!`, 'success');
        } else {
            showToast(data.message || 'Login failed', 'error');
        }
    } catch (error) {
        showToast('Could not connect to server', 'error');
        console.error('Login error:', error);
    }
});

document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('regUsername').value;
    const password = document.getElementById('regPassword').value;
    const confirmPassword = document.getElementById('regConfirmPassword').value;
    
    if (password !== confirmPassword) {
        showToast('Passwords do not match', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showToast('Registration successful! Please login.', 'success');
            showLogin();
            document.getElementById('registerForm').reset();
        } else {
            showToast(data.message || 'Registration failed', 'error');
        }
    } catch (error) {
        showToast('Could not connect to server', 'error');
        console.error('Registration error:', error);
    }
});

// ============================================================================
// ADMIN FUNCTIONS
// ============================================================================

document.getElementById('addMovieForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const movie = document.getElementById('movieName').value;
    const city = document.getElementById('movieCity').value;
    const seats = parseInt(document.getElementById('movieSeats').value);
    
    try {
        const response = await fetch(`${API_BASE}/add_movie`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: authToken, movie, city, seats })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showToast(`Movie "${movie}" added successfully!`, 'success');
            document.getElementById('addMovieForm').reset();
            document.getElementById('movieSeats').value = '50'; // Reset to default
            refreshAdminMovies();
        } else {
            showToast(data.message || 'Failed to add movie', 'error');
        }
    } catch (error) {
        showToast('Could not connect to server', 'error');
        console.error('Add movie error:', error);
    }
});

async function refreshAdminMovies() {
    const tbody = document.getElementById('adminMoviesBody');
    tbody.innerHTML = '<tr><td colspan="3" class="loading">Loading movies...</td></tr>';
    
    try {
        const response = await fetch(`${API_BASE}/data/movies?token=${authToken}`);
        const data = await response.json();
        
        if (data.status === 'success' && data.data.length > 0) {
            tbody.innerHTML = '';
            data.data.forEach(item => {
                const movieData = item.data;
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>${movieData.movie}</td>
                    <td>${movieData.city}</td>
                    <td>${movieData.seats}</td>
                `;
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="3" class="loading">No movies available</td></tr>';
        }
    } catch (error) {
        tbody.innerHTML = '<tr><td colspan="3" class="loading">Error loading movies</td></tr>';
        console.error('Refresh movies error:', error);
    }
}

async function loadSampleMovies() {
    try {
        const response = await fetch(`${API_BASE}/admin/load_sample_data`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: authToken })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            const loaded = data.loaded || {};
            showToast(`Loaded ${loaded.movies || 0} sample movies!`, 'success');
            refreshAdminMovies();
        } else {
            showToast(data.message || 'Failed to load sample data', 'error');
        }
    } catch (error) {
        showToast('Could not connect to server', 'error');
        console.error('Load sample error:', error);
    }
}

async function clearDatabase() {
    if (!confirm('⚠️ This will DELETE all movies and bookings!\n\nAre you sure you want to continue?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/admin/clear_database`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: authToken })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            const cleared = data.cleared || {};
            showToast(`Cleared ${cleared.movies || 0} movies and ${cleared.bookings || 0} bookings`, 'info');
            refreshAdminMovies();
            refreshAdminBookings();
        } else {
            showToast(data.message || 'Failed to clear database', 'error');
        }
    } catch (error) {
        showToast('Could not connect to server', 'error');
        console.error('Clear database error:', error);
    }
}

async function refreshAdminBookings() {
    const tbody = document.getElementById('adminBookingsBody');
    tbody.innerHTML = '<tr><td colspan="5" class="loading">Loading bookings...</td></tr>';
    
    try {
        const response = await fetch(`${API_BASE}/data/bookings?token=${authToken}`);
        const data = await response.json();
        
        if (data.status === 'success' && data.data.length > 0) {
            tbody.innerHTML = '';
            data.data.forEach(booking => {
                const bookingData = booking.data;
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>${booking.requestId.substring(0, 8)}...</td>
                    <td>${bookingData.username || 'N/A'}</td>
                    <td>${bookingData.movie}</td>
                    <td>${bookingData.city}</td>
                    <td>${bookingData.seats}</td>
                `;
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="5" class="loading">No bookings yet</td></tr>';
        }
    } catch (error) {
        tbody.innerHTML = '<tr><td colspan="5" class="loading">Error loading bookings</td></tr>';
        console.error('Refresh admin bookings error:', error);
    }
}

async function testLLM() {
    const resultsDiv = document.getElementById('testResults');
    resultsDiv.textContent = 'Testing LLM service...\n';
    
    try {
        // Test health endpoint
        resultsDiv.textContent += '\n1. Checking LLM health...\n';
        const healthResponse = await fetch('http://127.0.0.1:8500/health');
        const healthData = await healthResponse.json();
        resultsDiv.textContent += `✓ Status: ${healthData.status}\n`;
        resultsDiv.textContent += `✓ Model: ${healthData.model}\n`;
        resultsDiv.textContent += `✓ Model Loaded: ${healthData.model_loaded}\n`;
        
        // Test question endpoint
        resultsDiv.textContent += '\n2. Testing question endpoint...\n';
        const askResponse = await fetch('http://127.0.0.1:8500/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: 'How do I book a movie ticket?' })
        });
        const askData = await askResponse.json();
        resultsDiv.textContent += `✓ Response: ${askData.answer}\n`;
        
        showToast('LLM service is working!', 'success');
    } catch (error) {
        resultsDiv.textContent += `\n❌ Error: ${error.message}\n`;
        showToast('LLM service test failed', 'error');
    }
}

async function checkHealth() {
    const resultsDiv = document.getElementById('testResults');
    resultsDiv.textContent = 'Checking system health...\n\n';
    
    const services = [
        { name: 'App Server', url: `${API_BASE}/health` },
        { name: 'LLM Server', url: 'http://127.0.0.1:8500/health' },
        { name: 'Raft Node 1', url: 'http://127.0.0.1:50051/status' },
        { name: 'Raft Node 2', url: 'http://127.0.0.1:50052/status' },
        { name: 'Raft Node 3', url: 'http://127.0.0.1:50053/status' }
    ];
    
    for (const service of services) {
        try {
            const response = await fetch(service.url);
            const data = await response.json();
            resultsDiv.textContent += `✓ ${service.name}: OK\n`;
        } catch (error) {
            resultsDiv.textContent += `❌ ${service.name}: FAILED\n`;
        }
    }
    
    showToast('Health check complete', 'info');
}

// ============================================================================
// USER FUNCTIONS
// ============================================================================

async function refreshUserMovies() {
    const tbody = document.getElementById('userMoviesBody');
    tbody.innerHTML = '<tr><td colspan="4" class="loading">Loading movies...</td></tr>';
    
    try {
        const response = await fetch(`${API_BASE}/data/movies?token=${authToken}`);
        const data = await response.json();
        
        if (data.status === 'success' && data.data.length > 0) {
            tbody.innerHTML = '';
            data.data.forEach(item => {
                const movieData = item.data;
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>${movieData.movie}</td>
                    <td>${movieData.city}</td>
                    <td>${movieData.seats}</td>
                    <td>
                        <button class="btn btn-primary btn-small" 
                                onclick='openBookingModal(${JSON.stringify(movieData)})'>
                            Book Now
                        </button>
                    </td>
                `;
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="4" class="loading">No movies available</td></tr>';
        }
    } catch (error) {
        tbody.innerHTML = '<tr><td colspan="4" class="loading">Error loading movies</td></tr>';
        console.error('Refresh movies error:', error);
    }
}

async function refreshBookings() {
    const tbody = document.getElementById('bookingsBody');
    tbody.innerHTML = '<tr><td colspan="4" class="loading">Loading bookings...</td></tr>';
    
    try {
        const response = await fetch(`${API_BASE}/data/bookings?token=${authToken}`);
        const data = await response.json();
        
        if (data.status === 'success') {
            if (data.data && data.data.length > 0) {
                tbody.innerHTML = '';
                data.data.forEach(booking => {
                    const bookingData = booking.data;
                    const row = tbody.insertRow();
                    row.innerHTML = `
                        <td>${booking.requestId.substring(0, 8)}...</td>
                        <td>${bookingData.movie}</td>
                        <td>${bookingData.city}</td>
                        <td>${bookingData.seats}</td>
                    `;
                });
            } else {
                tbody.innerHTML = '<tr><td colspan="4" class="loading">No bookings yet</td></tr>';
            }
        } else {
            // If bookings endpoint returns error, show empty state instead of error
            tbody.innerHTML = '<tr><td colspan="4" class="loading">No bookings yet</td></tr>';
        }
    } catch (error) {
        // Silently handle error - user just hasn't made bookings yet
        tbody.innerHTML = '<tr><td colspan="4" class="loading">No bookings yet</td></tr>';
        console.log('Bookings not available yet:', error);
    }
}

function openBookingModal(movieData) {
    currentBooking = movieData;
    document.getElementById('bookingMovieInfo').textContent = 
        `Movie: ${movieData.movie} | City: ${movieData.city} | Available: ${movieData.seats} seats`;
    document.getElementById('bookingModal').style.display = 'block';
}

function closeBookingModal() {
    document.getElementById('bookingModal').style.display = 'none';
    document.getElementById('bookingForm').reset();
    currentBooking = null;
}

document.getElementById('bookingForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const seats = parseInt(document.getElementById('seatsToBook').value);
    
    if (!currentBooking) {
        showToast('No movie selected', 'error');
        return;
    }
    
    try {
        const payload = {
            requestId: generateRequestId(),
            payload: {
                type: 'book_seat',
                data: {
                    movie: currentBooking.movie,
                    city: currentBooking.city,
                    seats: seats
                }
            },
            context: { token: authToken }
        };
        
        const response = await fetch(`${API_BASE}/business`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showToast(`Successfully booked ${seats} seat(s) for "${currentBooking.movie}"!`, 'success');
            closeBookingModal();
            refreshUserMovies();
            refreshBookings();
        } else {
            showToast(data.message || 'Booking failed', 'error');
        }
    } catch (error) {
        showToast('Could not connect to server', 'error');
        console.error('Booking error:', error);
    }
});

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('bookingModal');
    if (event.target === modal) {
        closeBookingModal();
    }
}

// ============================================================================
// INITIALIZATION
// ============================================================================

// Show login page on load
showLogin();
