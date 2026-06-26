"""
Модульні тести для репозиторію контактів.
"""
import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from datetime import date

from app.models.contact import Contact
from app.models.user import User, Role
from app.schemas.contact import ContactCreate, ContactUpdate
from app.repository.contacts import (
    get_contacts, get_contact_by_id, get_contact_by_email,
    create_contact, update_contact, remove_contact, get_upcoming_birthdays
)

class TestContactsRepository(unittest.TestCase):
    def setUp(self):
        # Мокаємо сесію БД та створюємо фейкового користувача
        self.session = MagicMock(spec=Session)
        self.user = User(id=1, email="test@example.com", role=Role.user)

    def test_get_contacts(self):
        contacts = [Contact(id=1), Contact(id=2)]
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = contacts
        self.session.scalars.return_value = mock_scalars

        result = get_contacts(self.session, self.user)
        self.assertEqual(result, contacts)

    def test_get_contact_by_id_found(self):
        contact = Contact(id=1)
        mock_scalars = MagicMock()
        mock_scalars.first.return_value = contact
        self.session.scalars.return_value = mock_scalars

        result = get_contact_by_id(self.session, 1, self.user)
        self.assertEqual(result, contact)

    def test_get_contact_by_id_not_found(self):
        mock_scalars = MagicMock()
        mock_scalars.first.return_value = None
        self.session.scalars.return_value = mock_scalars

        result = get_contact_by_id(self.session, 999, self.user)
        self.assertIsNone(result)

    def test_create_contact(self):
        body = ContactCreate(
            first_name="Ivan", last_name="Franko", email="ivan@test.com",
            phone="0991234567", birthday=date(1856, 8, 27)
        )
        result = create_contact(self.session, body, self.user)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.email, body.email)
        self.assertTrue(self.session.add.called)
        self.assertTrue(self.session.commit.called)
        self.assertTrue(self.session.refresh.called)

    def test_update_contact_found(self):
        body = ContactUpdate(
            first_name="Taras", last_name="Shevchenko", email="taras@test.com",
            phone="0997654321", birthday=date(1814, 3, 9)
        )
        contact = Contact(id=1, user_id=self.user.id)
        
        mock_scalars = MagicMock()
        mock_scalars.first.return_value = contact
        self.session.scalars.return_value = mock_scalars

        result = update_contact(self.session, 1, body, self.user)
        self.assertEqual(result.first_name, body.first_name)
        self.assertTrue(self.session.commit.called)

    def test_remove_contact_found(self):
        contact = Contact(id=1)
        mock_scalars = MagicMock()
        mock_scalars.first.return_value = contact
        self.session.scalars.return_value = mock_scalars

        result = remove_contact(self.session, 1, self.user)
        self.assertEqual(result, contact)
        self.assertTrue(self.session.delete.called)
        self.assertTrue(self.session.commit.called)