import json
import os
from datasets import load_dataset

def is_truly_refined(text):
    text_lower = text.lower()

    code_markers = ["```", "fn ", "impl ", "trait ", "use ", "mod ", "struct ", "enum ", "cargo ", "rustc "]
    if not any(marker in text_lower for marker in code_markers):
        return False, [], []

    if len(text_lower) < 3000:
        return False, [], []

    RUST_KEYWORDS = {
        "rust", "cargo build", "cargo check", "tokio::", "async-std",
        "lifetimes", "wasm-bindgen", "std::sync", "axum", "actix-web",
        "serde_json", "panic!", "pattern matching", "trait implementation",
        "tauri", "leptos", "diesel::", "sqlx", "arc<mutex>", "unsafe rust",
        "result<", "?;", "anyhow::result", "ownership", "borrowing"
    }
    AUTONOMY_KEYWORDS = {
        "swarm", "multi-agent", "self-correct", "compilation error", "reverse engineering",
        "dom tree", "playwright", "puppeteer", "html parsing", "network traffic interception",
        "agentic workflow", "autonomous execution", "error recovery loop", "state machine",
        "api endpoint mapping", "web scraping automation", "auto-heal", "test suite automation",
        "debug", "fix", "resolve", "issue", "patch", "trajectory"
    }

    matched_rust = [k for k in RUST_KEYWORDS if k in text_lower]
    matched_autonomy = [k for k in AUTONOMY_KEYWORDS if k in text_lower]

    if matched_rust and matched_autonomy:
        return True, matched_rust, matched_autonomy
    return False, [], []

def run_filter():
    premium_dataset = []
    TARGET_LIMIT = 300
    inspected_count = 0
    saved_count = 0

    # --- SUMBER 1: AgentTrove ---
    print("\n[1/4] Menapis AgentTrove...")
    try:
        ds = load_dataset("open-thoughts/AgentTrove", split="train", streaming=True)
        for row in ds:
            source = row.get("source") or row.get("original_source")
            if source not in {"code_contests", "freelancer", "neulab-mind2web"}:
                continue
            inspected_count += 1
            convs = row.get("conversations") or row.get("messages") or []
            if not convs:
                continue
            text = json.dumps(convs)
            ok, rt, at = is_truly_refined(text)
            if ok:
                saved_count += 1
                premium_dataset.append({
                    "id": saved_count, "source": f"AgentTrove/{source}",
                    "data_quality_tier": "ultra_premium_elite_v2",
                    "total_characters": len(text),
                    "matched_rust_tags": rt, "matched_autonomy_tags": at,
                    "conversations": convs
                })
                print(f"[ELITE] Ke-{saved_count} | {source} | Panjang: {len(text)}")
            if saved_count >= TARGET_LIMIT:
                break
    except Exception as e:
        print(f"Gagal AgentTrove: {e}")

    # --- SUMBER 2: Strandset-Rust-v1 ---
    if saved_count < TARGET_LIMIT:
        print("\n[2/4] Menapis Strandset-Rust-v1...")
        try:
            ds = load_dataset("Fortytwo-Network/Strandset-Rust-v1", split="train", streaming=True)
            for row in ds:
                inspected_count += 1
                text = f"{row.get('prompt', '')} {row.get('completion', '')}"
                ok, rt, at = is_truly_refined(text)
                if ok:
                    saved_count += 1
                    premium_dataset.append({
                        "id": saved_count, "source": "Strandset-Rust-v1",
                        "data_quality_tier": "ultra_premium_elite_v2",
                        "total_characters": len(text),
                        "matched_rust_tags": rt, "matched_autonomy_tags": at,
                        "conversations": [
                            {"role": "user", "content": row.get("prompt", "")},
                            {"role": "assistant", "content": row.get("completion", "")}
                        ]
                    })
                    print(f"[ELITE] Ke-{saved_count} | Strandset | Panjang: {len(text)}")
                if saved_count >= TARGET_LIMIT:
                    break
        except Exception as e:
            print(f"Gagal Strandset: {e}")

    # --- SUMBER 3: SWE-bench Verified ---
    if saved_count < TARGET_LIMIT:
        print("\n[3/4] Menapis SWE-bench Verified...")
        try:
            ds = load_dataset("SWE-bench/SWE-bench_Verified", split="test", streaming=True)
            for row in ds:
                inspected_count += 1
                text = f"{row.get('problem_statement', '')} {row.get('patch', '')}"
                ok, rt, at = is_truly_refined(text)
                if ok:
                    saved_count += 1
                    premium_dataset.append({
                        "id": saved_count, "source": "SWE-bench_Verified",
                        "data_quality_tier": "ultra_premium_elite_v2",
                        "total_characters": len(text),
                        "matched_rust_tags": rt, "matched_autonomy_tags": at,
                        "conversations": [
                            {"role": "user", "content": row.get('problem_statement', '')},
                            {"role": "assistant", "content": row.get('patch', '')}
                        ]
                    })
                    print(f"[ELITE] Ke-{saved_count} | SWE-bench | Panjang: {len(text)}")
                if saved_count >= TARGET_LIMIT:
                    break
        except Exception as e:
            print(f"Gagal SWE-bench: {e}")

    # --- SUMBER 4: SWE-agent-trajectories ---
    if saved_count < TARGET_LIMIT:
        print("\n[4/4] Menapis SWE-agent-trajectories...")
        try:
            ds = load_dataset("nebius/SWE-agent-trajectories", split="train", streaming=True)
            for row in ds:
                inspected_count += 1
                text = json.dumps(row.get("trajectory", ""))
                ok, rt, at = is_truly_refined(text)
                if ok:
                    saved_count += 1
                    premium_dataset.append({
                        "id": saved_count, "source": "SWE-agent-trajectories",
                        "data_quality_tier": "ultra_premium_elite_v2",
                        "total_characters": len(text),
                        "matched_rust_tags": rt, "matched_autonomy_tags": at,
                        "conversations": row.get("trajectory", [])
                    })
                    print(f"[ELITE] Ke-{saved_count} | Trajectories | Panjang: {len(text)}")
                if saved_count >= TARGET_LIMIT:
                    break
        except Exception as e:
            print(f"Gagal Trajectories: {e}")

    output_file = "elite_rust_autonomous_data_v2.jsonl"
    print(f"\nMenyimpan {len(premium_dataset)} baris data ultra-premium ke {output_file}...")
    with open(output_file, "w", encoding="utf-8") as f:
        for trace in premium_dataset:
            f.write(json.dumps(trace) + "\n")
    print(f"Sukses! Fail disimpan di: {os.path.abspath(output_file)}")

if __name__ == "__main__":
    run_filter()
