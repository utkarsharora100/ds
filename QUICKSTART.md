# 🚀 Quick Start Guide

Get the system running in **under 5 minutes**!

## Prerequisites Check

```bash
python --version  # Should be 3.8+
pip --version     # Should be installed
```

## Installation (One Command)

```bash
pip install -r requirements.txt
```

⏳ **Wait time:** ~2-3 minutes depending on your internet speed

---

## Running the System

### 🎯 Method 1: Automated Script (Easiest)

**Linux/Mac:**
```bash
./start.sh
```

**Windows:**
```bash
start.bat
```

Then choose option **1** (Full System)

---

### 🎯 Method 2: Manual (4 terminals)

**Terminal 1 - Application Server:**
```bash
python Application_server/Application_server.py
```

**Terminal 2, 3, 4 - Raft Nodes:**
```bash
python main.py node1  # Terminal 2
python main.py node2  # Terminal 3
python main.py node3  # Terminal 4
```

**Terminal 5 - GUI:**
```bash
python app.py
```

---

## Using the GUI

1. **Click the 3 "Start Node" buttons** → Wait for 🟢 indicators
2. **Login:**
   - Username: `admin`
   - Password: `123`
3. **Add movies** and **test the system**!

---

## Quick Tests

### Check Raft Status:
```bash
curl http://localhost:50051/status
curl http://localhost:50052/status
curl http://localhost:50053/status
```

One should show `"state": "leader"`

### Test Login:
```bash
curl -X POST http://127.0.0.1:9000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "123"}'
```

---

## Troubleshooting

### "Port already in use"
```bash
./start.sh  # Choose option 6 to stop all
# OR manually:
lsof -ti:9000,50051,50052,50053 | xargs kill -9
```

### "Module not found"
```bash
pip install -r requirements.txt
```

### GUI won't open (Linux)
```bash
sudo apt-get install python3-tk  # Ubuntu/Debian
```

---

## What You Should See

✅ Application Server running on port 9000  
✅ Three Raft nodes on ports 50051-50053  
✅ One node elected as LEADER  
✅ GUI opens with login screen  

---

## Next Steps

📖 Read the full [README.md](README.md) for detailed architecture and API documentation

🧪 Explore the test files in `tests/` directory

🎓 Learn about [Raft Consensus](https://raft.github.io/)

---

**Questions?** Check the Troubleshooting section in README.md

**Ready to go!** 🎉
