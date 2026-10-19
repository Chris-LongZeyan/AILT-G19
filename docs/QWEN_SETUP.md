# Qwen configuration

Use Alibaba Cloud Model Studio (Bailian), Beijing, with `qwen-flash`.
Copy `.env.example` to ignored `.env` for local use. On Render set:

- `LLM_API_KEY`: your private API key
- `LLM_BASE_URL`: the workspace-specific OpenAI-compatible URL shown in the console
- `LLM_MODEL=qwen-flash`
- `LLM_PROVIDER=Qwen`
- `LLM_TIMEOUT_SECONDS=30`
- `LLM_REQUESTS_PER_MINUTE=10`

The Beijing URL has this form:
`https://YOUR_WORKSPACE_ID.cn-beijing.maas.aliyuncs.com/compatible-mode/v1`.
Do not append `/chat/completions`; the adapter adds it. API key, region and
workspace must agree. The key must permit the exact model `qwen-flash`. If an
IP allowlist is enabled, allow the deployment's outbound IPs as well.

The adapter disables thinking and requests JSON Object output. Quote capitalization
is restored to the exact source; altered wording and unknown IDs are rejected. An HTTP 403
with “Access denied by API-Key restrictions” indicates key permissions or
restrictions, not a matching failure. Never commit the exported credential CSV,
`.env`, or deployment secrets.

After saving settings, deploy/restart the application, choose **AI matching**,
and try `dark insulated flask with a silver screw top`. With the initial
fictional catalogue, LF-001 should be returned with quotations from its record.
Try `purple telescope` for a no-match example. These are demonstration probes,
not independent evidence of general accuracy.

Run `python -m evaluation.run --mode ai` for the synthetic benchmark.
The benchmark makes real API requests and uses the configured rate limit.
It does not mutate the inventory or send photos or staff credentials.

Sources: [First API call](https://help.aliyun.com/zh/model-studio/first-api-call-to-qwen),
[Structured output](https://www.alibabacloud.com/help/en/model-studio/qwen-structured-output).
