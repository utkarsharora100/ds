# Raft Leader Election Fix - Before & After

## 🚨 The Problem

**Error:** All 3 Raft nodes showing as "leader" simultaneously
**Location:** [raft/raft_node.py](raft/raft_node.py) lines 51-57
**Impact:** Violates Raft consensus protocol - only ONE leader should exist at any time

**Root Cause:** Nodes used **fake/simulated voting** instead of actual peer communication. Each node independently and randomly decided if it should become a leader, WITHOUT talking to other nodes.

---

## ✅ The Fix

### What Was Wrong

The `_start_election()` method used **random number generation** to simulate votes instead of actually requesting votes from peer nodes.

**BEFORE (Lines 51-57):**
```python
def _start_election(self):
    with self.lock:
        self.term += 1
        self.state = "candidate"
        self.voted_for = self.node_id

        # Simulate vote count
        votes = 1  # self vote
        total_nodes = len(self.peers) + 1
        majority = total_nodes // 2 + 1

        # ❌ FAKE VOTING - NO ACTUAL COMMUNICATION!
        votes += random.randint(0, len(self.peers))

        if votes >= majority:
            self.state = "leader"  # All nodes could become leader!
            self.leader_id = self.node_id
            print(f"[{self.node_id}] 🏆 is the LEADER now (term {self.term})")
        else:
            self.state = "follower"

        self.election_timeout = self._reset_timeout()
```

**Problems:**
1. ❌ No HTTP/gRPC communication with peers
2. ❌ Each node decides independently
3. ❌ Multiple nodes can become leader simultaneously
4. ❌ Violates Raft consensus algorithm

---

### What Was Fixed

**AFTER (Lines 46-93):**
```python
def _start_election(self):
    with self.lock:
        self.term += 1
        self.state = "candidate"
        self.voted_for = self.node_id

        # ✅ Real vote count - start with self vote
        votes = 1
        total_nodes = len(self.peers) + 1
        majority = total_nodes // 2 + 1

        # ✅ Request votes from actual peers via HTTP
        for peer_id, peer_address in self.peers.items():
            try:
                # Convert service name format to HTTP URL if needed
                if not peer_address.startswith('http'):
                    peer_url = f"http://{peer_address}"
                else:
                    peer_url = peer_address

                # ✅ REAL COMMUNICATION - Request vote from peer
                response = httpx.post(
                    f"{peer_url}/request-vote",
                    json={"term": self.term, "candidate_id": self.node_id},
                    timeout=1.0
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("vote_granted", False):
                        votes += 1
                        print(f"[{self.node_id}] ✓ Got vote from {peer_id}")
                    else:
                        print(f"[{self.node_id}] ✗ Vote denied by {peer_id} (term {data.get('term')})")
            except Exception as e:
                print(f"[{self.node_id}] ✗ Could not reach {peer_id}: {e}")

        # ✅ Check if we have majority of REAL votes
        if votes >= majority:
            self.state = "leader"
            self.leader_id = self.node_id
            print(f"[{self.node_id}] 🏆 is the LEADER now (term {self.term}, votes {votes}/{total_nodes})")
        else:
            self.state = "follower"
            print(f"[{self.node_id}] ❌ Election failed (term {self.term}, votes {votes}/{total_nodes})")

        self.election_timeout = self._reset_timeout()
```

**Improvements:**
1. ✅ Real HTTP communication with peers via httpx
2. ✅ Nodes must request votes from each peer
3. ✅ Only ONE node can get majority votes and become leader
4. ✅ Follows proper Raft consensus algorithm
5. ✅ Better logging showing vote counts

---

### New Endpoint Added

**BEFORE:** No endpoint for voting

**AFTER:** Added `/request-vote` endpoint (Lines 108-131)
```python
@self.app.post("/request-vote")
async def request_vote(request: Request):
    """Handle vote requests from other nodes during elections"""
    data = await request.json()
    candidate_term = data.get("term", 0)
    candidate_id = data.get("candidate_id", "")

    with self.lock:
        # If candidate's term is higher, update our term and step down
        if candidate_term > self.term:
            self.term = candidate_term
            self.state = "follower"
            self.voted_for = None
            self.leader_id = None

        # Grant vote if we haven't voted in this term
        if candidate_term == self.term and (self.voted_for is None or self.voted_for == candidate_id):
            self.voted_for = candidate_id
            self.election_timeout = self._reset_timeout()
            print(f"[{self.node_id}] ✓ Granted vote to {candidate_id} for term {candidate_term}")
            return {"term": self.term, "vote_granted": True}
        else:
            print(f"[{self.node_id}] ✗ Denied vote to {candidate_id} (already voted for {self.voted_for})")
            return {"term": self.term, "vote_granted": False}
```

**Features:**
- ✅ Nodes can only vote once per term
- ✅ Higher term candidates cause nodes to step down
- ✅ Resets election timeout when granting vote (Raft protocol)
- ✅ Proper vote granted/denied logic

---

### Import Changes

**BEFORE (Lines 1-3):**
```python
import threading
import random
import time
```

**AFTER (Lines 1-4):**
```python
import threading
import random
import time
import httpx  # ✅ Added for HTTP communication
```

Also updated FastAPI import to include `Request`:
```python
from fastapi import FastAPI, Request  # ✅ Added Request for POST endpoints
```

---

## 🚀 How to Apply the Fix

### Method 1: Use the Fix Script (Easiest)

```bash
cd "/Users/aniketsaxena/Desktop/untitled folder/SOFTWARE SYSTEM/Semester 1/AOS/project/v2/ds"
bash fix-raft-leader.sh
```

This script will:
1. Stop all 3 Raft nodes
2. Rebuild with no cache (ensures clean build)
3. Start all 3 Raft nodes
4. Check status of each node
5. Show which node is the leader

### Method 2: Manual Fix

```bash
cd "/Users/aniketsaxena/Desktop/untitled folder/SOFTWARE SYSTEM/Semester 1/AOS/project/v2/ds"

# Stop Raft nodes
docker compose -f docker-compose.combined.yml stop raft-node1 raft-node2 raft-node3

# Rebuild (no cache to ensure clean build)
docker compose -f docker-compose.combined.yml build --no-cache raft-node1 raft-node2 raft-node3

# Start Raft nodes
docker compose -f docker-compose.combined.yml up -d raft-node1 raft-node2 raft-node3

# Wait for startup
sleep 10

# Check status
curl http://localhost:50051/status | jq '.'
curl http://localhost:50052/status | jq '.'
curl http://localhost:50053/status | jq '.'
```

---

## 🧪 Verify the Fix

### Step 1: Check Node Status

```bash
# Check Node 1
curl http://localhost:50051/status

# Check Node 2
curl http://localhost:50052/status

# Check Node 3
curl http://localhost:50053/status
```

**Expected Output:**
```json
// Node 1 (example - LEADER)
{
  "node_id": "node1",
  "state": "leader",
  "term": 1,
  "leader_id": "node1",
  "peers": ["node2", "node3"]
}

// Node 2 (FOLLOWER)
{
  "node_id": "node2",
  "state": "follower",
  "term": 1,
  "leader_id": null,
  "peers": ["node1", "node3"]
}

// Node 3 (FOLLOWER)
{
  "node_id": "node3",
  "state": "follower",
  "term": 1,
  "leader_id": null,
  "peers": ["node1", "node2"]
}
```

**Key Points:**
- ✅ **Only ONE** node should have `"state": "leader"`
- ✅ Other nodes should have `"state": "follower"` or `"state": "candidate"`
- ✅ All nodes will eventually converge to same term

### Step 2: Check Logs for Vote Communication

```bash
# View Raft node logs
docker compose -f docker-compose.combined.yml logs -f raft-node1 raft-node2 raft-node3
```

**You Should See:**
```
[node1] ✓ Got vote from node2
[node1] ✓ Got vote from node3
[node1] 🏆 is the LEADER now (term 1, votes 3/3)

[node2] ✓ Granted vote to node1 for term 1
[node3] ✓ Granted vote to node1 for term 1
```

**You Should NOT See:**
```
[node1] 🏆 is the LEADER now
[node2] 🏆 is the LEADER now  # ❌ BAD - Multiple leaders!
[node3] 🏆 is the LEADER now  # ❌ BAD - Multiple leaders!
```

### Step 3: Test Leader Re-election

```bash
# Trigger new election on node 2
curl -X POST http://localhost:50052/trigger-election

# Check status again
curl http://localhost:50051/status | jq '.state'
curl http://localhost:50052/status | jq '.state'
curl http://localhost:50053/status | jq '.state'

# Still only ONE leader!
```

---

## 📊 Technical Details

### Raft Consensus Algorithm - Key Principles

1. **Leader Election:**
   - Nodes start as followers
   - If no heartbeat received, become candidate and request votes
   - Must get majority votes to become leader
   - Only ONE leader per term

2. **Vote Rules:**
   - Each node can only vote once per term
   - Vote for first candidate that requests (FIFO)
   - Higher term always wins

3. **Term Management:**
   - Term increments on each election
   - All nodes eventually converge to same term

### Why This Fix Works

**Before:**
- Node 1: `votes = 1 + random(0-2)` → Could be 1, 2, or 3 → Might become leader
- Node 2: `votes = 1 + random(0-2)` → Could be 1, 2, or 3 → Might become leader
- Node 3: `votes = 1 + random(0-2)` → Could be 1, 2, or 3 → Might become leader

Result: **All 3 could randomly become leaders!** ❌

**After:**
- Node 1 starts election, requests votes from Node 2 and Node 3
- Node 2 grants vote to Node 1 (first to ask)
- Node 3 grants vote to Node 1 (first to ask)
- Node 1: votes = 3/3 (majority) → **Becomes leader** ✅
- Node 2 starts election later, but Node 1 & Node 3 already voted → votes = 1/3 → **Stays follower** ✅
- Node 3 starts election later, but all voted → votes = 1/3 → **Stays follower** ✅

Result: **Only ONE leader!** ✅

---

## 🔍 Why This Happened

### Original Implementation

The original code was a **simplified simulation** meant for demonstration, not production use. It used `random.randint()` to simulate votes, which worked for showing the concept but didn't implement actual consensus.

### The Problem with Simulated Voting

```python
# This is NOT real consensus:
votes += random.randint(0, len(self.peers))  # Each node rolls dice independently!

# This IS real consensus:
for peer in peers:
    if peer.request_vote(self.term):  # Actually ask each peer!
        votes += 1
```

---

## 🛠️ Troubleshooting

### Issue: Still Seeing Multiple Leaders After Rebuild

**Solution:**
```bash
# Force complete rebuild and restart
docker compose -f docker-compose.combined.yml down
docker compose -f docker-compose.combined.yml build --no-cache raft-node1 raft-node2 raft-node3
docker compose -f docker-compose.combined.yml up -d
```

### Issue: Nodes Not Communicating

**Check logs:**
```bash
docker compose -f docker-compose.combined.yml logs raft-node1
```

**Common causes:**
1. Network issues between containers
2. Firewall blocking ports
3. Wrong peer addresses configured

**Verify network:**
```bash
# Check if nodes can reach each other
docker exec raft-node1 ping -c 2 raft-node2
docker exec raft-node1 curl http://raft-node2:50052/status
```

### Issue: No Leader Elected

**Possible causes:**
1. All nodes starting at exact same time (split vote)
2. Network partition
3. Timeout too short

**Solution:**
```bash
# Manually trigger election on one node
curl -X POST http://localhost:50051/trigger-election

# Check if it became leader
curl http://localhost:50051/status | jq '.state'
```

---

## 📝 Complete Fix Summary

### Files Modified: 1
- ✅ [raft/raft_node.py](raft/raft_node.py)
  - Added `import httpx` (line 4)
  - Added `from fastapi import FastAPI, Request` (line 7)
  - Replaced fake voting with real HTTP communication (lines 46-93)
  - Added `/request-vote` endpoint (lines 108-131)

### Files Created: 2
- ✅ [fix-raft-leader.sh](fix-raft-leader.sh) - Quick fix script
- ✅ [RAFT_FIX_BEFORE_AFTER.md](RAFT_FIX_BEFORE_AFTER.md) - This documentation

### Dependencies: No Changes
- httpx was already in requirements-raft.txt (line 13)
- No new dependencies needed

### Build Time: 2-3 minutes
### Breaking Changes: None
### Backward Compatible: Yes (endpoints unchanged, just implementation fixed)

---

## 🎯 Quick Commands Reference

**Apply fix:**
```bash
bash fix-raft-leader.sh
```

**Check node status:**
```bash
curl http://localhost:50051/status | jq '.'
curl http://localhost:50052/status | jq '.'
curl http://localhost:50053/status | jq '.'
```

**View logs:**
```bash
docker compose -f docker-compose.combined.yml logs -f raft-node1
```

**Trigger manual election:**
```bash
curl -X POST http://localhost:50051/trigger-election
```

**Restart Raft nodes:**
```bash
docker compose -f docker-compose.combined.yml restart raft-node1 raft-node2 raft-node3
```

**Full rebuild:**
```bash
docker compose -f docker-compose.combined.yml down
docker compose -f docker-compose.combined.yml up -d --build
```

---

## ✅ Verification Checklist

After applying the fix:

- [ ] Only ONE node shows `"state": "leader"`
- [ ] Other nodes show `"state": "follower"`
- [ ] Logs show vote requests and grants
- [ ] Logs show "Got vote from" messages
- [ ] No random voting messages
- [ ] Leader election completes in < 10 seconds
- [ ] Re-elections work correctly

---

## 🎉 Summary

**Problem:** All 3 Raft nodes claiming to be "leader" simultaneously

**Root Cause:** Fake random voting - no actual peer communication

**Solution:**
1. Added real HTTP communication using httpx
2. Nodes now request votes from peers via `/request-vote` endpoint
3. Only node with majority votes becomes leader

**Result:** ✅ Proper Raft consensus! Only ONE leader elected!

---

**Fixed:** 2025-11-13
**Rebuild Required:** Yes (use `bash fix-raft-leader.sh`)
**Estimated Fix Time:** 3 minutes
**Status:** ✅ Ready to test!
