from django.test import TestCase
from rest_framework.test import APIClient
from .engine.moto_manual_agent.agent_config import AGENT, MotoManualRAG

class MotoManualAgentTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
    def test_ask_manual_endpoint(self):
        response = self.client.post('/ask-manual/', {
            'query': 'Como trocar o óleo da moto?'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('answer', response.data)
        
    def test_agent_rag_action(self):
        action = AGENT.choose_action()
        self.assertIsInstance(action, MotoManualRAG)
