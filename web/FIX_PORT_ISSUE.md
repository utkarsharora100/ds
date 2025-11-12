# 🔧 Fix: Port Permission Error (WinError 10013)

## Problem
Even in Administrator mode, you're getting:
```
PermissionError: [WinError 10013] An attempt was made to access a socket in a way forbidden by its access permissions
```

## ✅ Solution: Use Port 3000 with Localhost Binding

### Step 1: Open PowerShell as Administrator
(Right-click PowerShell → Run as Administrator)

### Step 2: Navigate to web directory
```powershell
cd "C:\Users\utkarsh\Desktop\New folder (3)\ds\web"
```

### Step 3: Start server on port 3000 (BIND TO LOCALHOST)
```powershell
python -m http.server 3000 --bind 127.0.0.1
```

**Expected output:**
```
Serving HTTP on 127.0.0.1 port 3000 (http://127.0.0.1:3000/) ...
```

### Step 4: Open in browser
```
http://localhost:3000
```

---

## Alternative Ports to Try

If port 3000 doesn't work, try these in order:

```powershell
# Port 5000
python -m http.server 5000 --bind 127.0.0.1

# Port 8888
python -m http.server 8888 --bind 127.0.0.1

# Port 9001
python -m http.server 9001 --bind 127.0.0.1

# Port 7000
python -m http.server 7000 --bind 127.0.0.1
```

---

## Why This Works

1. **Port 3000** is not in Windows reserved ranges
2. **`--bind 127.0.0.1`** binds only to localhost, avoiding network permission issues
3. This combination avoids both port reservation and network binding issues

---

## Quick Test Command

Copy and paste this entire block:

```powershell
cd "C:\Users\utkarsh\Desktop\New folder (3)\ds\web"
python -m http.server 3000 --bind 127.0.0.1
```

Then open: **http://localhost:3000**

---

## If Still Not Working

### Check Windows Firewall
```powershell
# Check firewall status
Get-NetFirewallProfile | Select-Object Name, Enabled
```

### Try Disabling Firewall Temporarily (for testing only)
```powershell
# Disable firewall (NOT RECOMMENDED for production)
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False

# Re-enable after testing
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
```

### Use Python's SimpleHTTPServer Alternative
If you have Python 2.7 installed:
```powershell
python -m SimpleHTTPServer 3000
```

### Check for Antivirus Blocking
- Temporarily disable antivirus
- Add Python to antivirus exceptions
- Check Windows Defender settings

---

## Verify Server is Running

In a **NEW PowerShell window** (regular, not admin):

```powershell
netstat -ano | findstr ":3000"
```

You should see output like:
```
TCP    127.0.0.1:3000         0.0.0.0:0              LISTENING       12345
```

---

## Complete Working Example

```powershell
# 1. Open PowerShell as Administrator
# 2. Run these commands:

cd "C:\Users\utkarsh\Desktop\New folder (3)\ds\web"
python --version
python -m http.server 3000 --bind 127.0.0.1
```

**Then in browser:** `http://localhost:3000`

---

## Notes

- **Keep PowerShell window open** while server runs
- **Press Ctrl+C** to stop server
- **Port 3000 is safe** - not in Windows reserved ranges
- **Binding to 127.0.0.1** limits access to localhost only (more secure)

