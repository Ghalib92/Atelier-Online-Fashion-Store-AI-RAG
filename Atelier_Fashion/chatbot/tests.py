from unittest.mock import patch

from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class ChatbotTests(APITestCase):
    @override_settings(OPENAI_API_KEY="", PINECONE_API_KEY="")
    def test_unconfigured_returns_503(self):
        # Cached chain must be cleared so the empty-key settings take effect.
        from chatbot import rag
        rag.get_rag_chain.cache_clear()
        resp = self.client.post(reverse("chat"), {"message": "What should I wear?"})
        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_empty_message_rejected(self):
        resp = self.client.post(reverse("chat"), {"message": ""})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("chatbot.views.answer_question", return_value="Try a navy blazer.")
    def test_answer_returned(self, _mock):
        resp = self.client.post(reverse("chat"), {"message": "Outfit ideas?"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["answer"], "Try a navy blazer.")
