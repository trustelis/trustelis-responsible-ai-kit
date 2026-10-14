import unittest
from .common import policy
from trustelis_rai import ResponsibleAIKit

class ConfigurationTests(unittest.TestCase):
    def test_reference_valid(self): self.assertEqual(64, len(ResponsibleAIKit(policy()).policy_sha256))
    def test_missing_auth(self):
        p=policy(); del p['factors']['authorization']
        with self.assertRaises(ValueError): ResponsibleAIKit(p)
    def test_bad_auth_type(self):
        p=policy(); p['factors']['authorization']=None
        with self.assertRaises(ValueError): ResponsibleAIKit(p)
    def test_disabled_auth(self):
        p=policy(); p['factors']['authorization']={'enabled':False}
        with self.assertRaises(ValueError): ResponsibleAIKit(p)
    def test_tenant_must_be_enforced(self):
        p=policy(); p['factors']['authorization']['tenant_isolation']=False
        with self.assertRaises(ValueError): ResponsibleAIKit(p)
    def test_unknown_factor_fails_closed(self):
        p=policy(); p['factors']['magic_certified_ai']={'enabled':True}
        with self.assertRaisesRegex(ValueError,'Unknown factor'): ResponsibleAIKit(p)
    def test_unknown_auth_option_fails(self):
        p=policy(); p['factors']['authorization']['trust_model_approval']=True
        with self.assertRaises(ValueError): ResponsibleAIKit(p)
    def test_negative_limit_fails(self):
        p=policy(); p['factors']['action_limits']['maximum_amounts_usd']['refund.create']=-1
        with self.assertRaises(ValueError): ResponsibleAIKit(p)
    def test_boolean_limit_fails(self):
        p=policy(); p['factors']['action_limits']['maximum_amounts_usd']['refund.create']=True
        with self.assertRaises(ValueError): ResponsibleAIKit(p)
    def test_nan_limit_fails(self):
        p=policy(); p['factors']['action_limits']['maximum_amounts_usd']['refund.create']=float('nan')
        with self.assertRaises(ValueError): ResponsibleAIKit(p)
    def test_wrong_schema_version_fails(self):
        p=policy(); p['schema_version']='999'
        with self.assertRaises(ValueError): ResponsibleAIKit(p)
    def test_disabled_factor_only_flag(self):
        p=policy(); p['factors']['fairness']={'enabled':False}
        self.assertEqual('DISABLED', next(x for x in ResponsibleAIKit(p).control_card()['factors'] if x['name']=='fairness')['status'])
    def test_disabled_extra_fields_rejected(self):
        p=policy(); p['factors']['fairness']={'enabled':False,'review_note':'should be removed'}
        with self.assertRaises(ValueError): ResponsibleAIKit(p)
    def test_policy_snapshot_immutable_relative_to_input(self):
        p=policy(); kit=ResponsibleAIKit(p); h=kit.policy_sha256
        p['factors']['authorization']['deny_actions'].append('refund.create')
        self.assertEqual(h,kit.policy_sha256)
    def test_duplicate_roles_action_rejected(self):
        p=policy(); p['factors']['authorization']['allowed_actions_by_role']['support_agent'].append('refund.create')
        with self.assertRaises(ValueError): ResponsibleAIKit(p)
