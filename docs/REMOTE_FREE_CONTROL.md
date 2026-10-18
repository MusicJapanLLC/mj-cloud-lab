# Remote-Desktop-independent engineering lane — 2026-10-18

## Scope and verified prerequisite

This implementation is a **live public-cloud audit lane**, not a claim that the two Windows computers can be controlled when offline. Its workflows run on GitHub-hosted Ubuntu runners, do not call Remote Desktop Commander or a paid AI API, and do not ingest company data. A public repo is intentionally limited to public GitHub metadata and synthetic tests.

- Public lane: `MusicJapanLLC/mj-cloud-lab` + `MusicJapanLLC/music-japan-cloud-inference` — cloud jobs and operational receipts without a PC session.
- Private lane already available elsewhere: `MusicJapanLLC/music-japan-ai-mesh` on `rd-lab/evidence-staging` uses GitHub Actions OIDC to prove exact repository, branch, workflow, and owner claims before accepting **metadata-only** Supabase R&D receipts.
- Device lane already available elsewhere: a Supabase `mj-rd-device-gateway` verifies per-device RSA proofs and nonce replay protections. One enrolled device does not constitute two-PC failover.
- Business documents and live credentials **never** enter this public lane. Any private task must go through the existing scoped private repository and authentication gateways.

## Operational behavior

1. Run the `Remote-Free Continuity Audit` GitHub Actions workflow manually or on the configured six-hour schedule *after merged to the default branch*. Pushes that modify the three referenced workflow/source paths also trigger the audit.
2. Standard Ubuntu runner executes six **network-free** unit tests. The collector then queries only the two explicitly approved public GitHub repositories' Actions metadata (read-only).
3. The job prints a canonical SHA-256 receipt for independently verifiable observations. An API failure makes the job fail rather than reporting fictitious health. A repository with no recent actions remains observable but **inactive**, not broken.
4. A failed or absent cloud run is not evidence of a Windows PC state. Monitoring does not re-enable a stopped AutonomyMesh task and does not provide a bypass for Windows or service-level controls.

## Next implementation gates (separate)

- Replace PC-by-PC interactive calls with the **existing signed, pull-based, allowlisted worker protocol** on each authorized machine. Reuse enrolled per-device keys and preserve STOP/disabled tasks until owner-approved repair is tested. No open arbitrary-shell RPC and no reusing browser session credentials.
- Add an independently tested second device registration and durable lease handoff; preserve exactly-once-or-retry-safe idempotency, bounded execution time and transparent audit receipts.
- Use GitHub-hosted or approved cloud runners for coding tests and independent technical inference; keep personal data and company research behind authenticated private gates.
- Verify failure injection: (A) Remote Desktop Commander disconnected, (B) laptop offline, (C) desktop offline, (D) cloud provider unavailable. State specifically what proceeds and what queues without pretending an offline PC can execute code.

## Costs

This GitHub Actions workflow is deployed **only in a public repository with standard GitHub-hosted runners** (free under GitHub's documented public-repo billing rule). It uses no model or storage API credits; GitHub's own service availability and fair-use limits still apply. Nothing here authorizes usage-based paid compute, private repo Actions overspend, or turning off security checks.
