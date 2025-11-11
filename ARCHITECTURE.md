# 🏗️ System Architecture

## Overview

This document provides a detailed technical overview of the Distributed Movie Booking System architecture.

## System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐                    ┌──────────────┐           │
│  │   GUI App    │                    │ CLI Client   │           │
│  │ (app.py)     │                    │ (client.py)  │           │
│  └──────┬───────┘                    └──────┬───────┘           │
│         │                                    │                   │
└─────────┼────────────────────────────────────┼───────────────────┘
          │                                    │
          │            HTTP/REST               │
          └────────────────┬───────────────────┘
                          │
┌─────────────────────────▼─────────────────────────────────────┐
│                   APPLICATION LAYER                            │
├────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────┐   │
│  │       Application Server (FastAPI)                      │   │
│  │       Port: 9000                                        │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐             │   │
│  │  │   Auth   │  │ Business │  │  Admin   │             │   │
│  │  │  Module  │  │  Logic   │  │  Panel   │             │   │
│  │  └──────────┘  └──────────┘  └──────────┘             │   │
│  └────────────────────────┬───────────────────────────────┘   │
│                           │                                    │
│  ┌────────────────────────▼───────────────────────────────┐   │
│  │          LLM Server (Optional)                         │   │
│  │          Port: 8500                                    │   │
│  │          Model: deepset/roberta-base-squad2           │   │
│  └────────────────────────────────────────────────────────┘   │
└────────────────────────┬───────────────────────────────────────┘
                         │
                         │ SQLite
                         ▼
┌────────────────────────────────────────────────────────────────┐
│                    DATA PERSISTENCE LAYER                       │
├────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Users &    │  │   Movies &   │  │   Bookings   │         │
│  │   Sessions   │  │  Showtimes   │  │   & Seats    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                   In-Memory SQLite                              │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│                    CONSENSUS LAYER (Raft)                       │
├────────────────────────────────────────────────────────────────┤
│  ┌──────────┐         ┌──────────┐         ┌──────────┐       │
│  │  Node 1  │◄───────►│  Node 2  │◄───────►│  Node 3  │       │
│  │  :50051  │  gRPC   │  :50052  │  gRPC   │  :50053  │       │
│  └──────────┘         └──────────┘         └──────────┘       │
│       │                     │                     │            │
│       └─────────────────────┴─────────────────────┘            │
│                  Leader Election                               │
│              (Raft Consensus Protocol)                         │
└────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. GUI Application (`app.py`)

**Technology:** CustomTkinter (modern Tkinter wrapper)

**Responsibilities:**
- User authentication interface
- Admin dashboard for movie management
- Client simulation controls
- Raft node lifecycle management
- Visual feedback for system status

**Key Features:**
- Dark mode UI
- Multi-threaded to prevent blocking
- Direct subprocess management for Raft nodes
- Real-time status indicators

**Communication:**
- HTTP REST calls to Application Server
- Direct subprocess spawning for Raft nodes

---

### 2. Application Server (`Application_server/Application_server.py`)

**Technology:** FastAPI + Uvicorn (ASGI)

**Port:** 9000

**Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | Create new user account |
| POST | `/login` | Authenticate and get session token |
| GET | `/data/{type}` | Fetch movies, bookings, etc. |
| POST | `/business` | Process booking requests |
| POST | `/add_movie` | Admin: Add new movie |

**Data Structures:**
```python
{
    "users": Dict[str, str],           # username -> password
    "sessions": Dict[str, str],        # token -> username
    "store": {
        "movies": List[Dict],
        "bookings": List[Dict],
        "documents": List[Dict],
        "messages": List[Dict]
    }
}
```

**Authentication:**
- Token-based sessions (UUID4)
- In-memory session storage
- No expiration (current implementation)

---

### 3. Raft Consensus Layer

**Technology:** Custom implementation + gRPC + Protocol Buffers

**Protocol:** Raft Consensus Algorithm

#### Raft Node (`raft/raft_node.py`)

**Ports:** 50051, 50052, 50053

**States:**
- `follower`: Default state, responds to leader
- `candidate`: Requests votes during election
- `leader`: Handles all client requests

**Key Mechanisms:**

1. **Leader Election:**
   - Election timeout: 5-8 seconds (randomized)
   - Majority vote required
   - Term-based versioning

2. **Heartbeat:**
   - Leader sends periodic heartbeats (1 second interval)
   - Prevents unnecessary elections
   - Confirms leader liveness

3. **Log Replication:**
   - Leader replicates log entries to followers
   - Ensures consistency across cluster
   - Commit only after majority acknowledgment

**gRPC Services:**
```protobuf
service RaftService {
  rpc RequestVote(RequestVoteRequest) returns (RequestVoteResponse);
  rpc AppendEntries(AppendEntriesRequest) returns (AppendEntriesResponse);
}
```

**FastAPI Endpoints:**
- `GET /status`: Node state, term, leader info
- `POST /trigger-election`: Manual election trigger (testing)

---

### 4. LLM Server (`llm/llm_server.py`)

**Technology:** FastAPI + Hugging Face Transformers

**Port:** 8500

**Model:** `deepset/roberta-base-squad2` (BERT-based Q&A)

**Functionality:**
- Answer domain-specific FAQs
- Extractive question answering
- Context-based responses

**Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/ask` | Submit question, get answer |

**Response Format:**
```json
{
  "answer": "string",
  "confidence": 0.0-1.0
}
```

**Context Domain:**
- Movie booking process
- Cancellation policies
- Payment procedures
- System architecture (Raft)
- Support information

---

### 5. Client Simulator (`client/client.py`)

**Purpose:** Automated testing and load simulation

**Capabilities:**
- User registration
- Authentication
- Movie listing
- Seat booking

**Use Cases:**
- Concurrent client testing
- Load testing
- Integration testing
- Demo purposes

---

### 6. Data Layer (`llm/storage.py`)

**Technology:** SQLite (in-memory)

**Schema:**

```sql
-- Authentication
users (id, username, password_hash, created_at)
sessions (token, user_id, created_at, expires_at)

-- Movies
movies (id, title, language, format, duration)
showtimes (id, movie_id, start_time, screen)
seats (id, showtime_id, row, seat_number, price, available)
```

**Functions:**
- `create_user()`: Register new user
- `authenticate_user()`: Validate credentials
- `create_session()`: Generate session token
- `get_user_by_token()`: Validate session
- `logout()`: Invalidate session

**Initialization:**
- Auto-seeded with sample movies
- Random showtimes and seat allocation
- 5 movies × ~2 showtimes × 50 seats each

---

## Communication Patterns

### 1. Client → Application Server
**Protocol:** HTTP/REST  
**Format:** JSON  
**Security:** Token-based authentication

```
Client                    Application Server
  │                              │
  ├─── POST /login ─────────────►│
  │                              │
  │◄─── {token: "..."} ──────────┤
  │                              │
  ├─── GET /data/movies ────────►│
  │      ?token=...              │
  │◄─── [{movie1}, {movie2}] ────┤
```

### 2. Raft Inter-Node Communication
**Protocol:** gRPC  
**Format:** Protocol Buffers  
**Security:** None (trusted network assumed)

```
Node 1 (Leader)         Node 2 (Follower)
  │                           │
  ├─── AppendEntries ────────►│
  │    (heartbeat)            │
  │◄─── Success ──────────────┤
  │                           │
```

### 3. GUI → Raft Nodes
**Protocol:** HTTP/REST (FastAPI endpoints)  
**Purpose:** Status monitoring

```
GUI                     Raft Node
  │                         │
  ├─── GET /status ────────►│
  │                         │
  │◄─── {state: "leader"} ──┤
```

---

## Raft Consensus Algorithm

### States and Transitions

```
┌──────────┐  timeout, start election   ┌───────────┐
│ Follower │──────────────────────────►│ Candidate │
└──────────┘                            └───────────┘
     ▲                                       │
     │                                       │ receives votes
     │                                       │ from majority
     │  discovers current leader             │
     │  or new term                          ▼
     │                                  ┌────────┐
     └──────────────────────────────────┤ Leader │
                                        └────────┘
```

### Election Process

1. **Timeout Occurs:**
   - Follower doesn't receive heartbeat
   - Transitions to Candidate
   - Increments term

2. **Vote Request:**
   - Candidate votes for itself
   - Sends RequestVote RPC to all peers
   - Includes term and log info

3. **Vote Decision:**
   - Followers grant vote if:
     - Haven't voted this term
     - Candidate's log is up-to-date

4. **Election Outcome:**
   - **Win:** Majority votes → Become Leader
   - **Lose:** Discover higher term → Become Follower
   - **Split:** Timeout → Start new election

### Log Replication

1. **Client Request:**
   - Sent to leader
   - Leader appends to local log

2. **Replication:**
   - Leader sends AppendEntries to followers
   - Includes log entries

3. **Commitment:**
   - After majority acknowledgment
   - Leader commits entry
   - Notifies followers to commit

4. **Apply:**
   - State machine applies committed entries
   - Results returned to client

---

## Data Flow Example: Movie Booking

```
┌───────┐       ┌─────────────┐       ┌──────────┐       ┌─────────┐
│ User  │       │ GUI/Client  │       │   App    │       │ SQLite  │
│       │       │             │       │  Server  │       │   DB    │
└───┬───┘       └──────┬──────┘       └─────┬────┘       └────┬────┘
    │                  │                    │                  │
    │  Click "Book"    │                    │                  │
    ├─────────────────►│                    │                  │
    │                  │  POST /business    │                  │
    │                  ├───────────────────►│                  │
    │                  │  {type: "book"}    │                  │
    │                  │  {token: "..."}    │                  │
    │                  │                    │  Validate Token  │
    │                  │                    ├─────────────────►│
    │                  │                    │◄─────────────────┤
    │                  │                    │  User Valid      │
    │                  │                    │                  │
    │                  │                    │  Create Booking  │
    │                  │                    ├─────────────────►│
    │                  │                    │◄─────────────────┤
    │                  │                    │  Booking ID      │
    │                  │  {booking_id}      │                  │
    │                  │◄───────────────────┤                  │
    │  "Booking OK"    │                    │                  │
    │◄─────────────────┤                    │                  │
    │                  │                    │                  │
```

---

## Scalability Considerations

### Current Limitations

1. **In-Memory Storage:**
   - Data lost on restart
   - Limited by RAM

2. **Single Application Server:**
   - No load balancing
   - Single point of failure

3. **Static Raft Cluster:**
   - 3 nodes only
   - Manual configuration

### Future Improvements

1. **Persistent Storage:**
   - PostgreSQL/MySQL
   - Distributed databases (Cassandra, MongoDB)

2. **Horizontal Scaling:**
   - Multiple application servers
   - Load balancer (Nginx, HAProxy)

3. **Dynamic Cluster Membership:**
   - Add/remove Raft nodes dynamically
   - Configuration service (etcd, Consul)

4. **Caching Layer:**
   - Redis for session management
   - Memcached for query results

5. **Message Queue:**
   - RabbitMQ/Kafka for async processing
   - Event-driven architecture

---

## Security Considerations

### Current Implementation

⚠️ **Not Production-Ready** - This is an educational project

**Missing Security Features:**
- No password hashing (plaintext storage)
- No HTTPS/TLS
- No rate limiting
- No input validation
- No CSRF protection
- No SQL injection prevention
- Hardcoded credentials

### Production Recommendations

1. **Authentication:**
   - bcrypt/argon2 password hashing
   - JWT with expiration
   - OAuth2 integration

2. **Network Security:**
   - TLS/SSL certificates
   - mTLS for Raft communication
   - Firewall rules

3. **Data Protection:**
   - Prepared statements (SQL)
   - Input sanitization
   - Output encoding

4. **Monitoring:**
   - Audit logging
   - Intrusion detection
   - Rate limiting

---

## Performance Characteristics

### Expected Latencies

| Operation | Latency | Notes |
|-----------|---------|-------|
| Login | ~10-50ms | In-memory lookup |
| Fetch Movies | ~5-20ms | SQLite query |
| Book Seat | ~50-200ms | Includes DB write |
| Raft Election | 5-8s | Timeout period |
| Raft Heartbeat | 1s | Leader → Followers |

### Throughput

- **Application Server:** ~1000 req/s (single instance)
- **Raft Cluster:** ~100 commits/s (dependent on network)
- **Database:** Limited by SQLite (single writer)

### Resource Usage

- **Memory:** ~500MB (with LLM model loaded)
- **CPU:** Low (~5% idle, ~30% under load)
- **Network:** <1 Mbps for typical workloads

---

## Testing Strategy

### Unit Tests (`tests/`)

- `test_raft.py`: Raft algorithm correctness
- `test_booking.py`: Booking logic validation

### Integration Tests

- Client-server communication
- Multi-node Raft consensus
- Database operations

### Load Tests

- `client.py` with multiple concurrent instances
- GUI simulation feature (5 concurrent bookings)

### Manual Testing

- GUI functionality
- Node failure scenarios
- Leader election verification

---

## Deployment

### Development

```bash
# All services on localhost
python app.py
```

### Production (Recommended)

```bash
# Use Docker Compose
docker-compose up -d

# Or systemd services
systemctl start movie-booking-app
systemctl start movie-booking-raft@{1,2,3}
```

### Environment Variables

See `.env.example` for configuration options

---

## Monitoring & Observability

### Metrics to Track

1. **Application Server:**
   - Request rate
   - Response time
   - Error rate
   - Active sessions

2. **Raft Cluster:**
   - Leader stability
   - Election frequency
   - Log replication lag
   - Node health

3. **Database:**
   - Query latency
   - Connection pool
   - Storage usage

### Recommended Tools

- **Logging:** Structured logging (JSON), ELK stack
- **Metrics:** Prometheus + Grafana
- **Tracing:** Jaeger, OpenTelemetry
- **Alerts:** PagerDuty, Opsgenie

---

## Further Reading

- [Raft Paper](https://raft.github.io/raft.pdf)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [gRPC Python Tutorial](https://grpc.io/docs/languages/python/)
- [Distributed Systems Concepts](https://www.distributedsystemscourse.com/)

---

**Last Updated:** November 2025
