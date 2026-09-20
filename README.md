# 🛎️ Grand Royale - Automated Hotel Service Request System

An Autonomous **Agentic AI Hotel Service Request & Operations Management System** built with **Python, Gradio, LangGraph, and SQLite**.

---

## 🌟 Key Features

### 1. 🤖 LangGraph Agentic AI Engine
- **Autonomous Intent Parser**: Detects whether the guest wants to create a request, track status, cancel a ticket, ask about hotel amenities/policies, or engage in general conversation.
- **Intelligent Department Classifier**: Automatically routes requests to **Housekeeping**, **Room Service**, **Maintenance**, **Laundry**, or **Concierge**.
- **Dynamic Priority Engine**: Assigns priority levels (**Urgent**, **High**, **Medium**, **Low**) and SLA Estimated Time of Arrival (ETA) based on urgency triggers (e.g. plumbing leaks/lockouts = *Urgent* / 10-15m; hot meals = *High* / 25-30m; towels = *Medium* / 15-20m).
- **Dual-Engine Architecture**: Operates with zero API keys using built-in semantic pattern engines, with plug-and-play support for Google Gemini & OpenAI LLMs.

### 2. 🛎️ Interactive Guest Concierge Portal
- **Guest Authentication Simulation**: Quick dropdown to simulate being in Room 101 through Room 505 with authentic VIP tiers.
- **Conversational Chatbot**: Natural language dialogue with rich markdown confirmation cards.
- **Quick Action Pills**: One-click prompt shortcuts for common hotel requests.
- **Live Room Status Widget**: Instant sidebar updates showing guest profile details and active requests.

### 3. 🔍 Live Request Tracking & Lifecycle Manager
- **Visual Progress Timeline**: Step tracker showing `Received ➔ Assigned ➔ In Progress ➔ Completed`.
- **Search by Ticket or Room**: Instant lookup for any ticket (e.g. `HTL-1082`) or room number.
- **One-Click Cancellation**: Guests can cancel active requests with immediate database synchronization.

### 4. 📊 Real-Time Staff Operations Dashboard
- **Live KPI Stat Cards**: Total requests, pending dispatches, in-progress tasks, completed requests, and active urgent issues.
- **Multi-Criteria Filtering**: Filter live tickets by Department, Status, Priority, or search query.
- **Ticket Dispatch & Action Panel**: Update statuses, assign specific staff members, and record internal notes.

### 5. 🏨 Services Catalog & Hotel Knowledge Base
- **Complete Hotel Amenities**: Visual directory of services across all departments with standard delivery ETAs.
- **Interactive FAQ Engine**: Instant answers for Wi-Fi passwords, pool/gym hours, buffet timings, parking, and pet policies.

---

## 🏗️ Project Structure

```
├── app.py              # Main Gradio multi-tab web application
├── agent_graph.py      # LangGraph StateGraph & Agentic AI workflows
├── database.py         # SQLite database schema, CRUD methods, and seed data
├── ui_theme.py         # 5-Star Luxury styling, CSS tokens, and glassmorphic cards
├── test_suite.py       # Automated unit & integration tests
├── requirements.txt    # Pinned Python package dependencies
└── hotel_service.db    # Auto-generated SQLite database
```

---

## 🚀 Quick Start Guide

### 1. Run the Application
```bash
python app.py
```
Open your browser and navigate to: `http://127.0.0.1:7860`

### 2. Run the Automated Test Suite
```bash
python -m unittest test_suite.py
```

---

## 🧪 Sample Test Prompts to Try

| Scenario | Sample Prompt | Expected Routing | Priority |
| :--- | :--- | :--- | :--- |
| **Housekeeping** | *"Can you send 2 fresh bath towels and shampoo to room 204?"* | `Housekeeping` | `Medium` (~15m) |
| **Emergency Maintenance** | *"Emergency! Water is leaking from the AC in bathroom of 312!"* | `Maintenance` | `Urgent` (~10m) |
| **Room Service** | *"I'd like to order 1 Wagyu Burger, Truffle Fries, and a Sparkling Water."* | `Room Service` | `High` (~25m) |
| **Express Laundry** | *"Please pick up my suit for express dry cleaning before my 6 PM meeting."* | `Laundry` | `High` (~60m) |
| **Status Inquiry** | *"What is the status of ticket #HTL-1082?"* | `Status Query` | N/A |
| **Hotel FAQ** | *"What time is the breakfast buffet and where is the rooftop pool?"* | `Hotel FAQ` | N/A |
| **Cancellation** | *"Cancel ticket #HTL-1082, I don't need it anymore."* | `Cancellation` | N/A |

---

## 🛡️ Technology Stack
- **AI / Agentic Framework**: [LangGraph](https://github.com/langchain-ai/langgraph) & [LangChain](https://github.com/langchain-ai/langchain)
- **Frontend / UI**: [Gradio](https://www.gradio.app/)
- **Database**: SQLite3
- **Language**: Python 3.13+
