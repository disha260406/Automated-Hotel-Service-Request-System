"""
Hotel Service Request System - LangGraph Agentic AI Engine
Defines the StateGraph workflow, routing nodes, priority assessment, and luxury response synthesis.
"""

import os
import re
from typing import Dict, Any, List, Optional, TypedDict, Annotated, Tuple
from langgraph.graph import StateGraph, END
import database

# Optional LangChain / LLM imports
try:
    from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_openai import ChatOpenAI
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False


class AgentState(TypedDict):
    """LangGraph State representation for the Hotel AI Agent."""
    messages: List[Dict[str, str]]
    user_input: str
    active_room: str
    extracted_room: Optional[str]
    guest_name: Optional[str]
    intent: str
    service_type: Optional[str]
    priority: str
    eta_minutes: int
    ticket_id: Optional[str]
    action_result: Optional[Dict[str, Any]]
    agent_response: str
    card_data: Optional[Dict[str, Any]]
    reasoning_chain: List[str]


# -------------------------------------------------------------
# Classification & Parsing Helpers (Agentic Reasoning Tools)
# -------------------------------------------------------------

SERVICE_KEYWORDS = {
    "Maintenance": [
        "ac", "air condition", "air conditioning", "heater", "heating", "leak", "leaking", "pipe",
        "plumb", "plumbing", "faucet", "tap", "shower", "water", "toilet", "clog", "clogged",
        "drain", "lock", "keycard", "key card", "door", "tv", "television", "remote", "wifi",
        "bulb", "light", "socket", "power", "electricity", "safe", "smell", "broken", "repair", "fix"
    ],
    "Housekeeping": [
        "towel", "towels", "linen", "sheet", "pillow", "blanket", "duvet", "clean", "cleaning",
        "turn down", "turndown", "trash", "dustbin", "shampoo", "soap", "toiletries", "robe",
        "bathrobe", "slippers", "bed", "vacuum", "mop", "sweep", "refresh", "dental kit"
    ],
    "Room Service": [
        "food", "eat", "dining", "dinner", "lunch", "breakfast", "burger", "pizza", "sandwich",
        "salad", "coffee", "latte", "espresso", "cappuccino", "tea", "drink", "water bottle",
        "sparkling water", "snack", "order", "dessert", "cocktail", "wine", "champagne", "ice bucket", "menu"
    ],
    "Laundry": [
        "laundry", "dry clean", "dry cleaning", "wash", "washing", "iron", "ironing", "press",
        "pressing", "steam", "suit", "shirt", "dress", "trousers", "shoe shine", "polish", "garment"
    ],
    "Concierge": [
        "cab", "taxi", "chauffeur", "transfer", "airport", "reservation", "booking", "restaurant table",
        "tour", "sightseeing", "luggage", "baggage", "bellboy", "valet", "car"
    ]
}

URGENT_TRIGGERS = [
    "leak", "leaking", "flooding", "flood", "smoke", "fire", "spark", "burning",
    "locked out", "lock broken", "stuck", "emergency", "urgent", "asap", "immediately",
    "overflowing", "no water", "extreme heat", "freezing"
]

HIGH_PRIORITY_TRIGGERS = [
    "food", "breakfast", "dinner", "hungry", "express", "flight", "meeting", "important",
    "dry cleaning today", "safe locked", "no key"
]

STATUS_KEYWORDS = [
    "status", "track", "tracking", "where is", "update on", "check on", "how long",
    "what happened to", "is it ready", "progress", "ticket"
]

CANCEL_KEYWORDS = [
    "cancel", "abort", "don't need", "do not need", "withdraw", "stop request", "never mind"
]


def extract_room_number(text: str, default_room: str = "101") -> str:
    """Extracts room number from user input or falls back to active room."""
    match = re.search(r'\b(?:room|rm|suite|in)\s*#?\s*(\d{3,4})\b', text, re.IGNORECASE)
    if match:
        return match.group(1)
    
    # Check for standalone 3-digit room number
    digits = re.findall(r'\b([1-5]\d{2})\b', text)
    if digits:
        return digits[0]

    return default_room or "101"


def extract_ticket_id(text: str) -> Optional[str]:
    """Extracts ticket ID (e.g. HA-1234, HTL-1234, #1234) from user input."""
    match_prefix = re.search(r'\b(HA|HTL)-(\d{4})\b', text, re.IGNORECASE)
    if match_prefix:
        return f"{match_prefix.group(1).upper()}-{match_prefix.group(2)}"
    
    match_hash = re.search(r'#(\d{4})\b', text)
    if match_hash:
        return f"HA-{match_hash.group(1)}"

    match_digits = re.search(r'\b(?:ticket|tracking|request)\s*#?\s*(\d{4})\b', text, re.IGNORECASE)
    if match_digits:
        return f"HA-{match_digits.group(1)}"

    return None


def classify_intent(text: str) -> str:
    """Classifies the primary intent of the guest's message."""
    t = text.lower()
    
    # Cancellation check
    if any(k in t for k in CANCEL_KEYWORDS):
        return "cancel_request"
    
    # Status tracking check
    if any(k in t for k in STATUS_KEYWORDS) or "htl-" in t:
        return "query_status"
    
    # FAQ check
    faq_match = database.search_hotel_knowledge(t)
    if faq_match and ("what" in t or "when" in t or "where" in t or "how" in t or "policy" in t or "wifi" in t or "pool" in t or "gym" in t or "check" in t or "time" in t or "cost" in t):
        # Verify it's not a direct service order like "can I order breakfast"
        if not any(word in t for word in ["bring", "send", "need", "deliver", "order", "fix", "repair"]):
            return "hotel_faq"

    # Service Request creation check
    for dept, keywords in SERVICE_KEYWORDS.items():
        if any(k in t for k in keywords):
            return "create_request"
            
    # Greeting / General Chat
    if any(g in t for g in ["hi", "hello", "hey", "good morning", "good evening", "thank", "thanks", "who are you", "help"]):
        return "general_chat"
        
    return "create_request"


def classify_service(text: str) -> Tuple[str, str, int]:
    """
    Classifies service category, priority, and estimated completion time in minutes.
    Returns: (service_type, priority, eta_minutes)
    """
    t = text.lower()
    
    # 1. Department Detection
    scores = {dept: 0 for dept in SERVICE_KEYWORDS}
    for dept, keywords in SERVICE_KEYWORDS.items():
        for k in keywords:
            if k in t:
                scores[dept] += 2 if len(k) > 4 else 1

    matched_dept = max(scores, key=scores.get)
    if scores[matched_dept] == 0:
        matched_dept = "Housekeeping"  # sensible default

    # 2. Priority Calculation
    if any(u in t for u in URGENT_TRIGGERS):
        priority = "Urgent"
        eta = 10 if matched_dept == "Maintenance" else 15
    elif any(h in t for h in HIGH_PRIORITY_TRIGGERS):
        priority = "High"
        eta = 25 if matched_dept == "Room Service" else 30
    elif matched_dept == "Laundry":
        priority = "Medium"
        eta = 60
    elif matched_dept == "Maintenance":
        priority = "Medium"
        eta = 20
    else:
        priority = "Medium"
        eta = 20

    # Low priority adjustments
    if any(l in t for l in ["whenever", "no rush", "later", "pillow", "extra slippers"]):
        priority = "Low"
        eta = 35

    return matched_dept, priority, eta


# -------------------------------------------------------------
# LangGraph Nodes
# -------------------------------------------------------------

def node_parse_intent(state: AgentState) -> AgentState:
    """Node 1: Analyzes user input, extracts room number, guest details, and intent."""
    user_input = state["user_input"]
    active_room = state.get("active_room", "101")
    
    reasoning = list(state.get("reasoning_chain", []))
    reasoning.append(f"🔍 [Intent Parser]: Analyzing input '{user_input}'")

    room = extract_room_number(user_input, active_room)
    ticket_id = extract_ticket_id(user_input)
    intent = classify_intent(user_input)

    guest = database.get_guest_by_room(room)
    guest_name = guest["name"] if guest else "Valued Guest"
    vip_status = guest["vip_status"] if guest else "Standard"

    reasoning.append(f"🏨 [Room & Guest]: Resolved Room #{room} | Guest: {guest_name} ({vip_status})")
    reasoning.append(f"🎯 [Identified Intent]: {intent.upper()}")

    return {
        **state,
        "extracted_room": room,
        "guest_name": guest_name,
        "ticket_id": ticket_id,
        "intent": intent,
        "reasoning_chain": reasoning
    }


def node_classify_service_and_priority(state: AgentState) -> AgentState:
    """Node 2: Determines the specific department, priority level, and ETA."""
    reasoning = list(state.get("reasoning_chain", []))
    intent = state.get("intent", "create_request")
    user_input = state["user_input"]

    if intent == "create_request":
        service_type, priority, eta = classify_service(user_input)
        reasoning.append(f"🏷️ [Service Classifier]: Routed to '{service_type}' | Priority: '{priority}' | ETA: {eta} mins")
    else:
        service_type = None
        priority = "Medium"
        eta = 0
        reasoning.append(f"ℹ️ [Workflow Note]: Non-creation intent ({intent}), skipping service ticket classification.")

    return {
        **state,
        "service_type": service_type,
        "priority": priority,
        "eta_minutes": eta,
        "reasoning_chain": reasoning
    }


def node_execute_action(state: AgentState) -> AgentState:
    """Node 3: Executes database operations according to the classified intent."""
    reasoning = list(state.get("reasoning_chain", []))
    intent = state.get("intent", "create_request")
    room = state.get("extracted_room", "101")
    guest_name = state.get("guest_name", "Valued Guest")
    user_input = state["user_input"]
    ticket_id = state.get("ticket_id")

    action_result = None
    card_data = None

    if intent == "create_request":
        service_type = state.get("service_type", "Housekeeping")
        priority = state.get("priority", "Medium")
        eta = state.get("eta_minutes", 25)

        created = database.create_service_request(
            room_number=room,
            guest_name=guest_name,
            service_type=service_type,
            description=user_input,
            priority=priority,
            eta_minutes=eta
        )
        action_result = created
        card_data = {
            "type": "ticket_created",
            "ticket_id": created["ticket_id"],
            "room_number": room,
            "guest_name": guest_name,
            "service_type": service_type,
            "priority": priority,
            "status": "Pending",
            "eta_minutes": eta,
            "assigned_staff": created["assigned_staff"]
        }
        reasoning.append(f"💾 [DB Action]: Created Ticket #{created['ticket_id']} in SQLite with status 'Pending'.")

    elif intent == "query_status":
        if ticket_id:
            req = database.get_request_by_ticket(ticket_id)
            if req:
                action_result = req
                card_data = {
                    "type": "ticket_found",
                    "ticket_id": req["ticket_id"],
                    "room_number": req["room_number"],
                    "service_type": req["service_type"],
                    "description": req["description"],
                    "priority": req["priority"],
                    "status": req["status"],
                    "assigned_staff": req["assigned_staff"],
                    "eta_minutes": req["eta_minutes"],
                    "created_at": req["created_at"]
                }
                reasoning.append(f"🔍 [DB Query]: Retrieved Ticket #{ticket_id} (Status: {req['status']}).")
            else:
                action_result = {"error": f"Ticket #{ticket_id} not found."}
                reasoning.append(f"⚠️ [DB Query]: Ticket #{ticket_id} does not exist.")
        else:
            # Look for active requests in the current room
            room_requests = database.get_requests_by_room(room)
            action_result = {"room_requests": room_requests}
            reasoning.append(f"🔍 [DB Query]: Found {len(room_requests)} request(s) for Room #{room}.")

    elif intent == "cancel_request":
        if ticket_id:
            success, msg = database.cancel_service_request(ticket_id)
            action_result = {"success": success, "message": msg, "ticket_id": ticket_id}
            card_data = {"type": "ticket_cancelled", "ticket_id": ticket_id, "success": success}
            reasoning.append(f"🚫 [DB Action]: Cancel ticket #{ticket_id} -> {msg}")
        else:
            # Check most recent active request for the room
            room_requests = database.get_requests_by_room(room)
            active_reqs = [r for r in room_requests if r["status"] in ["Pending", "In Progress"]]
            if active_reqs:
                target_ticket = active_reqs[0]["ticket_id"]
                success, msg = database.cancel_service_request(target_ticket)
                action_result = {"success": success, "message": msg, "ticket_id": target_ticket}
                card_data = {"type": "ticket_cancelled", "ticket_id": target_ticket, "success": success}
                reasoning.append(f"🚫 [DB Action]: Cancelled latest active ticket #{target_ticket} for Room #{room}.")
            else:
                action_result = {"success": False, "message": f"No active pending request found to cancel for Room #{room}."}
                reasoning.append(f"ℹ️ [DB Action]: No pending requests found for Room #{room}.")

    elif intent == "hotel_faq":
        faq_matches = database.search_hotel_knowledge(user_input)
        action_result = {"faqs": faq_matches}
        reasoning.append(f"📖 [Knowledge Base]: Matched {len(faq_matches)} FAQ result(s).")

    elif intent == "general_chat":
        action_result = {"greeting": True}
        reasoning.append("💬 [Concierge Mode]: Generating luxury concierge greeting.")

    return {
        **state,
        "action_result": action_result,
        "card_data": card_data,
        "reasoning_chain": reasoning
    }


def node_synthesize_response(state: AgentState) -> AgentState:
    """Node 4: Synthesizes a polite, 5-star luxury concierge response."""
    reasoning = list(state.get("reasoning_chain", []))
    intent = state.get("intent", "create_request")
    room = state.get("extracted_room", "101")
    guest_name = state.get("guest_name", "Valued Guest")
    action_result = state.get("action_result", {})
    card_data = state.get("card_data")

    priority_emojis = {
        "Urgent": "🔴 **[URGENT]**",
        "High": "🟠 **[HIGH]**",
        "Medium": "🟡 **[MEDIUM]**",
        "Low": "🟢 **[LOW]**"
    }

    if intent == "create_request" and card_data:
        tid = card_data["ticket_id"]
        dept = card_data["service_type"]
        prio = card_data["priority"]
        eta = card_data["eta_minutes"]
        staff = card_data["assigned_staff"]

        response = (
            f"🛎️ **Grand Azure AI Concierge**: Certainly, {guest_name}!\n\n"
            f"Your **{dept}** request for **Suite #{room}** has been registered in SQLite and dispatched.\n\n"
            f"```\n"
            f"┌────────────────────────────────────────────────────────┐\n"
            f"│  GRAND AZURE SERVICE REQUEST TICKET: #{tid:<17}│\n"
            f"├────────────────────────────────────────────────────────┤\n"
            f"│  Suite:       #{room:<41}│\n"
            f"│  Guest:       {guest_name:<41}│\n"
            f"│  Department:  {dept:<41}│\n"
            f"│  Priority:    {prio:<41}│\n"
            f"│  Status:      Pending (Assigned to {staff})│\n"
            f"│  Est. Arrival: ~{eta} minutes                         │\n"
            f"└────────────────────────────────────────────────────────┘\n"
            f"```\n"
            f"Our team has been auto-dispatched. You can track this request in real-time with Ticket **#{tid}**."
        )

    elif intent == "query_status":
        if "error" in action_result:
            response = f"⚠️ {action_result['error']}\nPlease double check the ticket ID or let me know your room number to look up active requests."
        elif card_data and card_data.get("type") == "ticket_found":
            tid = card_data["ticket_id"]
            dept = card_data["service_type"]
            status = card_data["status"]
            desc = card_data["description"]
            staff = card_data["assigned_staff"]
            eta = card_data["eta_minutes"]

            status_icon = "⏳" if status == "Pending" else "🔄" if status == "In Progress" else "✅" if status == "Completed" else "🚫"

            response = (
                f"📋 **Status Update for Ticket #{tid}**:\n\n"
                f"- **Room**: #{card_data['room_number']}\n"
                f"- **Department**: {dept}\n"
                f"- **Request**: *\"{desc}\"*\n"
                f"- **Current Status**: {status_icon} **{status}**\n"
                f"- **Assigned Handler**: {staff}\n"
                f"- **Estimated Delivery**: ~{eta} minutes\n\n"
                f"Is there anything else I can coordinate for you, {guest_name}?"
            )
        elif "room_requests" in action_result:
            reqs = action_result["room_requests"]
            if reqs:
                req_lines = []
                for r in reqs[:4]:
                    st_icon = "⏳" if r["status"] == "Pending" else "🔄" if r["status"] == "In Progress" else "✅" if r["status"] == "Completed" else "🚫"
                    req_lines.append(f"- **#{r['ticket_id']}** ({r['service_type']}): *{r['description'][:40]}...* ➔ {st_icon} **{r['status']}**")
                response = (
                    f"📋 Here are the recent service requests for **Room #{room}** ({guest_name}):\n\n"
                    + "\n".join(req_lines)
                    + "\n\nFeel free to ask for detailed updates on any ticket above."
                )
            else:
                response = f"ℹ️ There are currently no active service requests on file for **Room #{room}**."

    elif intent == "cancel_request":
        if action_result.get("success"):
            tid = action_result.get("ticket_id", "")
            response = f"✅ **Request Cancelled**: {action_result['message']}\nOur team has updated the service schedule. Please let us know if you need anything else!"
        else:
            response = f"⚠️ {action_result.get('message', 'Unable to cancel the requested ticket.')}"

    elif intent == "hotel_faq":
        faqs = action_result.get("faqs", [])
        if faqs:
            best_faq = faqs[0]
            response = (
                f"🏨 **Hotel service systemHotel Information**:\n\n"
                f"**{best_faq['question']}**\n\n"
                f"{best_faq['answer']}\n\n"
                f"*Category: {best_faq['category']} | Dial 0 for Front Desk assistance.*"
            )
        else:
            response = "I am happy to assist with any hotel inquiries or service requests. You may dial 0 for 24/7 Front Desk support."

    else:
        # General Concierge Welcome
        response = (
            f"✨ **Welcome to The Grand Azure AI Concierge**, {guest_name} (Suite #{room})!\n\n"
            f"I am your 24/7 automated agentic hotel assistant. How may I assist you today?\n\n"
            f"**Popular Guest Services**:\n"
            f"• 🧹 **Housekeeping**: Extra towels, pillows, turn-down service, room cleaning\n"
            f"• 🍽️ **Room Service**: Continental breakfast, gourmet dinners, beverages, ice\n"
            f"• 🔧 **Maintenance**: AC adjustments, plumbing, Wi-Fi support, repairs\n"
            f"• 👔 **Laundry**: Express dry-cleaning, steam pressing, garment care\n"
            f"• 🔍 **Tracking**: Instant real-time updates on your existing requests"
        )

    reasoning.append("✨ [Response Synthesizer]: Formatted luxury concierge message output.")

    return {
        **state,
        "agent_response": response,
        "reasoning_chain": reasoning
    }


# -------------------------------------------------------------
# LangGraph Graph Construction
# -------------------------------------------------------------

def build_hotel_agent_graph():
    """Builds and compiles the LangGraph StateGraph."""
    graph = StateGraph(AgentState)

    # Add Nodes
    graph.add_node("intent_parser", node_parse_intent)
    graph.add_node("service_classifier", node_classify_service_and_priority)
    graph.add_node("action_executor", node_execute_action)
    graph.add_node("response_synthesizer", node_synthesize_response)

    # Define Edges / Transitions
    graph.set_entry_point("intent_parser")
    graph.add_edge("intent_parser", "service_classifier")
    graph.add_edge("service_classifier", "action_executor")
    graph.add_edge("action_executor", "response_synthesizer")
    graph.add_edge("response_synthesizer", END)

    return graph.compile()


# Singleton compiled graph
HOTEL_AGENT_GRAPH = build_hotel_agent_graph()


def process_guest_message(
    user_message: str,
    active_room: str = "101",
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    Main entrypoint invoked by Gradio UI or API.
    Executes the compiled LangGraph workflow.
    """
    history = conversation_history or []
    
    initial_state: AgentState = {
        "messages": history,
        "user_input": user_message.strip(),
        "active_room": str(active_room).strip(),
        "extracted_room": None,
        "guest_name": None,
        "intent": "create_request",
        "service_type": None,
        "priority": "Medium",
        "eta_minutes": 25,
        "ticket_id": None,
        "action_result": None,
        "agent_response": "",
        "card_data": None,
        "reasoning_chain": []
    }

    final_state = HOTEL_AGENT_GRAPH.invoke(initial_state)
    return {
        "response": final_state["agent_response"],
        "intent": final_state["intent"],
        "service_type": final_state["service_type"],
        "priority": final_state["priority"],
        "eta_minutes": final_state["eta_minutes"],
        "room_number": final_state["extracted_room"],
        "guest_name": final_state["guest_name"],
        "card_data": final_state["card_data"],
        "reasoning_chain": final_state["reasoning_chain"]
    }
