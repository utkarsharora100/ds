# 🚀 Getting Started with Distributed Movie Booking System

Welcome! This guide will help you get the system up and running in minutes.

## 📚 Documentation Index

| Document | Purpose |
|----------|---------|
| **[README.md](README.md)** | Complete system overview and detailed instructions |
| **[QUICKSTART.md](QUICKSTART.md)** | Fast track to running the system (< 5 minutes) |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | Technical architecture and design details |
| **[CONTRIBUTING.md](CONTRIBUTING.md)** | How to contribute to the project |
| **This file** | Navigation and first steps |

---

## 🎯 Choose Your Path

### Path 1: Just Want to Run It? → [QUICKSTART.md](QUICKSTART.md)

**Time:** 5 minutes  
**For:** Users who want to see the system in action immediately

### Path 2: Understand the System → [README.md](README.md)

**Time:** 15-20 minutes  
**For:** Users who want comprehensive documentation and multiple ways to run the system

### Path 3: Deep Dive → [ARCHITECTURE.md](ARCHITECTURE.md)

**Time:** 30+ minutes  
**For:** Developers who want to understand the technical implementation

### Path 4: Want to Contribute? → [CONTRIBUTING.md](CONTRIBUTING.md)

**Time:** Variable  
**For:** Contributors ready to enhance the project

---

## ⚡ Super Quick Start

For the impatient:

```bash
# Install dependencies
pip install -r requirements.txt

# Run everything
./start.sh
# Choose option 1

# Login with: admin / 123
```

That's it! 🎉

---

## 🎓 What This Project Teaches

### Distributed Systems Concepts

✅ **Consensus Algorithms** - Raft protocol implementation  
✅ **Leader Election** - Automatic failover and recovery  
✅ **Log Replication** - Data consistency across nodes  
✅ **Fault Tolerance** - System works with minority failures  
✅ **Network Partitions** - Handling split-brain scenarios  

### Software Engineering

✅ **Microservices Architecture** - Separation of concerns  
✅ **RESTful APIs** - Modern web service design  
✅ **gRPC Communication** - High-performance RPC  
✅ **Protocol Buffers** - Efficient serialization  
✅ **Async Programming** - FastAPI async/await patterns  

### Practical Skills

✅ **Python Development** - Real-world Python application  
✅ **GUI Development** - Desktop app with CustomTkinter  
✅ **Database Management** - SQLite integration  
✅ **Testing** - Unit and integration tests  
✅ **Documentation** - Comprehensive project docs  

---

## 🏗️ System Components at a Glance

```
┌─────────────────────────────────────────────────────┐
│  GUI Application (app.py)                           │
│  • User Login                                       │
│  • Movie Management                                 │
│  • Raft Node Control                               │
└────────────┬────────────────────────────────────────┘
             │
             ├──► Application Server (port 9000)
             │    • User Authentication
             │    • Booking Management
             │    • Business Logic
             │
             └──► Raft Cluster (ports 50051-50053)
                  • Leader Election
                  • Consensus Protocol
                  • Data Replication
```

---

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.8 or higher installed
- [ ] pip package manager available
- [ ] At least 1GB free RAM (for LLM model)
- [ ] Terminal/Command Prompt access
- [ ] Internet connection (for downloading dependencies)

**Check your versions:**
```bash
python --version   # Should be 3.8+
pip --version      # Should be installed
```

---

## 🔧 Installation Methods

### Method 1: Automatic (Recommended)

```bash
pip install -r requirements.txt
```

**Time:** 2-3 minutes

---

### Method 2: Manual (If automatic fails)

```bash
# Core dependencies
pip install fastapi uvicorn requests

# GUI
pip install customtkinter

# gRPC
pip install grpcio grpcio-tools

# LLM (optional, heavy download)
pip install transformers torch
```

---

## 🎮 Running the System

### Option A: Automated Script

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

**Windows:**
```bash
start.bat
```

Then select option **1** for full system.

---

### Option B: Step-by-Step Manual

**Terminal 1 - Application Server:**
```bash
python Application_server/Application_server.py
```
Wait for: `Uvicorn running on http://127.0.0.1:9000`

**Terminal 2, 3, 4 - Raft Nodes:**
```bash
python main.py node1  # Terminal 2
python main.py node2  # Terminal 3
python main.py node3  # Terminal 4
```
Wait for one to show: `🏆 is the LEADER now`

**Terminal 5 - GUI:**
```bash
python app.py
```
GUI window should open.

---

## 🎯 First Use Tutorial

### Step 1: Start Raft Nodes

In the GUI login screen:
1. Click **"Start Node 1"** → Wait for 🟢
2. Click **"Start Node 2"** → Wait for 🟢
3. Click **"Start Node 3"** → Wait for 🟢

⏳ **Wait 5-8 seconds** for leader election.

---

### Step 2: Login

- **Username:** `admin`
- **Password:** `123`

Click **"Login"**

---

### Step 3: Add Movies

1. Enter a movie name (e.g., "Inception")
2. Click **"Add Movie"**
3. Movie appears in the table below

---

### Step 4: Test the System

**Option A: Simulate Clients**
- Click **"Simulate Multiple Clients (5 users booking)"**
- Check terminals for booking logs

**Option B: Test Raft**
- Click **"Test Database Consistency (Raft Verification)"**
- Should show "✅ Raft Verified: Leader detected"

---

## 🔍 Verify Everything Works

### Check 1: Application Server

```bash
curl http://127.0.0.1:9000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "123"}'
```

**Expected:** JSON with `"status": "success"` and a token

---

### Check 2: Raft Nodes

```bash
curl http://localhost:50051/status
curl http://localhost:50052/status
curl http://localhost:50053/status
```

**Expected:** One shows `"state": "leader"`, others show `"follower"`

---

### Check 3: GUI

- GUI window should be open
- You should be logged in as admin
- Movies table should be visible

---

## 🐛 Common Issues & Solutions

### Issue 1: "Module not found"

**Solution:**
```bash
pip install -r requirements.txt
```

---

### Issue 2: "Port already in use"

**Linux/Mac:**
```bash
lsof -ti:9000,50051,50052,50053 | xargs kill -9
```

**Windows:**
```bash
netstat -ano | findstr :9000
taskkill /PID <PID> /F
```

---

### Issue 3: GUI won't open

**Linux (missing tkinter):**
```bash
sudo apt-get install python3-tk      # Ubuntu/Debian
sudo dnf install python3-tkinter     # Fedora
sudo pacman -S tk                    # Arch
```

**Windows/Mac:** Should work out of the box

---

### Issue 4: No leader elected

**Solution:**
1. Stop all nodes
2. Restart all 3 nodes at approximately the same time
3. Wait 5-8 seconds
4. Check logs for "🏆 is the LEADER now"

---

### Issue 5: Import errors

**Check you're in the right directory:**
```bash
pwd  # Should show: /home/aniket/study/ds
ls   # Should show: app.py, main.py, Application_server/, etc.
```

---

## 📊 System Health Checklist

After starting everything:

- [ ] Application Server running (port 9000)
- [ ] 3 Raft nodes running (ports 50051-50053)
- [ ] One Raft node is LEADER
- [ ] GUI is open and responsive
- [ ] Can login as admin
- [ ] Can add movies
- [ ] Client simulation works

---

## 🎓 Learning Path

### Beginner (Week 1)
1. Run the system using QUICKSTART.md
2. Explore the GUI features
3. Read README.md overview
4. Try simulating clients

### Intermediate (Week 2)
1. Study ARCHITECTURE.md
2. Understand Raft consensus
3. Modify application server endpoints
4. Add a new feature to the GUI

### Advanced (Week 3+)
1. Implement persistent storage
2. Add security features
3. Write comprehensive tests
4. Contribute back (see CONTRIBUTING.md)

---

## 🔗 Useful Links

| Resource | Link |
|----------|------|
| Raft Interactive Visualization | https://raft.github.io/ |
| FastAPI Documentation | https://fastapi.tiangolo.com/ |
| gRPC Python Guide | https://grpc.io/docs/languages/python/ |
| CustomTkinter Docs | https://customtkinter.tomschimansky.com/ |

---

## 📞 Getting Help

### Documentation Not Clear?

1. Check [README.md](README.md) for detailed explanations
2. Check [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
3. Look at code comments in Python files

### Found a Bug?

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to report issues

### Want to Improve Docs?

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 🎯 Next Steps

Choose what interests you:

**🎮 Want to use it?** → Open the GUI and explore features  
**🔧 Want to modify it?** → Read ARCHITECTURE.md  
**🤝 Want to contribute?** → Read CONTRIBUTING.md  
**📚 Want to learn?** → Study the code with README.md open  

---

## 🏆 Project Goals Achieved

✅ **Working distributed system** with real consensus  
✅ **Educational codebase** with comprehensive docs  
✅ **Multiple interfaces** (GUI, CLI, API)  
✅ **Real-world patterns** (authentication, booking logic)  
✅ **Extensible design** for future enhancements  

---

## 📝 Project Structure Summary

```
ds/
├── 📄 Documentation
│   ├── README.md           ← Comprehensive guide
│   ├── QUICKSTART.md       ← Fast setup (5 min)
│   ├── ARCHITECTURE.md     ← Technical deep dive
│   ├── CONTRIBUTING.md     ← How to contribute
│   └── GETTING_STARTED.md  ← This file
│
├── 🚀 Quick Start Scripts
│   ├── start.sh            ← Linux/Mac launcher
│   ├── start.bat           ← Windows launcher
│   └── requirements.txt    ← Dependencies
│
├── 🖥️ Application Code
│   ├── app.py              ← GUI application
│   ├── main.py             ← Raft node launcher
│   ├── Application_server/ ← REST API server
│   ├── client/             ← Client simulator
│   ├── llm/                ← LLM FAQ server + DB
│   ├── proto/              ← Protocol Buffers
│   └── raft/               ← Raft implementation
│
└── 🧪 Tests
    └── tests/              ← Unit & integration tests
```

---

## 🎉 You're Ready!

You now have everything you need to:
- ✅ Run the system
- ✅ Understand how it works
- ✅ Modify and extend it
- ✅ Contribute improvements

**Start with:** [QUICKSTART.md](QUICKSTART.md) if you haven't already!

---

**Happy Learning! 🚀**

Questions? Check the other documentation files or create an issue on GitHub.
