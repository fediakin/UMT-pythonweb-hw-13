"""
Модульні тести для репозиторію користувачів.
"""
import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserModel
from app.repository.users import (
    get_user_by_email, create_user, update_token, confirm_email, update_avatar
)

class TestUsersRepository(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)

    def test_get_user_by_email(self):
        user = User(id=1, email="test@example.com")
        mock_scalars = MagicMock()
        mock_scalars.first.return_value = user
        self.session.scalars.return_value = mock_scalars

        result = get_user_by_email(self.session, "test@example.com")
        self.assertEqual(result, user)
        self.assertEqual(result.email, "test@example.com")

    def test_create_user(self):
        body = UserModel(email="new@example.com", password="password123")
        
        result = create_user(self.session, body)
        self.assertEqual(result.email, "new@example.com")
        self.assertTrue(self.session.add.called)
        self.assertTrue(self.session.commit.called)
        self.assertTrue(self.session.refresh.called)

    def test_update_token(self):
        user = User(id=1, email="test@example.com", refresh_token=None)
        
        update_token(self.session, user, "new_refresh_token")
        self.assertEqual(user.refresh_token, "new_refresh_token")
        self.assertTrue(self.session.commit.called)

    def test_confirm_email(self):
        user = User(id=1, email="test@example.com", confirmed=False)
        mock_scalars = MagicMock()
        mock_scalars.first.return_value = user
        self.session.scalars.return_value = mock_scalars

        confirm_email(self.session, "test@example.com")
        self.assertTrue(user.confirmed)
        self.assertTrue(self.session.commit.called)

    def test_update_avatar(self):
        user = User(id=1, email="test@example.com", avatar=None)
        mock_scalars = MagicMock()
        mock_scalars.first.return_value = user
        self.session.scalars.return_value = mock_scalars

        result = update_avatar(self.session, "test@example.com", "http://example.com/avatar.jpg")
        self.assertEqual(result.avatar, "http://example.com/avatar.jpg")
        self.assertTrue(self.session.commit.called)
        self.assertTrue(self.session.refresh.called)