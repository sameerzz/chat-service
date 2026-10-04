"""Run manually before promotion: python scripts/check_staging.py STAGING_URL.

Makes one real, billable LLM request. This is a smoke/latency check, not a
comprehensive AI quality evaluation or an enforced Cloud Deploy verify job.
"""
import argparse
import json
import time
import urllib.request


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--max-seconds", type=float, default=30)
    args = parser.parse_args()
    base = args.url.rstrip("/")
    with urllib.request.urlopen(base + "/books/101", timeout=30) as response:
        book = json.load(response)
    if book.get("id") != 101:
        raise SystemExit("FAIL: book API returned unexpected data")
    request = urllib.request.Request(
        base + "/chat",
        data=json.dumps({"message": "Recommend one beginner-friendly book about habits and briefly explain why."}).encode(),
        headers={"Content-Type": "application/json"},
    )
    start = time.monotonic()
    with urllib.request.urlopen(request, timeout=args.max_seconds) as response:
        result = json.load(response)
    elapsed = time.monotonic() - start
    reply = result.get("response")
    if not isinstance(reply, str) or not reply.strip() or elapsed > args.max_seconds:
        raise SystemExit("FAIL: empty reply or latency threshold exceeded")
    print(f"PASS: book API and live chat responded; chat latency {elapsed:.2f}s")
    print("Review this reply for recommendation quality before promotion:")
    print(reply)


if __name__ == "__main__":
    main()
