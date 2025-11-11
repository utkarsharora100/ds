# Raft Consensus Testing Guide

## Current Status

### ✅ Completed Fixes
1. **Database Integration** - Movies are now stored in SQLite database via `storage.py`
2. **Seat Management** - Admin can specify seat counts when adding movies
3. **Dynamic Seat Tracking** - Available seats decrement when bookings are made
4. **Validation** - Bookings fail when insufficient seats are available
5. **Persistent Storage** - Sample movies loaded from database on startup

### 🔄 Raft Cluster Status
- **3 Nodes Running**: node1 (port 50051), node2 (port 50052), node3 (port 50053)
- **Leader Election**: Working - nodes elect leaders automatically
- **Cluster Health**: All nodes responding to `/status` endpoint

## Testing Database Integration

### 1. Check Initial Movies (From Database)
```bash
TOKEN="cbeca569-219e-41f3-bf48-87e5be5e7a60"  # Your login token
curl -s "http://127.0.0.1:9000/data/movies?token=$TOKEN"
```

**Expected Result**: Shows 5 sample movies from database with seat counts:
- Interstellar (English) - 169 seats
- Inception (English) - 148 seats
- Dangal (Hindi) - 161 seats
- Avatar (English) - 181 seats
- Baahubali (Telugu) - 167 seats

### 2. Add Movie with Seats
```bash
curl -X POST http://127.0.0.1:9000/add_movie \
  -H "Content-Type: application/json" \
  -d '{"token":"'$TOKEN'","movie":"Dune 2","city":"New York","seats":100}'
```

**Expected Result**: `{"status":"success"}`

### 3. Verify Movie Added to Database
```bash
curl -s "http://127.0.0.1:9000/data/movies?token=$TOKEN" | grep "Dune 2"
```

**Expected Result**: Shows Dune 2 with 100 seats

### 4. Book Tickets
```bash
curl -X POST http://127.0.0.1:9000/business \
  -H "Content-Type: application/json" \
  -d '{
    "requestId":"test-1",
    "payload":{
      "type":"book_seat",
      "data":{"movie":"Dune 2","city":"New York","seats":5}
    },
    "context":{"token":"'$TOKEN'"}
  }'
```

**Expected Result**: `{"status":"success","booking_id":"<uuid>"}`

### 5. Check Seat Decrement
```bash
curl -s "http://127.0.0.1:9000/data/movies?token=$TOKEN" | grep "Dune 2"
```

**Expected Result**: Shows Dune 2 with 95 seats (100 - 5)

### 6. Test Insufficient Seats
```bash
curl -X POST http://127.0.0.1:9000/business \
  -H "Content-Type: application/json" \
  -d '{
    "requestId":"test-2",
    "payload":{
      "type":"book_seat",
      "data":{"movie":"Dune 2","city":"New York","seats":100}
    },
    "context":{"token":"'$TOKEN'"}
  }'
```

**Expected Result**: `{"status":"failure","message":"Insufficient seats or movie not found"}`

## Testing Raft Cluster

### Check Node Status
```bash
# Node 1
curl http://127.0.0.1:50051/status

# Node 2
curl http://127.0.0.1:50052/status

# Node 3
curl http://127.0.0.1:50053/status
```

**Expected Response**:
```json
{
  "node_id": "node1",
  "state": "leader",  // or "follower"
  "term": 2,
  "leader_id": "node1",
  "peers": ["node2", "node3"]
}
```

### Trigger Manual Election
```bash
curl -X POST http://127.0.0.1:50051/trigger-election
```

### Monitor Leader Changes
```bash
# Run this in a loop to watch elections
while true; do
  echo "=== $(date) ==="
  curl -s http://127.0.0.1:50051/status | grep -o '"state":"[^"]*"'
  curl -s http://127.0.0.1:50052/status | grep -o '"state":"[^"]*"'
  curl -s http://127.0.0.1:50053/status | grep -o '"state":"[^"]*"'
  sleep 3
done
```

## Current Raft Limitations

⚠️ **Important**: The current Raft implementation handles **leader election only**. Database operations are **not yet replicated** across Raft nodes.

### What's Working:
- ✅ Leader election with majority voting
- ✅ Term management
- ✅ Election timeout handling
- ✅ Automatic re-election on leader failure

### What's Not Implemented:
- ❌ Log replication across nodes
- ❌ Database state synchronization
- ❌ Write forwarding from followers to leader
- ❌ Consensus on database mutations

### Architecture Notes:
- Each Raft node runs independently
- Application server has **one** database instance
- Raft cluster is **separate** from application server
- To achieve true distributed consistency, need to:
  1. Add gRPC methods for log replication
  2. Implement `AppendEntries` RPC
  3. Forward all writes through Raft leader
  4. Apply committed log entries to database

## Verified Test Results

### ✅ Database Storage
- Movies persist in SQLite database
- Sample data loads on startup
- Admin-added movies stored in DB
- Client views show movies from database

### ✅ Seat Management  
- Seats specified during movie creation
- Initial count stored in database
- Bookings decrement available seats
- Insufficient seats validation works

### ✅ API Integration
- `/add_movie` accepts seats parameter
- `/data/movies` returns seat counts
- `/business` booking validates seat availability
- Proper error messages on failures

### ✅ Raft Cluster Health
- All 3 nodes running and responsive
- Leader election functioning
- `/status` endpoint shows cluster state
- Manual election triggers work

## Quick Verification Commands

```bash
# 1. Login and get token
LOGIN_RESP=$(curl -s -X POST http://127.0.0.1:9000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123"}')
TOKEN=$(echo $LOGIN_RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

# 2. View all movies with seats
curl -s "http://127.0.0.1:9000/data/movies?token=$TOKEN" | \
  python3 -c "import sys,json; data=json.load(sys.stdin); [print(f\"{m['data']['movie']:20} | {m['data']['city']:15} | {m['data']['seats']:3} seats\") for m in data['data']]"

# 3. Add movie with custom seat count
curl -s -X POST http://127.0.0.1:9000/add_movie \
  -H "Content-Type: application/json" \
  -d "{\"token\":\"$TOKEN\",\"movie\":\"The Matrix\",\"city\":\"LA\",\"seats\":75}"

# 4. Book tickets
curl -s -X POST http://127.0.0.1:9000/business \
  -H "Content-Type: application/json" \
  -d "{\"requestId\":\"test\",\"payload\":{\"type\":\"book_seat\",\"data\":{\"movie\":\"The Matrix\",\"city\":\"LA\",\"seats\":10}},\"context\":{\"token\":\"$TOKEN\"}}"

# 5. Verify seat decrease
curl -s "http://127.0.0.1:9000/data/movies?token=$TOKEN" | \
  python3 -c "import sys,json; data=json.load(sys.stdin); m=[x for x in data['data'] if x['data']['movie']=='The Matrix'][0]; print(f\"The Matrix: {m['data']['seats']} seats remaining\")"

# 6. Check Raft leader
curl -s http://127.0.0.1:50051/status | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"Node: {d['node_id']}, State: {d['state']}, Leader: {d['leader_id']}\")"
```

## Summary

**Database Integration**: ✅ **COMPLETE**
- All movies stored in SQLite
- Seats managed dynamically
- Bookings validate seat availability
- Data persists across restarts

**Raft Consensus**: ⚠️ **PARTIAL**
- Leader election working
- Cluster health monitoring available
- **Data replication not implemented** (requires additional gRPC work)

For production-grade distributed consensus with data replication, consider:
1. Implementing full Raft protocol (AppendEntries RPC)
2. Using existing libraries like etcd, Consul, or ZooKeeper
3. Integrating application server as Raft state machine
