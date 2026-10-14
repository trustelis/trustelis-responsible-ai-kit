import unittest
from .common import request,policy
from trustelis_rai import ResponsibleAIKit,card_markdown,decision_markdown

class ReportingTests(unittest.TestCase):
    def setUp(self):self.k=ResponsibleAIKit(policy())
    def test_card_shows_all_factors(self):
        card=self.k.control_card()
        self.assertEqual(9,len(card['factors']))
        self.assertIn('NOT_EVALUATED',card_markdown(card))
    def test_card_not_certification(self):
        card=self.k.control_card()
        self.assertIn('no compliance',card['disclaimer'])
    def test_decision_markdown(self):
        report=decision_markdown(self.k.check(request(amount=75)))
        self.assertIn('REQUIRE_APPROVAL',report)
        self.assertIn('not a persistent',report)
