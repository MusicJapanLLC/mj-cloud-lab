#!/usr/bin/env python3
"""Proof of real GitHub-hosted Linux VM resources; no credentials or private data."""
from __future__ import annotations
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys

def measure():
    ram=None
    if os.path.isfile("/proc/meminfo"):
        with open("/proc/meminfo","rt",encoding="utf-8") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    ram=round(int(line.split()[1])*1024/2**30,2)
                    break
    disk=shutil.disk_usage(os.getcwd())
    gpu_name=None
    if shutil.which("nvidia-smi"):
        try:
            proc=subprocess.run(["nvidia-smi","--query-gpu=name,memory.total",
                "--format=csv,noheader"],text=True,capture_output=True,timeout=5,check=False)
            if proc.returncode==0:
                gpu_name=proc.stdout.strip()[:160]
        except (OSError,subprocess.TimeoutExpired):
            pass
    return {"schema":"music-japan.cloud-vm-proof/1.0",
        "source":"github_hosted_standard_runner",
        "cpu_count":os.cpu_count(),
        "ram_gib":ram,"disk_total_gib":round(disk.total/2**30,2),
        "disk_free_gib":round(disk.free/2**30,2),
        "gpu_name":gpu_name,"system":platform.system(),
        "architecture":platform.machine(),
        "model_credits":0,"new_paid_services":0,
        "private_data_transferred":False}

def main():
    value=measure()
    if value["system"]!="Linux" or not value["cpu_count"] or not value["ram_gib"]:
        raise SystemExit("LINUX_VM_PROOF_FAILED")
    raw=json.dumps(value,sort_keys=True,separators=(",",":")).encode()
    value["proof_sha256"]=hashlib.sha256(raw).hexdigest()
    print(json.dumps(value,sort_keys=True,indent=2))
    return 0

if __name__=="__main__":
    sys.exit(main())
