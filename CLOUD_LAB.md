# Music Japan Cloud Lab

Public, synthetic-data-only cloud compute runner for Music Japan. Separate from company databases and private code.

- Public GitHub Actions standard hosted Ubuntu runners: 4 vCPU, 16 GB RAM, 14 GB SSD, no dedicated GPU
- Two independent hosted jobs: hardware audit and real zero-credit Qwen3.5 GGUF inference via llama.cpp
- Model: Apache 2.0 GGUF. Prebuilt binary and weights are SHA256 verified before executing
- No private business records, no app secrets, no purchased GPU resources, no AI vendor API credits
- All model execution occurs on runner loopback; no persistent public endpoints
- Workflow triggers by explicit manual dispatch or changes to cloud/trigger.txt

For stronger models use appropriate authorized GPU capacity. Hugging Face ZeroGPU supports shared 48GB/96GB VRAM with a limited free daily quota, not an always-on dedicated 2TB/64GB host.

Never push private chats, company files, tokens, or customer data here. Production integration must use authenticated scoped operations, not a public repository secret.
