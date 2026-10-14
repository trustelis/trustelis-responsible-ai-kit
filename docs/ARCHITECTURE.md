# Architecture — developer kit, not enterprise control plane

```text
TRUSTED APP (identity + resource metadata)       UNTRUSTED AI AGENT
                |                                     |
                +--------------> PROPOSED ACTION <---+
                                      |
                             ActionRequest / local policy
                                      |
                        ResponsibleAIKit.check()
                                      |
                      +---------------+----------------+
                      |               |                |
                  ENFORCEMENT       ADVISORY        MINIMAL RECORD
                 auth/limits       reviews         no sensitive body
                 data/approval      marked gap      no durable evidence
                      |               |                |
                      +---------------+----------------+
                                      |
                     ALLOW / BLOCK / REQUIRE_APPROVAL
                                      |
               execute_guarded() only calls your executor on ALLOW
```

**Architectural invariants:** local action guard has no server credentials and no organizational policy authority. The company SaaS owns enterprise decisions, tenant membership, approvals, and runtime policy. Public SDK extensions may become adapters, never a shadow source of enterprise policy truth. The existing synthetic benchmark can be extended to test this kit through its public interface; it is not bundled or copied here.
