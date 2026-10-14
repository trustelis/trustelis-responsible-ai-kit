import unittest
from .common import policy,request
from trustelis_rai import ResponsibleAIKit,FactorFinding

class PluginTests(unittest.TestCase):
    def cfg(self):
        p=policy();p['factors']['custom_check']={'enabled':True,'description':'Synthetic check'}
        return p
    def test_custom_allow(self):
        kit=ResponsibleAIKit(self.cfg(),custom_factors={'custom_check':lambda r,c:FactorFinding('custom_check','ENFORCEMENT','PASS','OK')})
        self.assertEqual('ALLOW',kit.check(request()).verdict)
    def test_custom_denies(self):
        kit=ResponsibleAIKit(self.cfg(),custom_factors={'custom_check':lambda r,c:FactorFinding('custom_check','ENFORCEMENT','BLOCK','CUSTOM_DENY')})
        self.assertEqual('BLOCK',kit.check(request()).verdict)
    def test_custom_throws_fail_closed(self):
        def bad(r,c):raise RuntimeError('CUSTOM_SECRET')
        kit=ResponsibleAIKit(self.cfg(),custom_factors={'custom_check':bad})
        record=kit.check(request())
        self.assertEqual('BLOCK',record.verdict)
        self.assertNotIn('CUSTOM_SECRET',str(record.as_dict()))
    def test_custom_forged_info_fails(self):
        kit=ResponsibleAIKit(self.cfg(),custom_factors={'custom_check':lambda r,c:FactorFinding('custom_check','ADVISORY','PASS','WRONG')})
        self.assertEqual('BLOCK',kit.check(request()).verdict)
    def test_custom_missing_registration_fails(self):
        with self.assertRaises(ValueError):ResponsibleAIKit(self.cfg())
    def test_builtin_override_fails(self):
        with self.assertRaises(ValueError):ResponsibleAIKit(policy(),custom_factors={'authorization':lambda r,c:None})
    def test_custom_non_callable_fails(self):
        with self.assertRaises(ValueError):ResponsibleAIKit(self.cfg(),custom_factors={'custom_check':'bad'})
