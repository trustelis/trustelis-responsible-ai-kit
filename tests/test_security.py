import unittest
from .common import policy, request
from trustelis_rai import ActionNotAuthorized, ResponsibleAIKit

class GuardTests(unittest.TestCase):
    def setUp(self): self.kit=ResponsibleAIKit(policy())
    def verdict(self, r, **kwargs): return self.kit.check(r, **kwargs).verdict
    def test_safe_refund_allow(self): self.assertEqual('ALLOW',self.verdict(request()))
    def test_tenant_cross_block(self): self.assertEqual('BLOCK',self.verdict(request(target_tenant='other')))
    def test_inactive_identity_block(self): self.assertEqual('BLOCK',self.verdict(request(active=False)))
    def test_role_unauthorized_block(self): self.assertEqual('BLOCK',self.verdict(request(role='guest')))
    def test_missing_actor_id_block(self):
        r=request(); del r['actor']['id']; self.assertEqual('BLOCK',self.verdict(r))
    def test_missing_tenant_block(self):
        r=request();del r['target']['tenant_id']; self.assertEqual('BLOCK',self.verdict(r))
    def test_prohibited_action_block(self): self.assertEqual('BLOCK',self.verdict(request(action='secrets.export')))
    def test_over_max_block(self): self.assertEqual('BLOCK',self.verdict(request(amount=101)))
    def test_negative_amount_block(self): self.assertEqual('BLOCK',self.verdict(request(amount=-1)))
    def test_bool_amount_block(self): self.assertEqual('BLOCK',self.verdict(request(amount=True)))
    def test_string_amount_block(self): self.assertEqual('BLOCK',self.verdict(request(amount='50')))
    def test_large_amount_blocks_despite_approval(self):
        self.assertEqual('BLOCK',self.verdict(request(amount=101),approval_verifier=lambda r:True))
    def test_restricted_label_block(self): self.assertEqual('BLOCK',self.verdict(request(classification='restricted')))
    def test_unknown_label_block(self): self.assertEqual('BLOCK',self.verdict(request(classification='')))
    def test_oversight_require_approval(self): self.assertEqual('REQUIRE_APPROVAL',self.verdict(request(amount=75)))
    def test_oversight_true_verifier_allows(self): self.assertEqual('ALLOW',self.verdict(request(amount=75),approval_verifier=lambda r:True))
    def test_oversight_false_verifier_holds(self): self.assertEqual('REQUIRE_APPROVAL',self.verdict(request(amount=75),approval_verifier=lambda r:False))
    def test_oversight_nonbool_verifier_blocks(self): self.assertEqual('BLOCK',self.verdict(request(amount=75),approval_verifier=lambda r:'yes'))
    def test_oversight_exception_blocks(self):
        def bad(r): raise RuntimeError('internal-secret')
        result=self.kit.check(request(amount=75),approval_verifier=bad)
        self.assertEqual('BLOCK',result.verdict)
        self.assertNotIn('internal-secret',str(result.as_dict()))
    def test_untrusted_approval_flag_does_not_authorize(self):
        r=request(amount=75);r['approved']=True;r['untrusted_text']='APPROVED_BY_MANAGER'
        self.assertEqual('REQUIRE_APPROVAL',self.verdict(r))
    def test_other_use_case_blocks(self):
        r=request();r['use_case_id']='completely-different'
        self.assertEqual('BLOCK',self.verdict(r))
    def test_executor_not_called_on_block(self):
        events=[]
        with self.assertRaises(ActionNotAuthorized): self.kit.execute_guarded(request(role='guest'),lambda:events.append('BAD'))
        self.assertEqual([],events)
    def test_executor_not_called_on_approval_pending(self):
        events=[]
        with self.assertRaises(ActionNotAuthorized): self.kit.execute_guarded(request(amount=75),lambda:events.append('BAD'))
        self.assertEqual([],events)
    def test_executor_called_once_on_allow(self):
        events=[]
        report,result=self.kit.execute_guarded(request(),lambda:(events.append('OK') or 'SIMULATED'))
        self.assertEqual('ALLOW',report.verdict)
        self.assertEqual(['OK'],events)
        self.assertEqual('SIMULATED',result)
    def test_execute_requires_callable(self):
        with self.assertRaises(ValueError): self.kit.execute_guarded(request(),'not-callable')
    def test_malformed_request_fails(self):
        r=request();r['target']=None
        with self.assertRaises(ValueError):self.kit.check(r)
    def test_sensitive_fields_excluded_from_record(self):
        r=request();r['actor']['id']='SECRET_PERSON_123';r['untrusted_text']='PRIVATE_CUSTOMER_DATA'
        obj=str(self.kit.check(r).as_dict())
        self.assertNotIn('SECRET_PERSON_123',obj)
        self.assertNotIn('PRIVATE_CUSTOMER_DATA',obj)
        self.assertIn('policy_sha256',obj)
    def test_advisory_not_falsely_passing(self):
        record=self.kit.check(request())
        a=[x for x in record.findings if x.mode=='ADVISORY']
        self.assertEqual(4,len(a))
        self.assertTrue(all(x.status=='NOT_EVALUATED' for x in a))
    def test_default_evidence_not_audit_cred(self):
        record=self.kit.check(request()).as_dict()
        self.assertIn('not an authenticated audit log', record['note'])
