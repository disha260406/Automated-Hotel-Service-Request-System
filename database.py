"""
Hotel Service Request System - SQLite Database Layer
Handles all persistent storage, schema management, and CRUD operations.
"""

import os
import shutil
import sqlite3
import datetime
import random
from typing import List, Dict, Any, Optional, Tuple

# Handle serverless/read-only environment (e.g., Vercel, AWS Lambda)
if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    DB_DIR = "/tmp"
    DB_PATH = os.path.join(DB_DIR, "hotel_service.db")
    SOURCE_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hotel_service.db")
    if not os.path.exists(DB_PATH) and os.path.exists(SOURCE_DB):
        try:
            shutil.copy2(SOURCE_DB, DB_PATH)
        except Exception:
            pass
else:
    DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hotel_service.db")


def get_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with Row factory enabled."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initializes database tables and populates seed data if empty."""
    conn = get_connection()
    cursor = conn.cursor()

    # Guests table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS guests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            phone TEXT,
            check_in_date TEXT,
            check_out_date TEXT,
            vip_status TEXT DEFAULT 'Standard'
        )
    """)

    # Service Requests table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS service_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT UNIQUE NOT NULL,
            room_number TEXT NOT NULL,
            guest_name TEXT NOT NULL,
            service_type TEXT NOT NULL,
            description TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            assigned_staff TEXT DEFAULT 'Unassigned',
            notes TEXT DEFAULT '',
            eta_minutes INTEGER DEFAULT 30,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    # Service Catalog
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS service_catalog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            item_name TEXT NOT NULL,
            standard_time_minutes INTEGER DEFAULT 25,
            base_priority TEXT DEFAULT 'Medium',
            description TEXT
        )
    """)

    # Hotel Knowledge / FAQ
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hotel_knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            keywords TEXT NOT NULL
        )
    """)

    # Request Audit Logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS request_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT NOT NULL,
            action TEXT NOT NULL,
            actor TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            comment TEXT
        )
    """)

    conn.commit()

    # Check if seed data exists
    cursor.execute("SELECT COUNT(*) FROM guests")
    if cursor.fetchone()[0] == 0:
        _populate_seed_data(conn)

    conn.close()


def _populate_seed_data(conn: sqlite3.Connection) -> None:
    """Populates realistic seed data for guests, service catalog, FAQs, and sample requests."""
    cursor = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    today = datetime.date.today()

    # 1. Seed Guests
    sample_guests = [
        ("412", "Eleanor Vance", "+1-555-0412", str(today), str(today + datetime.timedelta(days=4)), "VIP Titanium"),
        ("101", "ramesh kumar", "+1-555-0101", str(today), str(today + datetime.timedelta(days=3)), "VIP Platinum"),
        ("204", "Marcus Aurelius", "+1-555-0204", str(today), str(today + datetime.timedelta(days=5)), "VIP Diamond"),
        ("205", "Michael Brown", "+1-555-0205", str(today), str(today + datetime.timedelta(days=1)), "Standard"),
        ("312", "Chloe Tremblay", "+1-555-0312", str(today), str(today + datetime.timedelta(days=2)), "Standard"),
        ("318", "Kenji Sato", "+1-555-0318", str(today - datetime.timedelta(days=1)), str(today + datetime.timedelta(days=3)), "Standard"),
        ("604", "Elena Rostova", "+1-555-0604", str(today), str(today + datetime.timedelta(days=5)), "VIP Diamond"),
        ("PH-02", "Lord Alistair Sterling", "+1-555-0902", str(today), str(today + datetime.timedelta(days=7)), "VIP Royal"),
        ("102", "Sophia Martinez", "+1-555-0102", str(today), str(today + datetime.timedelta(days=2)), "Standard"),
        ("203", "James Chen", "+1-555-0203", str(today - datetime.timedelta(days=1)), str(today + datetime.timedelta(days=4)), "Standard"),
        ("301", "Amara Okafor", "+1-555-0301", str(today - datetime.timedelta(days=2)), str(today + datetime.timedelta(days=2)), "Standard"),
        ("501", "Noah Al-Mansoor", "+1-555-0501", str(today), str(today + datetime.timedelta(days=4)), "VIP Diamond")
    ]
    cursor.executemany(
        "INSERT INTO guests (room_number, name, phone, check_in_date, check_out_date, vip_status) VALUES (?, ?, ?, ?, ?, ?)",
        sample_guests
    )

    # 2. Seed Service Catalog
    catalog_items = [
        # Housekeeping
        ("Housekeeping", "Fresh Bath Towels & Linens", 15, "Medium", "Set of 2 plush bath towels, hand towels, and bath mat"),
        ("Housekeeping", "Full Room Cleaning & Turn-down", 45, "Medium", "Comprehensive room sanitation, bed linen refresh, and trash disposal"),
        ("Housekeeping", "Luxury Toiletries Kit", 15, "Low", "Hermès / Molton Brown shampoo, conditioner, body wash, and dental kit"),
        ("Housekeeping", "Feather / Memory Foam Pillow", 20, "Low", "Hypoallergenic ergonomic pillows from the pillow menu"),
        ("Housekeeping", "Extra Duvet & Blanket", 20, "Low", "Plush goose-down duvet and warm thermal blanket"),
        ("Housekeeping", "Sanitary Waste Disposal", 20, "Medium", "Immediate removal of room trash and bathroom bins"),

        # Room Service / Dining
        ("Room Service", "The Grand Continental Breakfast", 30, "High", "Artisanal croissants, farm eggs, seasonal berries, fresh OJ, and artisanal coffee"),
        ("Room Service", "Artisan Wagyu Burger & Truffle Fries", 35, "High", "Grilled wagyu beef, aged cheddar, caramelized onions, brioche bun"),
        ("Room Service", "Fresh Mediterranean Salad", 25, "Medium", "Burrata, heirloom tomatoes, balsamic glaze, pine nuts"),
        ("Room Service", "Midnight Snack Platter", 25, "Medium", "Assorted artisanal cheeses, charcuterie, crackers, and grapes"),
        ("Room Service", "Mineral & Sparkling Water Crate", 15, "Medium", "San Pellegrino & Acqua Panna glass bottles with ice bucket"),
        ("Room Service", "Espresso / Cappuccino Bar", 15, "Medium", "Freshly pulled double espresso or velvety oat milk cappuccino"),

        # Maintenance
        ("Maintenance", "AC / Climate Control Repair", 20, "Urgent", "Fixing HVAC thermostat temperature, airflow, or unusual noise"),
        ("Maintenance", "Plumbing / Water Leakage Fix", 15, "Urgent", "Immediate repair of leaking faucets, pipes, showerheads, or toilets"),
        ("Maintenance", "Keycard & Door Lock Malfunction", 10, "Urgent", "Emergency lock battery replacement or reprogramming"),
        ("Maintenance", "Smart TV / Wi-Fi Connectivity Fix", 25, "Medium", "Troubleshooting streaming apps, HDMI inputs, or room router signal"),
        ("Maintenance", "Light Bulb & Electrical Socket Replacement", 30, "Medium", "Changing blown lighting fixtures or testing power outlets"),
        ("Maintenance", "Safe Lockout & Reset", 15, "High", "Security team override and master keycode reset for in-room safe"),

        # Laundry & Dry Cleaning
        ("Laundry", "Express Same-Day Dry Cleaning", 120, "High", "Suits, blazers, evening gowns professionally dry-cleaned and pressed"),
        ("Laundry", "Steam Pressing & Ironing", 30, "Medium", "Crease-free steam iron for shirts, trousers, and dresses"),
        ("Laundry", "Standard Wash & Fold Service", 180, "Low", "Full bag garment washing, tumble drying, and neat folding"),
        ("Laundry", "Shoe Shine & Leather Polish", 45, "Low", "Professional buffing and buff-wax polish for dress shoes"),

        # Concierge
        ("Concierge", "Airport Chauffeur & Luxury Transfer", 60, "High", "Private Mercedes S-Class or Cadillac Escalade booking"),
        ("Concierge", "Fine Dining Table Reservation", 30, "Medium", "Securing priority tables at top Michelin-starred local restaurants"),
        ("Concierge", "Luggage Storage & Bellboy Assistance", 15, "Medium", "Baggage collection, safe storage, or transit assistance")
    ]
    cursor.executemany(
        "INSERT INTO service_catalog (category, item_name, standard_time_minutes, base_priority, description) VALUES (?, ?, ?, ?, ?)",
        catalog_items
    )

    # 3. Seed Hotel Knowledge & FAQs
    faqs = [
        ("General", "What are the standard Check-in and Check-out timings?", "Standard Check-in is at 3:00 PM and Check-out is at 12:00 PM (Noon). Late check-out until 2:00 PM is complimentary for VIP guests upon request.", "checkin checkout check in check out timing hours time leave arrive"),
        ("Dining", "What are the Breakfast hours and location?", "The Grand Buffet Breakfast is served daily from 6:30 AM to 10:30 AM at 'The Verandah Restaurant' on the Ground Floor. 24/7 in-room dining is also available.", "breakfast food buffet morning eat dining restaurant hours time"),
        ("Amenities", "Where is the Swimming Pool and Fitness Center located?", "The Infinity Pool and 24-hour Fitness Center are located on the 6th Floor Rooftop with panoramic skyline views. Pool hours: 6:00 AM to 10:00 PM.", "pool swimming gym fitness workout rooftop hours towel"),
        ("Internet", "How do I connect to the High-Speed Hotel Wi-Fi?", "Connect to the network 'GrandLuxe_Guest', select your room number, and enter your last name. High-speed 500 Mbps Wi-Fi is complimentary across all rooms.", "wifi internet connection password network speed login"),
        ("Amenities", "Does the hotel have a Spa and Wellness Center?", "Yes! 'The Serenity Spa' is on Level 2, offering Swedish massages, facials, and hot stone therapy from 9:00 AM to 9:00 PM. Dial 4 to book an appointment.", "spa massage facial relax wellness salon hours treatment"),
        ("Concierge", "Is valet parking and EV charging available?", "Complimentary 24/7 Valet Parking is available at the main porte-cochère. Fast Level-3 EV Charging stations are located in the basement garage.", "parking valet car ev charge garage vehicle drive"),
        ("Policies", "What is the hotel smoking and pet policy?", "Our hotel is 100% smoke-free in all indoor guest rooms. Dedicated outdoor cigar lounges are available on the terrace. Well-behaved pets under 15kg are warmly welcomed.", "smoking smoke pet dog cat policy cigarettes")
    ]
    cursor.executemany(
        "INSERT INTO hotel_knowledge (category, question, answer, keywords) VALUES (?, ?, ?, ?)",
        faqs
    )

    # 4. Seed Active Sample Service Requests
    sample_requests = [
        ("HA-8492", "412", "Eleanor Vance", "Maintenance", "HVAC Malfunction & Rattling Sound - Air blowing lukewarm", "Urgent", "In Progress", "Marcus Vance", "Dispatched with HVAC diagnostic tools", 6, now_str, now_str),
        ("HA-8491", "604", "Elena Rostova", "Housekeeping", "Evening Turndown & Extra Down Feather Pillows", "Medium", "In Progress", "Elena Rostova", "Staff en route with pillow selection", 22, now_str, now_str),
        ("HA-8490", "PH-02", "Lord Alistair Sterling", "Room Service", "Wagyu Burger & Vintage Pomerol 2018", "High", "Pending", "Chef Laurent", "Kitchen plating stage", 14, now_str, now_str),
        ("HA-8489", "318", "Kenji Sato", "Laundry", "Express laundry for 2 formal business suits before 8 AM", "High", "In Progress", "Kenji Sato", "Pickup completed, in dry-clean cycle", 45, now_str, now_str),
        ("HA-8488", "205", "Michael Brown", "Housekeeping", "Replenish luxury Hermès toiletries and fresh towels", "Low", "Completed", "Maria Gomez", "Delivered and verified with guest", 0, now_str, now_str),
        ("HA-8487", "101", "ramesh kumar", "Room Service", "The Grand Continental Breakfast with fresh OJ & Espresso", "Medium", "Completed", "F&B Team", "Breakfast served in room", 0, now_str, now_str)
    ]
    cursor.executemany("""
        INSERT INTO service_requests (ticket_id, room_number, guest_name, service_type, description, priority, status, assigned_staff, notes, eta_minutes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_requests)

    conn.commit()


def generate_ticket_id() -> str:
    """Generates a unique luxury ticket ID in format HA-XXXX."""
    conn = get_connection()
    cursor = conn.cursor()
    while True:
        num = random.randint(1000, 9999)
        ticket = f"HA-{num}"
        cursor.execute("SELECT id FROM service_requests WHERE ticket_id = ?", (ticket,))
        if not cursor.fetchone():
            conn.close()
            return ticket


def get_guest_by_room(room_number: str) -> Optional[Dict[str, Any]]:
    """Fetches guest details for a given room number."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM guests WHERE room_number = ?", (room_number.strip(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_rooms() -> List[str]:
    """Returns a list of all registered room numbers."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT room_number FROM guests ORDER BY room_number ASC")
    rooms = [row["room_number"] for row in cursor.fetchall()]
    conn.close()
    return rooms


def create_service_request(
    room_number: str,
    guest_name: str,
    service_type: str,
    description: str,
    priority: str = "Medium",
    eta_minutes: int = 25,
    notes: str = ""
) -> Dict[str, Any]:
    """Creates a new service request and logs the creation event."""
    conn = get_connection()
    cursor = conn.cursor()
    ticket_id = generate_ticket_id()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Determine default staff assignment suggestion based on department
    dept_map = {
        "Housekeeping": "Housekeeping Lead",
        "Room Service": "F&B Kitchen Team",
        "Maintenance": "Engineering Duty Officer",
        "Laundry": "Valet Laundry Staff",
        "Concierge": "Chief Concierge"
    }
    assigned_staff = dept_map.get(service_type, "Duty Manager")

    cursor.execute("""
        INSERT INTO service_requests (ticket_id, room_number, guest_name, service_type, description, priority, status, assigned_staff, notes, eta_minutes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, 'Pending', ?, ?, ?, ?, ?)
    """, (ticket_id, room_number, guest_name, service_type, description, priority, assigned_staff, notes, eta_minutes, now_str, now_str))

    cursor.execute("""
        INSERT INTO request_logs (ticket_id, action, actor, timestamp, comment)
        VALUES (?, 'Created', 'AI Agent / Guest', ?, 'Request autonomously created and assigned to department')
    """, (ticket_id, now_str))

    conn.commit()
    conn.close()

    return {
        "ticket_id": ticket_id,
        "room_number": room_number,
        "guest_name": guest_name,
        "service_type": service_type,
        "description": description,
        "priority": priority,
        "status": "Pending",
        "assigned_staff": assigned_staff,
        "eta_minutes": eta_minutes,
        "created_at": now_str
    }


def get_request_by_ticket(ticket_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a single request by its unique ticket ID (supports HA-XXXX, HTL-XXXX, #XXXX)."""
    conn = get_connection()
    cursor = conn.cursor()
    clean_ticket = ticket_id.strip().upper().lstrip('#')
    
    # Try exact match first
    cursor.execute("SELECT * FROM service_requests WHERE UPPER(ticket_id) = ?", (clean_ticket,))
    row = cursor.fetchone()
    
    # Try with HA- prefix if not found
    if not row and not clean_ticket.startswith("HA-") and not clean_ticket.startswith("HTL-"):
        cursor.execute("SELECT * FROM service_requests WHERE UPPER(ticket_id) = ?", (f"HA-{clean_ticket}",))
        row = cursor.fetchone()
        
    # Try with HTL- prefix if not found
    if not row and not clean_ticket.startswith("HTL-"):
        cursor.execute("SELECT * FROM service_requests WHERE UPPER(ticket_id) = ?", (f"HTL-{clean_ticket}",))
        row = cursor.fetchone()

    conn.close()
    return dict(row) if row else None


def get_requests_by_room(room_number: str) -> List[Dict[str, Any]]:
    """Retrieves all service requests for a specified room."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM service_requests WHERE room_number = ? ORDER BY id DESC", (room_number.strip(),))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_all_requests(
    department_filter: str = "All",
    status_filter: str = "All",
    priority_filter: str = "All",
    search_query: str = ""
) -> List[Dict[str, Any]]:
    """Fetches all service requests with optional multi-criteria filtering."""
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM service_requests WHERE 1=1"
    params = []

    if department_filter and department_filter != "All":
        query += " AND service_type = ?"
        params.append(department_filter)

    if status_filter and status_filter != "All":
        query += " AND status = ?"
        params.append(status_filter)

    if priority_filter and priority_filter != "All":
        query += " AND priority = ?"
        params.append(priority_filter)

    if search_query:
        query += " AND (ticket_id LIKE ? OR room_number LIKE ? OR guest_name LIKE ? OR description LIKE ?)"
        like_param = f"%{search_query.strip()}%"
        params.extend([like_param, like_param, like_param, like_param])

    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_request_status(
    ticket_id: str,
    new_status: str,
    assigned_staff: Optional[str] = None,
    notes: Optional[str] = None,
    actor: str = "Staff Member"
) -> bool:
    """Updates the status, assigned staff, and notes of a service request."""
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    req = get_request_by_ticket(ticket_id)
    if not req:
        conn.close()
        return False

    clean_ticket = req["ticket_id"]
    update_fields = ["status = ?", "updated_at = ?"]
    params = [new_status, now_str]

    if assigned_staff is not None and assigned_staff.strip():
        update_fields.append("assigned_staff = ?")
        params.append(assigned_staff.strip())

    if notes is not None:
        update_fields.append("notes = ?")
        params.append(notes.strip())

    params.append(clean_ticket)

    sql = f"UPDATE service_requests SET {', '.join(update_fields)} WHERE ticket_id = ?"
    cursor.execute(sql, params)

    cursor.execute("""
        INSERT INTO request_logs (ticket_id, action, actor, timestamp, comment)
        VALUES (?, ?, ?, ?, ?)
    """, (clean_ticket, f"Status changed to {new_status}", actor, now_str, notes or f"Updated status to {new_status}"))

    conn.commit()
    conn.close()
    return True


def cancel_service_request(ticket_id: str, reason: str = "Cancelled by guest") -> Tuple[bool, str]:
    """Cancels an existing service request if it's not already completed."""
    req = get_request_by_ticket(ticket_id)
    if not req:
        return False, f"Ticket #{ticket_id} could not be found."

    if req["status"] == "Completed":
        return False, f"Ticket #{ticket_id} is already completed and cannot be cancelled."

    if req["status"] == "Cancelled":
        return False, f"Ticket #{ticket_id} is already cancelled."

    success = update_request_status(
        ticket_id=ticket_id,
        new_status="Cancelled",
        notes=f"Cancelled: {reason}",
        actor="Guest"
    )
    if success:
        return True, f"Ticket #{ticket_id} ({req['service_type']}) has been successfully cancelled."
    return False, "Failed to cancel request."


def get_kpi_stats() -> Dict[str, Any]:
    """Calculates live KPI metrics for the staff dashboard."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM service_requests")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM service_requests WHERE status = 'Pending'")
    pending = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM service_requests WHERE status = 'In Progress'")
    in_progress = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM service_requests WHERE status = 'Completed'")
    completed = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM service_requests WHERE priority = 'Urgent' AND status != 'Completed' AND status != 'Cancelled'")
    urgent_active = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM service_requests WHERE priority = 'High' AND status != 'Completed' AND status != 'Cancelled'")
    high_active = cursor.fetchone()[0]

    # Department breakdown
    cursor.execute("""
        SELECT service_type, COUNT(*) as count 
        FROM service_requests 
        GROUP BY service_type
    """)
    dept_counts = {row["service_type"]: row["count"] for row in cursor.fetchall()}

    conn.close()

    return {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "completed": completed,
        "urgent_active": urgent_active,
        "high_active": high_active,
        "department_counts": dept_counts
    }


def search_hotel_knowledge(query: str) -> List[Dict[str, Any]]:
    """Searches the hotel FAQ and knowledge base using keyword matching."""
    conn = get_connection()
    cursor = conn.cursor()
    words = [w.lower() for w in query.split() if len(w) > 2]
    
    if not words:
        cursor.execute("SELECT * FROM hotel_knowledge LIMIT 5")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    cursor.execute("SELECT * FROM hotel_knowledge")
    all_faqs = [dict(r) for r in cursor.fetchall()]
    conn.close()

    scored = []
    for faq in all_faqs:
        score = 0
        searchable_text = f"{faq['category']} {faq['question']} {faq['answer']} {faq['keywords']}".lower()
        for w in words:
            if w in searchable_text:
                score += 1
        if score > 0:
            scored.append((score, faq))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored[:3]]


def get_service_catalog(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Returns the service catalog filtered optionally by category."""
    conn = get_connection()
    cursor = conn.cursor()
    if category and category != "All":
        cursor.execute("SELECT * FROM service_catalog WHERE category = ? ORDER BY id ASC", (category,))
    else:
        cursor.execute("SELECT * FROM service_catalog ORDER BY category, id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def reset_database() -> None:
    """Drops and re-initializes the database with fresh seed data."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS guests")
    cursor.execute("DROP TABLE IF EXISTS service_requests")
    cursor.execute("DROP TABLE IF EXISTS service_catalog")
    cursor.execute("DROP TABLE IF EXISTS hotel_knowledge")
    cursor.execute("DROP TABLE IF EXISTS request_logs")
    conn.commit()
    conn.close()
    init_db()


# Auto-initialize on import
init_db()
