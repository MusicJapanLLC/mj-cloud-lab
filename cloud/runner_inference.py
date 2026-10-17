#!/usr/bin/env python3
"""Run an openly licensed GGUF model on an ephemeral GitHub Linux VM.

Locally downloaded SHA-verified model and llama.cpp; no AI vendor API call.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

MODEL_ID="mj-cloud-qwen3.5-0.8b"
MODEL_SHA="57d1997790d1744fba5b40a7317df71ea5e2acee28c47e78f0cce39c0703f8cf"
MODEL_LICENSE="apache-2.0"

def checksum(path:Path)->str:
    digest=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):
            digest.update(block)
    return digest.hexdigest()

def get(url,body=None,timeout=9):
    req=urllib.request.Request(url,data=None if body is None else json.dumps(body).encode(),
        headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=timeout) as response:
        if response.status!=200:raise ValueError("INVALID_HTTP_"+str(response.status))
        return json.loads(response.read(1024*1024))

def serve_and_prove(binary:Path,weights:Path,port=18082)->dict:
    if checksum(weights)!=MODEL_SHA:
        raise ValueError("MODEL_WEIGHTS_SHA256_MISMATCH")
    if not binary.is_file():
        raise ValueError("LLAMA_CPP_BINARY_MISSING")
    cmd=[str(binary),"-m",str(weights),"--alias",MODEL_ID,
         "--host","127.0.0.1","--port",str(port),
         "-c","1024","-t","4","-ngl","0","-np","1",
         "--no-webui","--log-disable"]
    proc=subprocess.Popen(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                          stdin=subprocess.DEVNULL)
    start=time.monotonic()
    try:
        ready=False
        while time.monotonic()-start<70:
            if proc.poll() is not None:
                raise RuntimeError("LLAMA_CPP_EXIT_"+str(proc.returncode))
            try:
                health=get("http://127.0.0.1:"+str(port)+"/health",timeout=2)
                if health.get("status")=="ok":
                    ready=True;break
            except (urllib.error.URLError,OSError,TimeoutError,ValueError):
                pass
            time.sleep(.5)
        if not ready:raise TimeoutError("MODEL_START_TIMEOUT")
        catalog=get("http://127.0.0.1:"+str(port)+"/v1/models")
        if MODEL_ID not in [x.get("id") for x in catalog.get("data",[])]:
            raise ValueError("REAL_MODEL_CATALOG_MISMATCH")
        prompt={"model":MODEL_ID,"messages":[
              {"role":"system","content":"Do not show analysis. Give one short direct answer."},
              {"role":"user","content":"Reply with exactly CLOUD_OK"}],
             "max_tokens":40,"temperature":0,"stream":False,
             "chat_template_kwargs":{"enable_thinking":False}}
        output=get("http://127.0.0.1:"+str(port)+"/v1/chat/completions",body=prompt,timeout=95)
        if output.get("model")!=MODEL_ID:
            raise ValueError("INFERENCE_MODEL_ID_MISMATCH")
        choices=output.get("choices",[])
        generated=(choices[0].get("message",{}).get("content") or "") if choices else ""
        if not isinstance(generated,str) or not generated.strip():
            raise ValueError("EMPTY_GENERATED_TEXT")
        return {"schema":"music-japan.cloud-inference-proof/1.0",
                "status":"ACTUAL_GENERATION_OBSERVED",
                "model_id":MODEL_ID,"model_license":MODEL_LICENSE,
                "quantized_weights_sha256":MODEL_SHA,
                "generated_text_sample":generated.strip()[:120],
                "output_sha256":hashlib.sha256(generated.encode()).hexdigest(),
                "elapsed_seconds":round(time.monotonic()-start,2),
                "inference_backend":"llama.cpp local process on GitHub Actions Linux",
                "provider_llm_api_calls":0,"paid_gpu_jobs":0,
                "external_model_credits_used":0}
    finally:
        proc.terminate()
        try:proc.wait(timeout=6)
        except subprocess.TimeoutExpired:proc.kill()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--binary",required=True,type=Path)
    parser.add_argument("--weights",required=True,type=Path)
    args=parser.parse_args()
    print(json.dumps(serve_and_prove(args.binary.resolve(),args.weights.resolve()),
        ensure_ascii=False,sort_keys=True,indent=2),flush=True)

if __name__=="__main__":
    main()
