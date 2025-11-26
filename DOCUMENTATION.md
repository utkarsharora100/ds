# Distributed Movie Booking System

A fault-tolerant movie ticket booking system using Raft consensus algorithm with gRPC communication and MongoDB persistence.

---

## System Architecture

```
                                    ┌─────────────────┐
                                    │   Web Browser   │
                                    │   (Port 3000)   │
                                    └────────┬────────┘
                                             │ HTTP
                                             ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                        Docker Network (movie-booking-net)                  │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌──────────────────┐          ┌──────────────────┐                       │
│  │   App Server     │          │    LLM Server    │                       │
│  │   (Port 9000)    │          │   (Port 8500)    │                       │
│  │   FastAPI REST   │          │   FAQ Assistant  │                       │
│  └────────┬─────────┘          └──────────────────┘                       │
│           │                                                                │
│           ▼                                                                │
│  ┌──────────────────┐                                                     │
│  │     MongoDB      │  Application Data (users, movies, bookings)         │
│  │   (Port 27017)   │                                                     │
│  └──────────────────┘                                                     │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    Raft Consensus Cluster (gRPC)                    │  │
│  │                                                                     │  │
│  │  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐           │  │
│  │  │ raft-node1  │     │ raft-node2  │     │ raft-node3  │           │  │
│  │  │ (Port 50051)│◄───►│ (Port 50052)│◄───►│ (Port 50053)│           │  │
│  │  └──────┬──────┘     └──────┬──────┘     └──────┬──────┘           │  │
│  │         │                   │                   │                   │  │
│  │         ▼                   ▼                   ▼                   │  │
│  │  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐           │  │
│  │  │mongodb-raft1│     │mongodb-raft2│     │mongodb-raft3│           │  │
│  │  │ (Port 27018)│     │ (Port 27019)│     │ (Port 27020)│           │  │
│  │  └─────────────┘     └─────────────┘     └─────────────┘           │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. Raft Consensus Layer (`raft/`)

**raft_node_grpc.py** - Core Raft implementation using gRPC
- Leader election with randomized timeouts
- Log replication via AppendEntries RPC
- Heartbeat mechanism (50ms interval)
- Crash recovery from MongoDB

**raft_storage.py** - MongoDB persistence layer
- Singleton pattern (one connection per node)
- Persists: log entries, state machine, metadata (term, votedFor)
- Async writes for performance

**Key Raft Properties:**
- Election timeout: 500-1000ms
- Heartbeat interval: 50ms
- RPC timeout: 1 second
- Cluster size: 3 nodes (tolerates 1 failure)

### 2. Application Server (`Application_server/`)

**Application_server.py** - FastAPI REST backend
- User authentication (register, login, logout)
- Movie catalog management
- Seat booking with availability checks
- Admin endpoints for data management

**mongodb_storage.py** - Application data storage
- Collections: users, sessions, movies, bookings
- Atomic seat updates to prevent overbooking

### 3. LLM Server (`llm/`)

**llm_server.py** - FAQ assistant endpoint
- Uses DistilGPT2 model
- Answers movie booking questions
- Optional service (can be disabled)

### 4. Web Frontend (`web/`)

**app.js** - Single-page application
- User registration and login
- Movie browsing and booking
- Real-time seat availability
- Raft cluster status monitoring

### 5. Protocol Buffers (`proto/`)

**raft.proto** - gRPC service definitions
```protobuf
service RaftService {
  rpc RequestVote(RequestVoteRequest) returns (RequestVoteResponse);
  rpc AppendEntries(AppendEntriesRequest) returns (AppendEntriesResponse);
}
```

---

## Docker Services

| Service | Port (Internal) | Port (External) | Description |
|---------|-----------------|-----------------|-------------|
| app-server | 9000 | 9000 | FastAPI backend |
| mongodb | 27017 | 27017 | Application database |
| raft-node1 | 50051 (gRPC), 51051 (HTTP) | 50061, 51061 | Raft consensus node |
| raft-node2 | 50052 (gRPC), 51052 (HTTP) | 50062, 51062 | Raft consensus node |
| raft-node3 | 50053 (gRPC), 51053 (HTTP) | 50063, 51063 | Raft consensus node |
| mongodb-raft1 | 27017 | 27018 | Raft node 1 persistence |
| mongodb-raft2 | 27017 | 27019 | Raft node 2 persistence |
| mongodb-raft3 | 27017 | 27020 | Raft node 3 persistence |
| llm-server | 8500 | 8500 | LLM FAQ service |

### Raft Node Communication

Each Raft node exposes two ports:
- **gRPC Port** (50051-50053): Inter-node Raft consensus (RequestVote, AppendEntries)
- **HTTP Port** (51051-51053): Status monitoring for frontend integration

HTTP Status Endpoints:
- `GET /status` - Node status (state, term, leader, log length)
- `GET /health` - Health check
- `GET /log` - Log entries
- `GET /state` - State machine data

---

## API Endpoints

### Health & Status
- `GET /health` - Server health check
- `GET /proxy/raft/{node_id}/status` - Raft node status

### Authentication
- `POST /register` - Register new user
- `POST /login` - User login (returns token)
- `POST /logout` - User logout

### Data
- `GET /data/movies` - List all movies
- `GET /data/bookings` - User's bookings
- `GET /data/bookings/all` - All bookings (admin)

### Business
- `POST /business` - Book movie seats

### Admin
- `POST /admin/clear_database` - Clear all data
- `POST /admin/load_sample_data` - Load sample movies

---

## How to Run

### Prerequisites
- Docker and Docker Compose installed
- At least 4GB RAM available

### Start the System
```bash
cd ds
docker-compose up --build
```

### Access Points
- Web UI: http://localhost:9000 (served by app-server)
- API: http://localhost:9000
- Raft nodes: localhost:50061, 50062, 50063

### Default Credentials
- Admin: `admin` / `123`
- Sample user: `utkarsh` / `password123`

### Test Crash Recovery
1. Start all services
2. Make some bookings
3. Stop a Raft node: `docker stop mtbs-raft-node1`
4. Restart it: `docker start mtbs-raft-node1`
5. Verify state is recovered from MongoDB

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f raft-node1
```

---

## File Structure

```
ds/
├── main.py                 # Raft node entry point
├── start_combined.py       # Combined frontend+backend startup
├── docker-compose.yml      # Docker orchestration
├── README.md               # Quick start guide
├── DOCUMENTATION.md        # This file
│
├── raft/                   # Raft consensus implementation
│   ├── raft_node_grpc.py   # gRPC-based Raft node
│   ├── raft_storage.py     # MongoDB persistence
│   └── raft_state.py       # State machine
│
├── proto/                  # Protocol buffer definitions
│   ├── raft.proto          # gRPC service definition
│   ├── raft_pb2.py         # Generated message classes
│   └── raft_pb2_grpc.py    # Generated gRPC stubs
│
├── Application_server/     # FastAPI backend
│   ├── Application_server.py
│   └── mongodb_storage.py
│
├── llm/                    # LLM FAQ service
│   ├── llm_server.py
│   ├── storage.py
│   └── prompt_templates.py
│
├── web/                    # Frontend application
│   ├── app.js
│   ├── index.html
│   └── styles.css
│
├── client/                 # Test client
│   └── client.py
│
├── docker/                 # Dockerfiles
│   ├── Dockerfile.app
│   ├── Dockerfile.raft
│   ├── Dockerfile.llm
│   └── Dockerfile.combined
│
├── requirements/           # Python dependencies
│   ├── requirements-base.txt
│   ├── requirements-raft.txt
│   └── requirements-llm.txt
│
└── archive/                # Deprecated files (not used)
```

---

## Key Features

1. **Fault Tolerance**: Raft consensus ensures system continues with 1 node failure
2. **Persistence**: MongoDB stores all Raft state for crash recovery
3. **Scalability**: Microservices architecture with Docker
4. **Modern Stack**: gRPC, FastAPI, MongoDB, React-like frontend
5. **Real-time**: Heartbeat-based leader monitoring

---

## Troubleshooting

### Port Conflicts
```bash
# Check what's using a port
lsof -i :9000
```

### Container Issues
```bash
# Rebuild containers
docker-compose down
docker-compose up --build

# Remove all volumes (WARNING: deletes data)
docker-compose down -v
```

### Raft Election Issues
- Check logs for election timeouts
- Ensure all 3 Raft nodes can communicate
- Verify MongoDB connections for each node
