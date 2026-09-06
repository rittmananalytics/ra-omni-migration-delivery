#!/usr/bin/env python3
"""Render `claude -p --output-format stream-json --verbose` as live, readable
lines, and write the turn's final response text to last_turn.txt for the
driver's gate check. Reads JSONL on stdin; prints human-readable lines,
unbuffered, as each event arrives."""
import json
import sys


def flatten(value, limit=160):
    text = json.dumps(value) if not isinstance(value, str) else value
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 3] + "..."


def main():
    final_chunks = []
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            print(line, flush=True)
            continue
        etype = event.get("type")
        if etype == "system" and event.get("subtype") == "init":
            print(f"[session {event.get('session_id', '?')[:8]} started]", flush=True)
        elif etype == "assistant":
            for block in (event.get("message") or {}).get("content", []):
                if block.get("type") == "text" and block.get("text", "").strip():
                    print(block["text"], flush=True)
                    final_chunks = [block["text"]]  # keep the latest text block(s)
                elif block.get("type") == "tool_use":
                    print(f"  > {block.get('name')}: {flatten(block.get('input', {}))}", flush=True)
        elif etype == "user":
            for block in (event.get("message") or {}).get("content", []):
                if isinstance(block, dict) and block.get("type") == "tool_result":
                    print(f"  < {flatten(block.get('content', ''))}", flush=True)
        elif etype == "result":
            text = event.get("result") or "\n".join(final_chunks)
            print("--- turn result ---", flush=True)
            print(text, flush=True)
            cost = event.get("total_cost_usd")
            dur = event.get("duration_ms")
            if cost is not None or dur is not None:
                print(f"[duration {round((dur or 0)/1000)}s, cost ${cost:.2f}]" if cost is not None
                      else f"[duration {round((dur or 0)/1000)}s]", flush=True)
            with open("last_turn.txt", "w", encoding="utf-8") as fh:
                fh.write(text or "")


if __name__ == "__main__":
    main()
