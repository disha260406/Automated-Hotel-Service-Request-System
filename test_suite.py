"""
Automated Test Suite for the Automated Hotel Service Request System
Tests SQLite database transactions, LangGraph agent workflows, priority rules, and UI helpers.
"""

import unittest
import database
import agent_graph
import app


class TestHotelSystem(unittest.TestCase):

    def setUp(self):
        """Reset database to fresh state before each test suite."""
        database.reset_database()

    def test_database_initialization_and_guests(self):
        """Tests that guests and rooms are properly initialized."""
        rooms = database.get_all_rooms()
        self.assertGreater(len(rooms), 5)
        self.assertIn("101", rooms)
        self.assertIn("204", rooms)

        guest_101 = database.get_guest_by_room("101")
        self.assertIsNotNone(guest_101)
        self.assertEqual(guest_101["name"], "ramesh kumar")
        self.assertIn("VIP", guest_101["vip_status"])

    def test_service_request_creation_and_query(self):
        """Tests creating and querying service requests."""
        created = database.create_service_request(
            room_number="204",
            guest_name="Elena Rostova",
            service_type="Housekeeping",
            description="Need 2 extra feather pillows",
            priority="Medium",
            eta_minutes=15
        )
        self.assertTrue(created["ticket_id"].startswith("HA-"))
        self.assertEqual(created["status"], "Pending")

        # Query by ticket ID
        req = database.get_request_by_ticket(created["ticket_id"])
        self.assertIsNotNone(req)
        self.assertEqual(req["room_number"], "204")
        self.assertEqual(req["service_type"], "Housekeeping")

        # Query by room
        room_reqs = database.get_requests_by_room("204")
        ticket_ids = [r["ticket_id"] for r in room_reqs]
        self.assertIn(created["ticket_id"], ticket_ids)

    def test_request_status_update_and_cancellation(self):
        """Tests status transitions and cancellation constraints."""
        created = database.create_service_request(
            room_number="101",
            guest_name="ramesh kumar",
            service_type="Room Service",
            description="1 Espresso",
            priority="High",
            eta_minutes=15
        )
        tid = created["ticket_id"]

        # Update to In Progress
        success = database.update_request_status(tid, "In Progress", assigned_staff="Barista Team")
        self.assertTrue(success)
        req = database.get_request_by_ticket(tid)
        self.assertEqual(req["status"], "In Progress")
        self.assertEqual(req["assigned_staff"], "Barista Team")

        # Cancel request
        can_success, can_msg = database.cancel_service_request(tid, "Guest changed mind")
        self.assertTrue(can_success)
        req_cancelled = database.get_request_by_ticket(tid)
        self.assertEqual(req_cancelled["status"], "Cancelled")

        # Cannot cancel already cancelled
        can_again, _ = database.cancel_service_request(tid)
        self.assertFalse(can_again)

    def test_kpi_metrics(self):
        """Tests KPI calculation logic."""
        kpis = database.get_kpi_stats()
        self.assertIn("total", kpis)
        self.assertIn("pending", kpis)
        self.assertIn("in_progress", kpis)
        self.assertIn("completed", kpis)
        self.assertIn("urgent_active", kpis)
        self.assertGreater(kpis["total"], 0)

    def test_langgraph_housekeeping_routing(self):
        """Tests LangGraph classification of housekeeping requests."""
        res = agent_graph.process_guest_message("Could you please bring 2 fresh towels and soap to room 204?", "204")
        self.assertEqual(res["intent"], "create_request")
        self.assertEqual(res["service_type"], "Housekeeping")
        self.assertEqual(res["priority"], "Medium")
        self.assertIn("HA-", res["response"])
        self.assertIn("Housekeeping", res["response"])

    def test_langgraph_urgent_maintenance_routing(self):
        """Tests LangGraph classification of urgent maintenance emergencies."""
        res = agent_graph.process_guest_message("Emergency! Water is leaking heavily from the ceiling in room 312!", "312")
        self.assertEqual(res["intent"], "create_request")
        self.assertEqual(res["service_type"], "Maintenance")
        self.assertEqual(res["priority"], "Urgent")
        self.assertIn("Maintenance", res["response"])
        self.assertIn("312", res["response"])

    def test_langgraph_room_service_routing(self):
        """Tests LangGraph classification of room service orders."""
        res = agent_graph.process_guest_message("I'd like to order 1 Wagyu Burger with Truffle Fries and a Coke to room 101", "101")
        self.assertEqual(res["intent"], "create_request")
        self.assertEqual(res["service_type"], "Room Service")
        self.assertIn(res["priority"], ["High", "Medium"])
        self.assertIn("Room Service", res["response"])

    def test_langgraph_laundry_routing(self):
        """Tests LangGraph classification of laundry services."""
        res = agent_graph.process_guest_message("Please pick up my suit for dry cleaning and steam iron", "204")
        self.assertEqual(res["intent"], "create_request")
        self.assertEqual(res["service_type"], "Laundry")
        self.assertIn("Laundry", res["response"])

    def test_langgraph_status_tracking(self):
        """Tests LangGraph query status intent for existing ticket."""
        res = agent_graph.process_guest_message("What is the status of ticket #HA-8492?", "412")
        self.assertEqual(res["intent"], "query_status")
        self.assertIn("HA-8492", res["response"])
        self.assertIn("Status Update", res["response"])

    def test_langgraph_hotel_faq(self):
        """Tests LangGraph hotel knowledge retrieval for guest inquiries."""
        res = agent_graph.process_guest_message("What time is breakfast served at the hotel?", "101")
        self.assertEqual(res["intent"], "hotel_faq")
        self.assertIn("Breakfast", res["response"])

    def test_ui_helpers_and_dataframe(self):
        """Tests UI formatters and data retrieval."""
        profile_html = app.format_guest_profile_card("101")
        self.assertIn("ramesh kumar", profile_html)

        active_html = app.format_room_active_requests("412")
        self.assertIn("HA-", active_html)

        tracking_html = app.format_tracking_card("HA-8492")
        self.assertIn("Ticket #HA-8492", tracking_html)

        df = app.get_requests_dataframe()
        self.assertFalse(df.empty)
        self.assertIn("Ticket ID", df.columns)


if __name__ == "__main__":
    unittest.main()
