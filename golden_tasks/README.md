# Golden Tasks

This suite protects the current Step 2 baseline behavior.

Included tasks:
- `v0_echo_roundtrip`
- `v0_trim_behavior`
- `v0_no_memory`
- `v0_no_tool_calls`
- `tool_allowed_read_only_success`
- `tool_unknown_denied_default`
- `tool_side_effect_requires_approval`
- `tool_scope_boundary_denied`
- `policy_user_safe_and_internal_detailed`
- `policy_config_load_success`
- `policy_config_invalid_hard_fail`
- `approval_nl_approve_executes_tool`
- `approval_nl_deny_cancels_tool`
- `approval_unrelated_input_auto_cancels`
- `approval_no_pending_guidance`
- `persona_loaded_default`
- `persona_prompt_builder_structure`
- `model_stub_default_path`
- `model_missing_key_error`
- `model_provider_failure_handled`
- `model_real_openai_success_optional` (only when `RUN_LIVE_MODEL_TEST=1`)
- `security_gitleaks_clean_repo`

Run:
```bash
python3 scripts/run_golden_tasks.py
```

Optional live model check:
```bash
MODEL_PROVIDER=openai OPENAI_API_KEY=... RUN_LIVE_MODEL_TEST=1 python3 scripts/run_golden_tasks.py
```
