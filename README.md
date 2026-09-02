# Real-Time Notification System

A full-stack real-time notification system built with FastAPI, PostgreSQL, Redis Pub/Sub, WebSockets, and JavaScript.

## Features

- User registration and JWT authentication
- Secure user-specific notifications
- Create, read, update, and delete notifications
- Notification filtering by read/unread status
- Pagination
- Real-time notification delivery using WebSockets
- Redis Pub/Sub for event distribution
- Multiple WebSocket connections per user
- Browser notifications
- Notification sound
- Mark individual notifications as read
- Mark all notifications as read
- Delete individual notifications
- Delete all notifications
- Automatic WebSocket reconnection
- PostgreSQL persistence
- Alembic database migrations
- Docker Compose support
- Automated API tests

## Tech Stack

### Backend
- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Redis
- Redis Pub/Sub
- WebSockets
- JWT
- Pydantic

### Frontend
- HTML
- CSS
- JavaScript
- WebSocket API

### Infrastructure
- Docker
- Docker Compose

## Architecture

```text
                    ┌──────────────────┐
                    │     Frontend     │
                    │ HTML/CSS/JS      │
                    └────────┬─────────┘
                             │
                  HTTP       │       WebSocket
                             │
                             ▼
                    ┌──────────────────┐
                    │     FastAPI      │
                    │     Backend      │
                    └───────┬──────────┘
                            │
             ┌──────────────┼──────────────┐
             │              │              │
             ▼              ▼              ▼
       ┌──────────┐   ┌──────────┐   ┌──────────────┐
       │PostgreSQL│   │  Redis   │   │ WebSocket    │
       │ Database │   │ Pub/Sub  │   │ Connection   │
       └──────────┘   └─────┬────┘   │   Manager    │
                            │        └──────┬───────┘
                            │               │
                            └───────────────┘
                                    │
                                    ▼
                               Frontend