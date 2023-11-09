import unittest

from eduapp.main import EaAuthStatus
from ui.main import login_ui_handler


class LoginUiHandlerTesstCase(unittest.TestCase):
    def test_success(self):
        data = EaAuthStatus(True, 'username', 'token', 'error_message')
        result = login_ui_handler(data)
        expected_result = 'Пользователь "username" успешно залогинился'
        self.assertEqual(result, expected_result)

    def test_failure(self):
        data = EaAuthStatus(False, 'username', 'token', 'error_message')
        result = login_ui_handler(data)
        expected_result = 'Ошибка входа. \nerror_message'
        self.assertEqual(result, expected_result)
