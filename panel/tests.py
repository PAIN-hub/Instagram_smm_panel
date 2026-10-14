from django.test import TestCase, Client
from django.urls import reverse
from panel.models import InstagramAccount, Proxy, BotTask, GlobalSetting
from panel.bot_logic.settings_helper import get_setting, set_setting
from panel.bot_logic.browser import find_system_chromium, launch_browser

class PanelViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_dashboard_view(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Instagram SMM")

    def test_accounts_view(self):
        response = self.client.get(reverse('accounts_list'))
        self.assertEqual(response.status_code, 200)

    def test_tasks_view(self):
        response = self.client.get(reverse('tasks_list'))
        self.assertEqual(response.status_code, 200)

    def test_proxies_view(self):
        response = self.client.get(reverse('proxies_list'))
        self.assertEqual(response.status_code, 200)

    def test_settings_view(self):
        response = self.client.get(reverse('settings_view'))
        self.assertEqual(response.status_code, 200)

    def test_settings_helper(self):
        set_setting('test_key', 'test_value')
        self.assertEqual(get_setting('test_key'), 'test_value')
        # Default fallback
        self.assertEqual(get_setting('browser_type'), 'chromium')

    def test_browser_launch_and_close(self):
        # Verify launch_browser executes and shuts down cleanly in headless mode
        p, b, c, pg = launch_browser(headless=True)
        self.assertIsNotNone(b)
        self.assertIsNotNone(pg)
        pg.close()
        c.close()
        b.close()
        p.stop()

    def test_proxy_health_and_ping_views(self):
        from unittest.mock import patch
        # Create a test proxy
        proxy = Proxy.objects.create(
            ip="127.0.0.1",
            port=8080,
            protocol="http",
            health_status="untested"
        )
        self.assertEqual(proxy.health_status, "untested")
        
        # Test single proxy ping endpoint (will fail connection to 127.0.0.1:8080 and mark offline/unreachable)
        response = self.client.get(reverse('test_single_proxy', args=[proxy.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        proxy.refresh_from_db()
        self.assertEqual(proxy.health_status, "offline")
        self.assertFalse(proxy.is_active)
        self.assertIsNotNone(proxy.error_message)

        # Test batch verification endpoint
        with patch('threading.Thread.start'):
            response = self.client.get(reverse('trigger_test_proxies'), follow=True)
            self.assertEqual(response.status_code, 200)


