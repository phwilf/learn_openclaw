# Golden Tasks (Step 2 Baseline)

This suite protects the current Step 2 baseline behavior.

Included tasks:
- `v0_echo_roundtrip`
- `v0_trim_behavior`
- `v0_no_memory`
- `v0_no_tool_calls`
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
