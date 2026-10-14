import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from .common import ROOT

class CliTests(unittest.TestCase):
    def cmd(self,*args):
        env=os.environ.copy();env['PYTHONPATH']=str(ROOT/'src')
        return subprocess.run([sys.executable,'-m','trustelis_rai',*args],cwd=ROOT,
                              env=env,capture_output=True,text=True,timeout=12)
    def test_validation(self):
        r=self.cmd('validate','--policy','examples/refund_agent/policy.json')
        self.assertEqual(0,r.returncode);self.assertIn('PASS',r.stdout)
    def test_card_json(self):
        r=self.cmd('card','--policy','examples/refund_agent/policy.json')
        self.assertEqual(0,r.returncode)
        card=json.loads(r.stdout)
        self.assertEqual('customer-refund-agent',card['use_case']['id'])
    def test_card_markdown(self):
        r=self.cmd('card','--policy','examples/refund_agent/policy.json','--format','markdown')
        self.assertEqual(0,r.returncode);self.assertIn('NOT_EVALUATED',r.stdout)
    def test_allow_exit_code(self):
        r=self.cmd('check','--policy','examples/refund_agent/policy.json','--request','examples/refund_agent/request_allowed.json')
        self.assertEqual(0,r.returncode);self.assertEqual('ALLOW',json.loads(r.stdout)['verdict'])
    def test_approval_exit_code(self):
        r=self.cmd('check','--policy','examples/refund_agent/policy.json','--request','examples/refund_agent/request_needs_approval.json')
        self.assertEqual(4,r.returncode);self.assertEqual('REQUIRE_APPROVAL',json.loads(r.stdout)['verdict'])
    def test_block_exit_code(self):
        r=self.cmd('check','--policy','examples/refund_agent/policy.json','--request','examples/refund_agent/request_blocked.json')
        self.assertEqual(5,r.returncode);self.assertEqual('BLOCK',json.loads(r.stdout)['verdict'])
    def test_user_output_only_on_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'card.md'
            r=self.cmd('card','--policy','examples/refund_agent/policy.json','--format','markdown','--output',str(target))
            self.assertEqual(0,r.returncode)
            self.assertIn('Control Card',target.read_text())
    def test_invalid_policy_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'invalid.json';target.write_text('{}')
            r=self.cmd('validate','--policy',str(target))
            self.assertEqual(2,r.returncode)
