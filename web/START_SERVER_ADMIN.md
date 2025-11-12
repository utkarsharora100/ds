# 🚀 Starting Web Server in Administrator Mode (Windows)

## Step-by-Step Guide

### Step 1: Open PowerShell as Administrator

**Method A: From Start Menu**
1. Press `Windows Key` or click Start button
2. Type `PowerShell`
3. Right-click on **"Windows PowerShell"**
4. Select **"Run as Administrator"**
5. Click **"Yes"** when prompted by User Account Control (UAC)

**Method B: From Run Dialog**
1. Press `Windows Key + R`
2. Type: `powershell`
3. Press `Ctrl + Shift + Enter` (this opens as admin)
4. Click **"Yes"** when prompted

**Method C: From File Explorer**
1. Navigate to: `C:\Users\utkarsh\Desktop\New folder (3)\ds\web`
2. Click in the address bar
3. Type: `powershell`
4. Press `Ctrl + Shift + Enter`
5. Click **"Yes"** when prompted

---

### Step 2: Verify You're in Administrator Mode

In PowerShell, you should see:
```
PS C:\WINDOWS\system32>
```

If you see `system32`, you're in admin mode. ✅

---

### Step 3: Navigate to Web Directory

```powershell
cd "C:\Users\utkarsh\Desktop\New folder (3)\ds\web"
```

Verify you're in the right place:
```powershell
dir
```

You should see:
- `index.html`
- `app.js`
- `styles.css`
- `README.md`

---

### Step 4: Check Python Installation

```powershell
python --version
```

OR

```powershell
python3 --version
```

**Expected output:** `Python 3.x.x`

If you get an error, Python is not installed or not in PATH.

---

### Step 5: Try Port 8080 (Now with Admin Rights)

```powershell
python -m http.server 8080
```

**OR if python3 is the command:**

```powershell
python3 -m http.server 8080
```

**Expected output:**
```
Serving HTTP on 0.0.0.0 port 8080 (http://0.0.0.0:8080/) ...
```

**If it works:** ✅ Great! Open `http://localhost:8080` in your browser.

**If it still fails:** Continue to Step 6.

---

### Step 6: If Port 8080 Still Fails, Use Port 8000

Stop the previous command (press `Ctrl+C` if running), then:

```powershell
python -m http.server 8000
```

**Expected output:**
```
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

**Open in browser:** `http://localhost:8000`

---

### Step 7: Verify Server is Running

**In a NEW PowerShell window (regular, not admin):**

```powershell
netstat -ano | findstr :8080
```

OR for port 8000:

```powershell
netstat -ano | findstr :8000
```

You should see output showing the port is listening.

---

### Step 8: Open in Browser

Open your web browser and go to:

- **If using port 8080:** `http://localhost:8080`
- **If using port 8000:** `http://localhost:8000`

You should see the Movie Booking System login page.

---

## 🔧 Troubleshooting

### Error: "python is not recognized"

**Solution:**
1. Python might not be installed
2. Python might not be in PATH

**Check Python location:**
```powershell
where python
where python3
```

**If Python is installed but not found:**
- Reinstall Python and check "Add Python to PATH" during installation
- Or use full path: `C:\Python312\python.exe -m http.server 8000`

### Error: "Port already in use"

**Check what's using the port:**
```powershell
netstat -ano | findstr :8080
```

**Kill the process (replace PID with actual number):**
```powershell
taskkill /PID <PID> /F
```

### Error: Still getting WinError 10013

**Even in admin mode, try:**
1. Use a different port (8000, 3000, 5000, 8888)
2. Check Windows Firewall settings
3. Check if antivirus is blocking the port

**Check reserved ports:**
```powershell
netsh interface ipv4 show excludedportrange protocol=tcp
```

---

## ✅ Quick Command Summary

**Full command sequence (copy-paste ready):**

```powershell
# 1. Navigate to web directory
cd "C:\Users\utkarsh\Desktop\New folder (3)\ds\web"

# 2. Start server on port 8000 (recommended)
python -m http.server 8000

# OR try port 8080 if you need it
python -m http.server 8080
```

---

## 🎯 Alternative: Use Python's Built-in Server with Specific Host

If you still have issues, try binding to localhost only:

```powershell
python -m http.server 8000 --bind 127.0.0.1
```

This binds only to localhost and might avoid permission issues.

---

## 📝 Notes

- **Keep the PowerShell window open** while the server is running
- **Press Ctrl+C** to stop the server
- **The server runs until you stop it** - you can minimize the window
- **Each user session needs its own server** - if you close PowerShell, the server stops

---

## 🆘 Still Not Working?

1. **Check if backend services are running:**
   ```powershell
   docker compose ps
   ```

2. **Try a completely different port:**
   ```powershell
   python -m http.server 3000
   # Then open: http://localhost:3000
   ```

3. **Check Windows Event Viewer** for detailed error messages

4. **Try running from a different directory** to rule out path issues

