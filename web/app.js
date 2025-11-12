// Global state
let currentUser = null;
let authToken = null;
let currentBooking = null;

// API Base URL - Change this to your server IP when needed
// Backend server is running on port 9100 in this session
const API_BASE = 'http://127.0.0.1:9100';

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
    // Include username in the request id so bookings can be correlated to users
    const userPrefix = currentUser ? currentUser : 'anon';
    return `${userPrefix}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
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
                // booking object format: {"id":..., "data": {"user":..., ...}}
                const bookingId = booking.id || booking.requestId || '';
                const bookingData = booking.data || {};
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>${(bookingId || '').toString().substring(0, 12)}...</td>
                    <td>${bookingData.user || bookingData.username || 'N/A'}</td>
                    <td>${bookingData.movie || ''}</td>
                    <td>${bookingData.city || ''}</td>
                    <td>${bookingData.seats || ''}</td>
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


// ---------------------- RAFT LOGS & SIMULATION ----------------------
async function refreshRaftLogs() {
    const out = document.getElementById('raftLogs');
    out.textContent = 'Loading raft logs...';
    try {
        const response = await fetch(`${API_BASE}/admin/raft_logs?token=${authToken}`);
        const data = await response.json();
        if (data.status === 'success') {
            const logs = data.logs || [];
            out.textContent = logs.map(l => `[${l.id}] term=${l.term} ${l.created_at} -> ${l.command}`).join('\n');
        } else {
            out.textContent = 'Failed to load raft logs';
        }
    } catch (err) {
        out.textContent = `Error fetching raft logs: ${err.message}`;
    }
}

async function simulateClients() {
    const num = parseInt(document.getElementById('simNumClients').value || '10');
    const movie = document.getElementById('simMovie').value || '';
    const seats = parseInt(document.getElementById('simSeatsEach').value || '1');

    if (!confirm(`Run simulation with ${num} clients booking ${seats} seats each for '${movie}'?`)) return;

    try {
        const resp = await fetch(`${API_BASE}/admin/simulate_clients`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: authToken, num_clients: num, movie: movie, seats_per_client: seats })
        });
        const data = await resp.json();
        if (data.status === 'success') {
            const s = data.summary || {};
            showToast(`Simulation finished: ${s.success}/${s.total} succeeded`, 'info');
            // refresh movies and bookings to reflect changes
            refreshAdminMovies();
            refreshAdminBookings();
            refreshRaftLogs();
        } else {
            showToast(data.message || 'Simulation failed', 'error');
        }
    } catch (err) {
        showToast('Could not contact server for simulation', 'error');
        console.error('Simulate clients error:', err);
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
    
    // Use server-side aggregated health endpoint to avoid CORS issues with raft nodes
    try {
        // admin-only endpoint requires token
        const resp = await fetch(`${API_BASE}/admin/check_cluster_health?token=${authToken}`);
        const data = await resp.json();
        if (data.status === 'success') {
            const services = data.services || {};
            for (const [name, info] of Object.entries(services)) {
                if (info.ok) {
                    resultsDiv.textContent += `✓ ${name}: OK\n`;
                } else {
                    resultsDiv.textContent += `❌ ${name}: FAILED (${info.error || info.status_code || 'unknown'})\n`;
                }
            }
        } else {
            resultsDiv.textContent += '❌ Cluster health check failed on server\n';
        }
    } catch (err) {
        resultsDiv.textContent += `❌ Health check request failed: ${err.message}\n`;
    }
    
    showToast('Health check complete', 'info');
}

// ---------------- Live Health Polling ----------------
let liveHealthIntervalId = null;

function renderLiveHealth(data) {
    const summaryEl = document.getElementById('liveHealthSummary');
    const detailsEl = document.getElementById('liveHealthDetails');
    if (!data || data.status !== 'success') {
        summaryEl.textContent = 'Live health failed to fetch.';
        detailsEl.textContent = JSON.stringify(data, null, 2);
        return;
    }
    const services = data.services || {};
    let okCount = 0, total = 0;
    const lines = [];
    for (const [name, info] of Object.entries(services)) {
        total++;
        if (info.ok) okCount++;
        lines.push(`${name}: ${info.ok ? 'OK' : 'FAILED'} ${info.ok ? '' : ('(' + (info.error || info.status_code || '') + ')')}`);
    }
    summaryEl.textContent = `${okCount}/${total} services healthy`;
    detailsEl.textContent = lines.join('\n');
}

async function fetchLiveHealth() {
    try {
        const resp = await fetch(`${API_BASE}/admin/check_cluster_health?token=${authToken}`);
        const data = await resp.json();
        renderLiveHealth(data);
    } catch (err) {
        renderLiveHealth({ status: 'error', error: err.message });
    }
}

function toggleLiveHealth() {
    const btn = document.getElementById('toggleLiveHealthBtn');
    const intervalInput = document.getElementById('liveInterval');
    if (!liveHealthIntervalId) {
        const intervalSec = Math.max(1, parseInt(intervalInput.value || '5'));
        fetchLiveHealth(); // immediate
        liveHealthIntervalId = setInterval(fetchLiveHealth, intervalSec * 1000);
        btn.textContent = 'Stop Live Health';
    } else {
        clearInterval(liveHealthIntervalId);
        liveHealthIntervalId = null;
        btn.textContent = 'Start Live Health';
        document.getElementById('liveHealthSummary').textContent = 'No live health running.';
        document.getElementById('liveHealthDetails').textContent = '';
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
            // Filter bookings client-side to ensure only this user's bookings are shown
            const allBookings = data.data || [];
            const visible = allBookings.filter(b => {
                const bdata = b.data || {};
                // booking stored user may be in bdata.user or bdata.username
                return (bdata.user === currentUser) || (bdata.username === currentUser);
            });

            if (visible.length > 0) {
                tbody.innerHTML = '';
                visible.forEach(booking => {
                    const bookingId = booking.id || booking.requestId || '';
                    const bookingData = booking.data || {};
                    const row = tbody.insertRow();
                    row.innerHTML = `
                        <td>${(bookingId || '').toString().substring(0, 12)}...</td>
                        <td>${bookingData.movie || ''}</td>
                        <td>${bookingData.city || ''}</td>
                        <td>${bookingData.seats || ''}</td>
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
