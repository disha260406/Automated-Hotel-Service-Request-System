"""
Grand Royale Hotel - Automated Hotel Service Request System
Built with Python, Gradio, LangGraph Agentic AI, and SQLite.
"""

import gradio as gr
import pandas as pd
import datetime
import os
import database
import agent_graph
import ui_theme


def format_guest_profile_card(room_number: str) -> str:
    """Generates an HTML luxury profile card for the selected room."""
    guest = database.get_guest_by_room(room_number)
    if not guest:
        return f"""
        <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(197, 160, 89, 0.25); border-radius: 12px; padding: 16px; margin-bottom: 12px;">
            <div style="color: #94a3b8; font-size: 13px;">Room Status</div>
            <div style="color: #f8fafc; font-size: 18px; font-weight: 700; margin-top: 4px;">Room #{room_number} (Vacant / Unregistered)</div>
        </div>
        """
    
    vip_badge = f'<span style="background: rgba(197, 160, 89, 0.2); color: #dfb76c; border: 1px solid #c5a059; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 700;">{guest["vip_status"]}</span>'
    
    return f"""
    <div style="background: linear-gradient(145deg, #131d31 0%, #0c1220 100%); border: 1px solid rgba(197, 160, 89, 0.3); border-radius: 14px; padding: 18px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <div style="font-family: 'Cinzel', serif; font-size: 18px; font-weight: 700; color: #dfb76c;">Room #{guest['room_number']}</div>
            {vip_badge}
        </div>
        <div style="font-size: 16px; font-weight: 600; color: #f8fafc;">{guest['name']}</div>
        <div style="color: #94a3b8; font-size: 12px; margin-top: 6px; display: grid; grid-template-columns: 1fr 1fr; gap: 4px;">
            <div>📞 {guest['phone']}</div>
            <div>📅 Out: {guest['check_out_date']}</div>
        </div>
    </div>
    """


def format_room_active_requests(room_number: str) -> str:
    """Generates an HTML list of active requests for the sidebar widget."""
    reqs = database.get_requests_by_room(room_number)
    if not reqs:
        return """
        <div style="background: rgba(15, 23, 42, 0.6); border: 1px dashed rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 20px; text-align: center; color: #64748b; font-size: 13px; margin-top: 12px;">
            No active service requests for this room.<br>Use the concierge chat to place an order or request assistance.
        </div>
        """
    
    html = '<div style="margin-top: 12px; display: flex; flex-direction: column; gap: 10px;">'
    for r in reqs[:5]:
        prio_color = "#ef4444" if r["priority"] == "Urgent" else "#f97316" if r["priority"] == "High" else "#eab308" if r["priority"] == "Medium" else "#10b981"
        status_color = "#3b82f6" if r["status"] == "Pending" else "#8b5cf6" if r["status"] == "In Progress" else "#10b981" if r["status"] == "Completed" else "#64748b"
        
        html += f"""
        <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(255, 255, 255, 0.08); border-left: 4px solid {prio_color}; border-radius: 10px; padding: 12px 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 700; color: #dfb76c;">#{r['ticket_id']}</span>
                <span style="background: {status_color}22; color: {status_color}; border: 1px solid {status_color}; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 700;">{r['status']}</span>
            </div>
            <div style="font-size: 13px; font-weight: 600; color: #f8fafc; margin-top: 4px;">{r['service_type']}</div>
            <div style="font-size: 12px; color: #94a3b8; margin-top: 2px; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">{r['description']}</div>
            <div style="display: flex; justify-content: space-between; font-size: 11px; color: #64748b; margin-top: 6px;">
                <span>Priority: <b style="color: {prio_color};">{r['priority']}</b></span>
                <span>⏱️ ~{r['eta_minutes']}m</span>
            </div>
        </div>
        """
    html += "</div>"
    return html


def format_kpi_html() -> str:
    """Renders the HTML KPI metric summary cards for the Staff Dashboard."""
    kpis = database.get_kpi_stats()
    return f"""
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-label">Total Requests</div>
            <div class="kpi-value">{kpis['total']}</div>
            <div class="kpi-sub">Lifetime logged in SQLite</div>
        </div>
        <div class="kpi-card" style="border-color: rgba(59, 130, 246, 0.3);">
            <div class="kpi-label" style="color: #60a5fa;">Pending Dispatch</div>
            <div class="kpi-value" style="color: #60a5fa;">{kpis['pending']}</div>
            <div class="kpi-sub">Awaiting staff pickup</div>
        </div>
        <div class="kpi-card" style="border-color: rgba(139, 92, 246, 0.3);">
            <div class="kpi-label" style="color: #a78bfa;">In Progress</div>
            <div class="kpi-value" style="color: #a78bfa;">{kpis['in_progress']}</div>
            <div class="kpi-sub">Active staff handling</div>
        </div>
        <div class="kpi-card" style="border-color: rgba(16, 185, 129, 0.3);">
            <div class="kpi-label" style="color: #34d399;">Resolved</div>
            <div class="kpi-value" style="color: #34d399;">{kpis['completed']}</div>
            <div class="kpi-sub">Delivered & verified</div>
        </div>
        <div class="kpi-card" style="border-color: rgba(239, 68, 68, 0.4);">
            <div class="kpi-label" style="color: #f87171;">Urgent Attention</div>
            <div class="kpi-value" style="color: #f87171;">{kpis['urgent_active']}</div>
            <div class="kpi-sub">Requires priority SLA</div>
        </div>
    </div>
    """


def get_requests_dataframe(dept="All", status="All", priority="All", search="") -> pd.DataFrame:
    """Returns a formatted Pandas DataFrame of requests for the dashboard."""
    reqs = database.get_all_requests(dept, status, priority, search)
    if not reqs:
        return pd.DataFrame(columns=["Ticket ID", "Room", "Guest", "Department", "Priority", "Status", "Staff Assigned", "ETA", "Created At"])
    
    rows = []
    for r in reqs:
        rows.append({
            "Ticket ID": r["ticket_id"],
            "Room": r["room_number"],
            "Guest": r["guest_name"],
            "Department": r["service_type"],
            "Priority": r["priority"],
            "Status": r["status"],
            "Staff Assigned": r["assigned_staff"],
            "ETA (mins)": r["eta_minutes"],
            "Created At": r["created_at"],
            "Description": r["description"]
        })
    return pd.DataFrame(rows)


def format_tracking_card(ticket_or_room: str) -> str:
    """Generates the visual progress timeline and ticket card for the Tracker tab."""
    if not ticket_or_room.strip():
        return "<div style='text-align: center; color: #64748b; padding: 40px;'>Enter a Ticket ID (e.g. HTL-1082) or Room Number (e.g. 204) to track request progress.</div>"
    
    clean_input = ticket_or_room.strip().upper()
    req = database.get_request_by_ticket(clean_input)
    
    if not req:
        # Check if user entered room number
        room_reqs = database.get_requests_by_room(clean_input)
        if room_reqs:
            req = room_reqs[0]
        else:
            return f"""
            <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 12px; padding: 24px; text-align: center;">
                <div style="font-size: 20px;">⚠️</div>
                <div style="color: #f87171; font-weight: 700; margin-top: 8px;">No Request Found for '{ticket_or_room}'</div>
                <div style="color: #94a3b8; font-size: 13px; margin-top: 4px;">Please check the ticket number format (HTL-XXXX) or verify the room number.</div>
            </div>
            """

    tid = req["ticket_id"]
    room = req["room_number"]
    guest = req["guest_name"]
    dept = req["service_type"]
    desc = req["description"]
    prio = req["priority"]
    status = req["status"]
    staff = req["assigned_staff"]
    eta = req["eta_minutes"]
    created_at = req["created_at"]
    notes = req["notes"] or "None"

    # Step Progress Logic
    step1_active = "background: #10b981; color: #080c14;"
    step2_active = "background: #10b981; color: #080c14;" if status in ["In Progress", "Completed"] else "background: #3b82f6; color: #fff;" if status == "Pending" else "background: #334155; color: #94a3b8;"
    step3_active = "background: #10b981; color: #080c14;" if status == "Completed" else "background: #8b5cf6; color: #fff;" if status == "In Progress" else "background: #334155; color: #94a3b8;"
    step4_active = "background: #10b981; color: #080c14;" if status == "Completed" else "background: #334155; color: #94a3b8;"

    if status == "Cancelled":
        step_banner = """
        <div style="background: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; border-radius: 10px; padding: 12px; text-align: center; color: #f87171; font-weight: 700; margin-bottom: 20px;">
            🚫 THIS SERVICE REQUEST HAS BEEN CANCELLED
        </div>
        """
    else:
        step_banner = f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 28px; position: relative;">
            <div style="position: absolute; top: 18px; left: 10%; right: 10%; height: 3px; background: rgba(255,255,255,0.1); z-index: 1;"></div>
            
            <div style="display: flex; flex-direction: column; align-items: center; z-index: 2; width: 25%;">
                <div style="width: 36px; height: 36px; border-radius: 50%; {step1_active} display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 14px; box-shadow: 0 0 10px rgba(16,185,129,0.5);">✓</div>
                <div style="font-size: 12px; font-weight: 600; color: #f8fafc; margin-top: 8px;">Received</div>
                <div style="font-size: 10px; color: #64748b;">Logged in DB</div>
            </div>

            <div style="display: flex; flex-direction: column; align-items: center; z-index: 2; width: 25%;">
                <div style="width: 36px; height: 36px; border-radius: 50%; {step2_active} display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 14px;">2</div>
                <div style="font-size: 12px; font-weight: 600; color: #f8fafc; margin-top: 8px;">Assigned</div>
                <div style="font-size: 10px; color: #64748b;">{staff[:16]}</div>
            </div>

            <div style="display: flex; flex-direction: column; align-items: center; z-index: 2; width: 25%;">
                <div style="width: 36px; height: 36px; border-radius: 50%; {step3_active} display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 14px;">3</div>
                <div style="font-size: 12px; font-weight: 600; color: #f8fafc; margin-top: 8px;">In Progress</div>
                <div style="font-size: 10px; color: #64748b;">Handling request</div>
            </div>

            <div style="display: flex; flex-direction: column; align-items: center; z-index: 2; width: 25%;">
                <div style="width: 36px; height: 36px; border-radius: 50%; {step4_active} display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 14px;">4</div>
                <div style="font-size: 12px; font-weight: 600; color: #f8fafc; margin-top: 8px;">Completed</div>
                <div style="font-size: 10px; color: #64748b;">Delivered</div>
            </div>
        </div>
        """

    prio_color = "#ef4444" if prio == "Urgent" else "#f97316" if prio == "High" else "#eab308" if prio == "Medium" else "#10b981"

    return f"""
    <div style="background: linear-gradient(145deg, #131d31 0%, #0c1220 100%); border: 1px solid rgba(197, 160, 89, 0.3); border-radius: 16px; padding: 28px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);">
        {step_banner}
        
        <div style="display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 16px; margin-bottom: 16px;">
            <div>
                <span style="font-family: 'Cinzel', serif; font-size: 22px; font-weight: 700; color: #dfb76c;">Ticket #{tid}</span>
                <div style="font-size: 14px; color: #94a3b8; margin-top: 2px;">Room #{room} &bull; Guest: <b style="color: #f8fafc;">{guest}</b></div>
            </div>
            <div style="text-align: right;">
                <span style="background: {prio_color}22; color: {prio_color}; border: 1px solid {prio_color}; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 700;">{prio.upper()} PRIORITY</span>
                <div style="font-size: 12px; color: #64748b; margin-top: 4px;">Created: {created_at}</div>
            </div>
        </div>

        <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 20px;">
            <div>
                <div style="font-size: 12px; color: #64748b; text-transform: uppercase; font-weight: 600;">Request Details</div>
                <div style="font-size: 16px; color: #f8fafc; font-weight: 500; margin-top: 4px; background: rgba(0,0,0,0.25); padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);">
                    "{desc}"
                </div>
                <div style="margin-top: 12px; font-size: 12px; color: #94a3b8;">
                    <b>Internal Notes:</b> <i>{notes}</i>
                </div>
            </div>

            <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(197, 160, 89, 0.15); border-radius: 10px; padding: 14px;">
                <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase;">Service Department</div>
                <div style="font-size: 14px; font-weight: 700; color: #dfb76c; margin-top: 2px;">{dept}</div>

                <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase; margin-top: 10px;">Assigned Handler</div>
                <div style="font-size: 14px; font-weight: 600; color: #f8fafc; margin-top: 2px;">{staff}</div>

                <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase; margin-top: 10px;">Estimated Delivery</div>
                <div style="font-size: 18px; font-weight: 700; color: #34d399; margin-top: 2px;">⏱️ ~{eta} mins</div>
            </div>
        </div>
    </div>
    """


# -------------------------------------------------------------
# Gradio Main Application Builder
# -------------------------------------------------------------

def create_app():
    all_rooms = database.get_all_rooms()
    initial_room = all_rooms[0] if all_rooms else "101"

    with gr.Blocks(title="Grand Royale - Automated Hotel Service System") as app:
        
        # State variables
        current_room_state = gr.State(initial_room)
        chat_history_state = gr.State([])

        # Top Header Banner
        gr.HTML("""
        <div class="hotel-header">
            <div>
                <h1 class="hotel-title">GRAND ROYALE HOTEL & RESIDENCES</h1>
                <div class="hotel-subtitle">Autonomous Agentic Guest Concierge & Service Operations System</div>
            </div>
            <div style="display: flex; gap: 12px; align-items: center;">
                <div class="hotel-badge">⭐ 5-Star Luxury SLA</div>
                <div class="hotel-badge" style="border-color: #10b981; color: #34d399;">⚡ LangGraph AI Active</div>
            </div>
        </div>
        """)

        with gr.Tabs() as main_tabs:

            # -----------------------------------------------------------------
            # TAB 1: 🛎️ Guest Concierge Chat
            # -----------------------------------------------------------------
            with gr.TabItem("🛎️ Guest Concierge & Chat", id="tab_chat"):
                with gr.Row():
                    # Left Column: Chat Assistant
                    with gr.Column(scale=7):
                        with gr.Row():
                            room_dropdown = gr.Dropdown(
                                choices=all_rooms,
                                value=initial_room,
                                label="🏨 Select Guest Room (Simulation Login)",
                                info="Select a room to automatically authenticate as that guest",
                                scale=8
                            )
                            sync_room_btn = gr.Button("🔄 Sync", scale=2)

                        chatbot = gr.Chatbot(
                            label="Grand Royale Luxury AI Concierge",
                            height=480,
                            elem_classes="chatbot"
                        )

                        # Quick Action Pills
                        gr.HTML("<div style='font-size: 12px; font-weight: 600; color: #94a3b8; margin: 8px 0 4px;'>💡 QUICK SERVICE SUGGESTIONS:</div>")
                        with gr.Row():
                            quick_btn_towels = gr.Button("🧹 2 Fresh Bath Towels & Kit", elem_classes="quick-pill")
                            quick_btn_leak = gr.Button("🔧 AC Leaking Water (Urgent)", elem_classes="quick-pill")
                            quick_btn_burger = gr.Button("🍽️ Wagyu Burger & Truffle Fries", elem_classes="quick-pill")
                            quick_btn_laundry = gr.Button("👔 Express Suit Dry Cleaning", elem_classes="quick-pill")

                        with gr.Row():
                            user_msg_input = gr.Textbox(
                                placeholder="E.g., 'Please send 2 extra pillows to room 204' or 'What time does the pool close?'",
                                label="Your Request / Message",
                                scale=9,
                                lines=2
                            )
                            send_btn = gr.Button("🛎️ Send Request", variant="primary", scale=3, elem_classes="primary")

                        with gr.Row():
                            clear_chat_btn = gr.Button("🧹 Clear Conversation", size="sm")

                    # Right Column: Active Room Summary Widget
                    with gr.Column(scale=4):
                        profile_card_html = gr.HTML(format_guest_profile_card(initial_room))
                        gr.HTML("<div style='font-size: 14px; font-weight: 700; color: #dfb76c; margin-top: 16px;'>📋 ACTIVE ROOM REQUESTS:</div>")
                        room_requests_html = gr.HTML(format_room_active_requests(initial_room))
                        refresh_sidebar_btn = gr.Button("🔄 Refresh Active Status", size="sm")

            # -----------------------------------------------------------------
            # TAB 2: 🔍 Live Request Tracking
            # -----------------------------------------------------------------
            with gr.TabItem("🔍 Live Request Tracking", id="tab_tracking"):
                gr.HTML("<div style='font-size: 18px; font-weight: 700; color: #dfb76c; margin-bottom: 12px;'>Real-Time Service Request Lifecycle & SLA Tracking</div>")
                
                with gr.Row():
                    tracking_search_input = gr.Textbox(
                        placeholder="Enter Ticket ID (e.g. HTL-1082) or Room Number (e.g. 204)",
                        label="Ticket ID or Room #",
                        scale=9
                    )
                    track_btn = gr.Button("🔍 Track Status", variant="primary", scale=3, elem_classes="primary")

                tracking_result_html = gr.HTML(format_tracking_card("HTL-1082"))

                with gr.Row(visible=True):
                    cancel_ticket_input = gr.Textbox(placeholder="Ticket ID to cancel (e.g. HTL-1082)", label="Cancel Request Ticket #", scale=6)
                    cancel_reason_input = gr.Textbox(placeholder="Reason (optional)", label="Cancellation Reason", scale=4)
                    cancel_btn = gr.Button("🚫 Cancel Ticket", variant="stop", scale=2)
                
                cancel_output_msg = gr.Markdown("")

            # -----------------------------------------------------------------
            # TAB 3: 📊 Staff Operations Dashboard
            # -----------------------------------------------------------------
            with gr.TabItem("📊 Staff Operations Dashboard", id="tab_staff"):
                kpi_banner_html = gr.HTML(format_kpi_html())

                with gr.Row():
                    filter_dept = gr.Dropdown(
                        choices=["All", "Housekeeping", "Room Service", "Maintenance", "Laundry", "Concierge"],
                        value="All",
                        label="Filter Department",
                        scale=3
                    )
                    filter_status = gr.Dropdown(
                        choices=["All", "Pending", "In Progress", "Completed", "Cancelled"],
                        value="All",
                        label="Filter Status",
                        scale=3
                    )
                    filter_priority = gr.Dropdown(
                        choices=["All", "Urgent", "High", "Medium", "Low"],
                        value="All",
                        label="Filter Priority",
                        scale=3
                    )
                    filter_search = gr.Textbox(
                        placeholder="Search Room, Ticket, Guest, or Description...",
                        label="Keyword Search",
                        scale=3
                    )
                    refresh_dash_btn = gr.Button("🔄 Refresh Table", variant="primary", scale=2, elem_classes="primary")

                # Dataframe Table
                dashboard_table = gr.DataFrame(
                    value=get_requests_dataframe(),
                    label="All Hotel Service Requests (Live SQLite)",
                    interactive=False,
                    wrap=True
                )

                # Staff Action & Dispatch Panel
                gr.HTML("<div style='font-size: 16px; font-weight: 700; color: #dfb76c; margin: 20px 0 8px;'>⚡ Quick Ticket Action & Staff Dispatch Panel</div>")
                with gr.Row():
                    update_ticket_id = gr.Textbox(placeholder="E.g. HTL-1082", label="Target Ticket ID", scale=3)
                    update_new_status = gr.Dropdown(choices=["Pending", "In Progress", "Completed", "Cancelled"], value="In Progress", label="Set New Status", scale=3)
                    update_staff_name = gr.Textbox(placeholder="Staff name / team", label="Assign Staff Member", scale=3)
                    update_notes = gr.Textbox(placeholder="Action notes...", label="Internal Notes", scale=3)
                    apply_update_btn = gr.Button("💾 Update Ticket", variant="primary", scale=2, elem_classes="primary")

                update_status_msg = gr.Markdown("")

            # -----------------------------------------------------------------
            # TAB 4: 🏨 Hotel Services Catalog & FAQ
            # -----------------------------------------------------------------
            with gr.TabItem("🏨 Services Catalog & Hotel FAQs", id="tab_catalog"):
                with gr.Row():
                    with gr.Column(scale=6):
                        gr.HTML("<div style='font-size: 18px; font-weight: 700; color: #dfb76c; margin-bottom: 12px;'>🛎️ Hotel Services & Amenities Catalog</div>")
                        catalog_filter_dropdown = gr.Dropdown(
                            choices=["All", "Housekeeping", "Room Service", "Maintenance", "Laundry", "Concierge"],
                            value="All",
                            label="Catalog Category"
                        )
                        catalog_table = gr.DataFrame(
                            value=pd.DataFrame(database.get_service_catalog()),
                            interactive=False,
                            wrap=True
                        )

                    with gr.Column(scale=6):
                        gr.HTML("<div style='font-size: 18px; font-weight: 700; color: #dfb76c; margin-bottom: 12px;'>📖 Hotel Knowledge Base & Policies</div>")
                        faq_search_box = gr.Textbox(placeholder="Search hotel policies, breakfast hours, pool, wifi...", label="Search Hotel FAQs")
                        faq_search_btn = gr.Button("🔍 Search Knowledge Base")
                        faq_results_df = gr.DataFrame(
                            value=pd.DataFrame(database.search_hotel_knowledge("")),
                            interactive=False,
                            wrap=True
                        )

            # -----------------------------------------------------------------
            # TAB 5: ⚙️ Agent Diagnostics & System Config
            # -----------------------------------------------------------------
            with gr.TabItem("⚙️ Agent Diagnostics & System", id="tab_diag"):
                gr.HTML("<div style='font-size: 18px; font-weight: 700; color: #dfb76c; margin-bottom: 8px;'>LangGraph Agentic State & Reasoning Inspector</div>")
                
                with gr.Row():
                    diag_input = gr.Textbox(
                        value="Water is leaking heavily in bathroom of room 312 emergency!",
                        label="Test Prompt for Agent Diagnostics",
                        scale=9
                    )
                    run_diag_btn = gr.Button("⚡ Test Agent Graph", variant="primary", scale=3, elem_classes="primary")

                with gr.Row():
                    diag_reasoning_box = gr.Textbox(label="Agent Reasoning Chain Trace", lines=8, interactive=False)
                    diag_state_box = gr.JSON(label="Final LangGraph State Output")

                gr.HTML("<div style='font-size: 16px; font-weight: 700; color: #dfb76c; margin: 24px 0 8px;'>Database Maintenance</div>")
                with gr.Row():
                    reset_db_btn = gr.Button("⚠️ Reset & Re-Seed SQLite Database", variant="stop")
                    reset_status_box = gr.Markdown("")

        # -------------------------------------------------------------
        # Event Handlers & Callback Bindings
        # -------------------------------------------------------------

        # Chat interaction function
        def handle_chat_turn(user_msg, history, room):
            if not user_msg.strip():
                return "", history, format_guest_profile_card(room), format_room_active_requests(room), format_kpi_html(), get_requests_dataframe()
            
            # Execute LangGraph Agent
            agent_result = agent_graph.process_guest_message(
                user_message=user_msg,
                active_room=room,
                conversation_history=history
            )

            new_history = list(history or [])
            new_history.append({"role": "user", "content": user_msg})
            new_history.append({"role": "assistant", "content": agent_result["response"]})

            # Update live sidebar cards & dashboard data
            updated_profile = format_guest_profile_card(room)
            updated_requests = format_room_active_requests(room)
            updated_kpis = format_kpi_html()
            updated_df = get_requests_dataframe()

            return "", new_history, updated_profile, updated_requests, updated_kpis, updated_df

        send_btn.click(
            handle_chat_turn,
            inputs=[user_msg_input, chatbot, room_dropdown],
            outputs=[user_msg_input, chatbot, profile_card_html, room_requests_html, kpi_banner_html, dashboard_table]
        )

        user_msg_input.submit(
            handle_chat_turn,
            inputs=[user_msg_input, chatbot, room_dropdown],
            outputs=[user_msg_input, chatbot, profile_card_html, room_requests_html, kpi_banner_html, dashboard_table]
        )

        # Quick suggestions click handlers
        def fill_prompt(text):
            return text

        quick_btn_towels.click(lambda: "Please deliver 2 fresh bath towels and toiletries kit to my room.", outputs=[user_msg_input])
        quick_btn_leak.click(lambda: "Emergency! Water is leaking from the AC in the bathroom!", outputs=[user_msg_input])
        quick_btn_burger.click(lambda: "I would like to order 1 Wagyu Burger with Truffle Fries and a Sparkling Water.", outputs=[user_msg_input])
        quick_btn_laundry.click(lambda: "Please pick up my suit for express same-day dry cleaning.", outputs=[user_msg_input])

        # Room change sync
        def on_room_change(room):
            return format_guest_profile_card(room), format_room_active_requests(room)

        room_dropdown.change(on_room_change, inputs=[room_dropdown], outputs=[profile_card_html, room_requests_html])
        sync_room_btn.click(on_room_change, inputs=[room_dropdown], outputs=[profile_card_html, room_requests_html])
        refresh_sidebar_btn.click(on_room_change, inputs=[room_dropdown], outputs=[profile_card_html, room_requests_html])

        # Clear chat
        clear_chat_btn.click(lambda: [], outputs=[chatbot])

        # Tracking Tab
        def track_ticket(ticket_input):
            return format_tracking_card(ticket_input)

        track_btn.click(track_ticket, inputs=[tracking_search_input], outputs=[tracking_result_html])
        tracking_search_input.submit(track_ticket, inputs=[tracking_search_input], outputs=[tracking_result_html])

        def handle_cancel_ticket(tid, reason):
            if not tid.strip():
                return "⚠️ Please provide a valid Ticket ID."
            success, msg = database.cancel_service_request(tid.strip(), reason.strip() or "Cancelled by user")
            status_prefix = "✅" if success else "⚠️"
            return f"{status_prefix} {msg}"

        cancel_btn.click(
            handle_cancel_ticket,
            inputs=[cancel_ticket_input, cancel_reason_input],
            outputs=[cancel_output_msg]
        )

        # Staff Dashboard Filters
        def update_dashboard(dept, status, priority, search):
            df = get_requests_dataframe(dept, status, priority, search)
            kpi_html = format_kpi_html()
            return df, kpi_html

        refresh_dash_btn.click(
            update_dashboard,
            inputs=[filter_dept, filter_status, filter_priority, filter_search],
            outputs=[dashboard_table, kpi_banner_html]
        )
        filter_dept.change(update_dashboard, inputs=[filter_dept, filter_status, filter_priority, filter_search], outputs=[dashboard_table, kpi_banner_html])
        filter_status.change(update_dashboard, inputs=[filter_dept, filter_status, filter_priority, filter_search], outputs=[dashboard_table, kpi_banner_html])
        filter_priority.change(update_dashboard, inputs=[filter_dept, filter_status, filter_priority, filter_search], outputs=[dashboard_table, kpi_banner_html])
        filter_search.submit(update_dashboard, inputs=[filter_dept, filter_status, filter_priority, filter_search], outputs=[dashboard_table, kpi_banner_html])

        # Staff Update Ticket
        def handle_ticket_update(tid, new_status, staff, notes):
            if not tid.strip():
                return "⚠️ Please enter a valid Ticket ID.", get_requests_dataframe(), format_kpi_html()
            
            success = database.update_request_status(
                ticket_id=tid.strip(),
                new_status=new_status,
                assigned_staff=staff if staff.strip() else None,
                notes=notes if notes.strip() else None,
                actor="Staff Dashboard"
            )
            if success:
                msg = f"✅ Ticket **#{tid.strip().upper()}** successfully updated to status **'{new_status}'**!"
            else:
                msg = f"⚠️ Could not find Ticket **#{tid.strip()}** in database."
            
            return msg, get_requests_dataframe(), format_kpi_html()

        apply_update_btn.click(
            handle_ticket_update,
            inputs=[update_ticket_id, update_new_status, update_staff_name, update_notes],
            outputs=[update_status_msg, dashboard_table, kpi_banner_html]
        )

        # Catalog Filter
        def filter_catalog(cat):
            return pd.DataFrame(database.get_service_catalog(cat))

        catalog_filter_dropdown.change(filter_catalog, inputs=[catalog_filter_dropdown], outputs=[catalog_table])

        # FAQ Search
        def search_faq(q):
            return pd.DataFrame(database.search_hotel_knowledge(q))

        faq_search_btn.click(search_faq, inputs=[faq_search_box], outputs=[faq_results_df])
        faq_search_box.submit(search_faq, inputs=[faq_search_box], outputs=[faq_results_df])

        # Diagnostics Tab
        def run_diagnostics(prompt):
            res = agent_graph.process_guest_message(prompt, "312")
            reasoning_str = "\n".join(res["reasoning_chain"])
            return reasoning_str, res

        run_diag_btn.click(run_diagnostics, inputs=[diag_input], outputs=[diag_reasoning_box, diag_state_box])

        # Reset Database
        def handle_reset_db():
            database.reset_database()
            return "✅ Database reset successfully with fresh seed data!", get_requests_dataframe(), format_kpi_html()

        reset_db_btn.click(handle_reset_db, outputs=[reset_status_box, dashboard_table, kpi_banner_html])

    return app


if __name__ == "__main__":
    app = create_app()
    app.launch(server_name="127.0.0.1", server_port=7860, share=False, theme=gr.themes.Base(), css=ui_theme.CUSTOM_CSS)
