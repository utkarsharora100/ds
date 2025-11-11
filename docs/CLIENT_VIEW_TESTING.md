# 🧪 Client View Testing Quick Reference

## Quick Test Commands

### 1. Check Server Status
```bash
curl http://localhost:9000/health
```

### 2. Register New User
```bash
curl -X POST http://localhost:9000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"YOUR_USERNAME","password":"YOUR_PASSWORD"}'
```

### 3. Login and Get Token
```bash
curl -X POST http://localhost:9000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"YOUR_USERNAME","password":"YOUR_PASSWORD"}'
```
Save the token from response for next steps.

### 4. View Available Movies
```bash
curl "http://localhost:9000/data/movies?token=YOUR_TOKEN"
```

### 5. Book a Ticket
```bash
curl -X POST http://localhost:9000/business \
  -H "Content-Type: application/json" \
  -d '{
    "requestId":"booking-'$(date +%s)'",
    "payload":{
      "type":"book_seat",
      "data":{
        "movie":"MOVIE_NAME",
        "city":"CITY_NAME",
        "seats":2
      }
    },
    "context":{"token":"YOUR_TOKEN"}
  }'
```

### 6. View Your Bookings
```bash
curl "http://localhost:9000/data/bookings?token=YOUR_TOKEN"
```

## Automated Demo

Run the complete demonstration:
```bash
./demo_client_view.sh
```

## GUI Application

### Install Dependencies
```bash
pip install customtkinter requests
```

### Run Application
```bash
python app.py
```

### Test Flow
1. Click "Register New Account"
2. Enter username and password
3. Login with credentials
4. Browse movies in left panel
5. Select movie and enter seats
6. Click "Book Selected Movie"
7. Check booking in right panel

## Expected Results

### Health Check
```json
{"status":"healthy","service":"application-server"}
```

### Registration
```json
{"status":"success","message":"User created"}
```

### Login
```json
{
  "status":"success",
  "token":"uuid-string",
  "user":"username"
}
```

### Get Movies
```json
{
  "status":"success",
  "data":[
    {"id":1,"data":{"movie":"Inception","city":"Delhi"}},
    {"id":2,"data":{"movie":"The Matrix","city":"Mumbai"}}
  ]
}
```

### Book Ticket
```json
{
  "status":"success",
  "booking_id":"uuid-string"
}
```

## Troubleshooting

### Service Not Running
```bash
sudo docker compose up -d
sudo docker compose ps
```

### Port Already in Use
```bash
sudo lsof -i :9000
kill <PID>
```

### View Logs
```bash
sudo docker compose logs app-server --tail=50
```

## Admin Functions (for setup)

### Add Movies
```bash
# Login as admin
ADMIN_TOKEN=$(curl -s -X POST http://localhost:9000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123"}' | grep -o '"token":"[^"]*"' | cut -d'"' -f4)

# Add movie
curl -X POST http://localhost:9000/add_movie \
  -H "Content-Type: application/json" \
  -d "{\"token\":\"$ADMIN_TOKEN\",\"movie\":\"Movie Name\",\"city\":\"City Name\"}"
```

## Full Documentation

For complete documentation, see [CLIENT_VIEW.md](CLIENT_VIEW.md)
