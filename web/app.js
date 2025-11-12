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
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.status === 'success') {
            const loaded = data.loaded || {};
            showToast(`Loaded ${loaded.movies || 0} sample movies!`, 'success');
            // Wait a bit for data to be committed
            setTimeout(() => {
                refreshAdminMovies();
            }, 500);
        } else {
            showToast(data.message || 'Failed to load sample data', 'error');
            console.error('Load sample error response:', data);
        }
    } catch (error) {
        showToast(`Could not connect to server: ${error.message}`, 'error');
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
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.status === 'success') {
            const cleared = data.cleared || {};
            showToast(`Cleared ${cleared.movies || 0} movies and ${cleared.bookings || 0} bookings`, 'info');
            // Wait a bit for data to be committed
            setTimeout(() => {
                refreshAdminMovies();
                refreshAdminBookings();
            }, 500);
        } else {
            showToast(data.message || 'Failed to clear database', 'error');
            console.error('Clear database error response:', data);
        }
    } catch (error) {
        showToast(`Could not connect to server: ${error.message}`, 'error');
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
        // Test health endpoint via proxy
        resultsDiv.textContent += '\n1. Checking LLM health...\n';
        const healthResponse = await fetch(`${API_BASE}/proxy/llm/health`);
        const healthData = await healthResponse.json();
        
        if (healthData.status === 'error') {
            resultsDiv.textContent += `❌ LLM Server: ${healthData.message}\n`;
            showToast('LLM service is not available', 'error');
            return;
        }
        
        resultsDiv.textContent += `✓ Status: ${healthData.status || 'OK'}\n`;
        resultsDiv.textContent += `✓ Model: ${healthData.model || 'N/A'}\n`;
        resultsDiv.textContent += `✓ Model Loaded: ${healthData.model_loaded ? 'Yes' : 'No'}\n`;
        
        // Test question endpoint via proxy
        resultsDiv.textContent += '\n2. Testing question endpoint...\n';
        const askResponse = await fetch(`${API_BASE}/proxy/llm/ask`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: 'How do I book a movie ticket?' })
        });
        const askData = await askResponse.json();
        
        if (askData.status === 'error') {
            resultsDiv.textContent += `❌ Error: ${askData.answer}\n`;
        } else {
            resultsDiv.textContent += `✓ Response: ${askData.answer || askData.response || 'N/A'}\n`;
        }
        
        showToast('LLM service test complete!', 'success');
    } catch (error) {
        resultsDiv.textContent += `\n❌ Error: ${error.message}\n`;
        showToast('LLM service test failed', 'error');
        console.error('LLM test error:', error);
    }
}

async function checkHealth() {
    const resultsDiv = document.getElementById('testResults');
    resultsDiv.textContent = 'Checking system health...\n\n';
    
    try {
        // Use the combined health check endpoint
        const response = await fetch(`${API_BASE}/admin/health/all`);
        const data = await response.json();
        
        // App Server
        if (data.app_server && data.app_server.status === 'healthy') {
            resultsDiv.textContent += `✓ App Server: OK\n`;
        } else {
            resultsDiv.textContent += `❌ App Server: FAILED\n`;
        }
        
        // LLM Server
        if (data.llm_server) {
            if (data.llm_server.status === 'error') {
                resultsDiv.textContent += `❌ LLM Server: ${data.llm_server.message || 'Unreachable'}\n`;
            } else {
                resultsDiv.textContent += `✓ LLM Server: OK (Model: ${data.llm_server.model || 'N/A'})\n`;
            }
        } else {
            resultsDiv.textContent += `❌ LLM Server: FAILED\n`;
        }
        
        // Raft Nodes
        for (let i = 1; i <= 3; i++) {
            const nodeKey = `raft_node_${i}`;
            if (data[nodeKey]) {
                if (data[nodeKey].status === 'error') {
                    resultsDiv.textContent += `❌ Raft Node ${i}: ${data[nodeKey].message || 'Unreachable'}\n`;
                } else {
                    const state = data[nodeKey].state || 'unknown';
                    resultsDiv.textContent += `✓ Raft Node ${i}: OK (State: ${state})\n`;
                }
            } else {
                resultsDiv.textContent += `❌ Raft Node ${i}: FAILED\n`;
            }
        }
        
        showToast('Health check complete', 'info');
    } catch (error) {
        resultsDiv.textContent += `❌ Error checking health: ${error.message}\n`;
        showToast('Health check failed', 'error');
        console.error('Health check error:', error);
    }
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
