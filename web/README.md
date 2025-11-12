# Web Frontend for Movie Booking System

A modern, responsive web-based frontend for the Distributed Movie Booking System.

## Features

- 🎨 **Modern Dark Theme UI** - Beautiful gradient design with smooth animations
- 📱 **Fully Responsive** - Works on desktop, tablet, and mobile devices
- 🔐 **User Authentication** - Login and registration functionality
- 👤 **User Dashboard** - Browse movies, book tickets, view bookings
- 👨‍💼 **Admin Dashboard** - Add movies, manage database, test system
- 🎬 **Real-time Updates** - Fetch latest data from backend API
- ⚡ **Fast & Lightweight** - Pure HTML/CSS/JavaScript, no frameworks needed

## Quick Start

### Option 1: Use Combined Docker Setup (Recommended)

The combined Docker setup includes the web frontend. Just start the services:

```bash
docker compose -f docker-compose.combined.yml up -d --build
```

Then access: **http://localhost:3000**

### Option 2: Local Server (Development)

1. **Ensure backend services are running:**
   ```bash
   docker compose ps  # Verify all services are up
   ```

2. **Start a simple HTTP server:**
   ```bash
   cd web
   
   # Linux/Mac - Use port 8080
   python3 -m http.server 8080
   
   # Windows - Use port 3000 (8080 is reserved by Windows)
   python -m http.server 3000 --bind 127.0.0.1
   ```

3. **Open in browser:**
   ```
   # Linux/Mac
   http://localhost:8080
   
   # Windows
   http://localhost:3000
   ```

**⚠️ Windows Users:** Port 8080 is reserved by Windows. Use port 3000, 8000, or 5000 instead.

### Option 3: Remote Access via SSH Port Forwarding

If accessing from a remote machine:

1. **SSH with port forwarding (from your LOCAL machine):**
   ```bash
   ssh -L 8080:localhost:8080 \
       -L 9000:localhost:9000 \
       -L 8500:localhost:8500 \
       -L 50051:localhost:50051 \
       -L 50052:localhost:50052 \
       -L 50053:localhost:50053 \
       aniket@YOUR_SERVER_IP
   ```

2. **On the server, start the web server:**
   ```bash
   cd /home/aniket/study/ds/web
   python3 -m http.server 8080
   ```

3. **On your LOCAL machine, open browser:**
   ```
   http://localhost:8080
   ```

### Option 3: Direct File Access

Simply open `index.html` in your browser (only works if backend is on localhost).

## File Structure

```
web/
├── index.html    # Main HTML structure
├── styles.css    # Styling and themes
├── app.js        # Frontend logic and API calls
└── README.md     # This file
```

## Configuration

### Change Backend URL

If your backend is NOT on `localhost:9000`, edit `app.js`:

```javascript
// Line 6 in app.js
const API_BASE = 'http://YOUR_SERVER_IP:9000';
```

### CORS Configuration

If you encounter CORS errors, you may need to configure your backend to allow cross-origin requests. The FastAPI server should already have CORS middleware enabled.

## User Guide

### Login Credentials

**Default Admin:**
- Username: `admin`
- Password: `123`

**Create New User:**
Click "Register New Account" on the login page.

### User Features

1. **Browse Movies** - View all available movies with seat availability
2. **Book Tickets** - Click "Book Now" and select number of seats
3. **View Bookings** - See all your past bookings in the right panel
4. **Refresh Data** - Update movies and bookings with latest data

### Admin Features

1. **Add Movies** - Add new movies with city and seat count
2. **Load Sample Data** - Populate database with 15 sample movies
3. **Clear Database** - Remove all movies and bookings (with confirmation)
4. **Test LLM** - Verify LLM service is working
5. **Check Health** - Test all system services (app, LLM, Raft nodes)

## API Endpoints Used

### Authentication
- `POST /login` - User login
- `POST /register` - User registration

### Data
- `GET /data/movies` - Fetch all movies
- `GET /data/bookings` - Fetch user bookings
- `POST /add_movie` - Add new movie (admin)

### Admin
- `POST /admin/load_sample_data` - Load sample movies
- `POST /admin/clear_database` - Clear all data

### Business
- `POST /business` - Book movie tickets

### Testing
- `GET /health` - App server health
- `GET http://localhost:8500/health` - LLM health
- `POST http://localhost:8500/ask` - Test LLM question
- `GET http://localhost:50051/status` - Raft node status

## Browser Compatibility

- ✅ Chrome/Chromium (Recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ⚠️ Internet Explorer (Not Supported)

## Troubleshooting

### Windows: Port Permission Error (WinError 10013)

**Error:** `OSError: [WinError 10013] An attempt was made to access a socket in a way forbidden by its access permissions`

**Cause:** Port 8080 is in Windows reserved port range (7985-8084).

**Solution: Use port 3000 with localhost binding**
```powershell
cd web
python -m http.server 3000 --bind 127.0.0.1
# Then open http://localhost:3000
```

**Alternative ports:**
```powershell
python -m http.server 8000 --bind 127.0.0.1   # http://localhost:8000
python -m http.server 5000 --bind 127.0.0.1   # http://localhost:5000
```

### "Could not connect to server"

**Cause:** Backend services not running or wrong URL.

**Solution:**
```bash
# Check if services are running
sudo docker compose ps

# Start services if needed
sudo docker compose up -d

# Verify app server is responding
curl http://localhost:9000/health
```

### CORS Errors

**Cause:** Browser blocking cross-origin requests.

**Solution:** Use same origin (recommended) or configure backend CORS settings.

### Port Forwarding Not Working

**Cause:** SSH tunnel disconnected or ports already in use.

**Solution:**
```bash
# Check if ports are listening
ss -tuln | grep -E "8080|9000|8500"

# Reconnect SSH with port forwarding
ssh -L 8080:localhost:8080 -L 9000:localhost:9000 ...
```

### Movies Not Loading

**Cause:** No movies in database.

**Solution:** Login as admin and click "Load Sample Movies".

## Development

### Modify Styles

Edit `styles.css` to change colors, fonts, or layout.

**Color Scheme Variables:**
```css
--primary-color: #2563eb;     /* Blue */
--success-color: #16a34a;     /* Green */
--danger-color: #dc2626;      /* Red */
--bg-dark: #0f172a;           /* Dark background */
--bg-card: #1e293b;           /* Card background */
```

### Add New Features

Edit `app.js` to add new functionality or API calls.

### HTML Structure

Edit `index.html` to modify page layout or add new sections.

## Security Notes

- 🔒 Tokens are stored in memory only (not persisted)
- 🔒 SSH port forwarding encrypts all traffic
- ⚠️ This is a demo application - use HTTPS in production
- ⚠️ Implement proper token storage for production use

## Performance

- **Load Time:** < 1 second
- **API Response:** < 100ms (local network)
- **Bundle Size:** ~15KB total (HTML + CSS + JS)
- **No Dependencies:** Zero external libraries

## License

Part of the Distributed Movie Booking System project.
