import frappe
import unittest
from neonnine.api.registration.main import register_user
def test_regi():
    type = register_user(
            name="Test User",
            phone="1234567890",
            address="Test Address",
            email="test@example.com",
            business_type="Retail")
    print(type)