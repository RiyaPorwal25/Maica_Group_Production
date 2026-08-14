from decimal import Decimal
from django.test import TestCase

from .models import Party
from .views import resolve_dispatch_rate, _delivery_challan_print_company_details, _delivery_challan_party_details


class DispatchRateResolutionTests(TestCase):
    def test_special_party_uses_fixed_rate(self):
        self.assertEqual(resolve_dispatch_rate("Maica Plastiwood Pvt. Ltd.", "120"), Decimal("82"))

    def test_non_special_party_requires_manual_rate(self):
        with self.assertRaises(ValueError):
            resolve_dispatch_rate("Some Other Party", "")

    def test_print_company_details_match_template(self):
        company_details = _delivery_challan_print_company_details()

        self.assertEqual(company_details["company_name"], "Maica Plastiwood")
        self.assertIn("maicagroup1@gmail.com", company_details["company_email"])
        self.assertIn("Madhya Pradesh", company_details["company_state"])

    def test_special_party_defaults_to_company_details_when_missing(self):
        party_details = _delivery_challan_party_details(
            type("Challan", (), {"party_name": "Maica Plastiwood Pvt. Ltd.", "party_address": "", "party_gst": "", "party_state": ""})()
        )

        self.assertEqual(party_details["address"], "Khasra No. 508 125/9, 125/8 A-2,, Indore Ahemdabad Highway, GNT Market, Indore, Indore")
        self.assertEqual(party_details["gst"], "23AENPC5208D2Z1")
        self.assertEqual(party_details["state"], "Madhya Pradesh")

    def test_party_master_details_are_preferred_over_challan_values(self):
        party = Party.objects.create(c_name="Test Party", address="Master Address", gst="MASTERGST", state="Master State")
        challan = type("Challan", (), {
            "party_name": "Test Party",
            "party_address": "Challan Address",
            "party_gst": "CHALLANGST",
            "party_state": "Challan State",
        })()

        party_details = _delivery_challan_party_details(challan)

        self.assertEqual(party_details["address"], "Master Address")
        self.assertEqual(party_details["gst"], "MASTERGST")
        self.assertEqual(party_details["state"], "Master State")

    def test_special_party_uses_party_master_details_when_present(self):
        party = Party.objects.create(c_name="Maica Plastiwood Pvt. Ltd.", address="Master Address", gst="MASTERGST", state="Master State")
        challan = type("Challan", (), {
            "party_name": "Maica Plastiwood Pvt. Ltd.",
            "party_address": "Challan Address",
            "party_gst": "CHALLANGST",
            "party_state": "Challan State",
        })()

        party_details = _delivery_challan_party_details(challan)

        self.assertEqual(party_details["address"], "Master Address")
        self.assertEqual(party_details["gst"], "MASTERGST")
        self.assertEqual(party_details["state"], "Master State")
