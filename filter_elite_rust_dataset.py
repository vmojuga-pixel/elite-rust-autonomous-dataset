import json
import os
from datasets import load_dataset

def run_ultra_premium_filter():
    TARGET_SOURCES = {"code_contests", "freelancer", "neulab-mind2web"}
    RUST_KEYWORDS = {
        "rust", "cargo build", "cargo check", "tokio::", "async-std", 
        "lifetimes", "wasm-bindgen", "std::sync", "axum", "actix-web", 
        "serde_json", "panic!", "pattern matching", "trait implementation",
        "tauri", "leptos", "diesel::", "sqlx", "arc<mutex>", "unsafe rust",
        "result<", "?;", "anyhow::result"
    }
    AUTONOMY_KEYWORDS = {
        "swarm", "multi-agent", "self-correct", "compilation error", "reverse engineering", 
        "dom tree", "playwright", "puppeteer", "html parsing", "network traffic interception",
        "agentic workflow", "autonomous execution", "error recovery loop", "state machine",
        "api endpoint mapping", "web scraping automation", "auto-heal", "test suite automation"
    }

    print("\nMemulakan penstriman dataset AgentTrove...")
    try:
        dataset = load_dataset("open-thoughts/AgentTrove", split="train", streaming=True)
    except Exception as e:
        print(f"Gagal memuatkan dataset: {e}")
        return

    premium_dataset = []
    TARGET_LIMIT = 200  
    inspected_count = 0
    saved_count = 0

    print("Menapis data...\n")

    for row in dataset:
        source = row.get("source") or row.get("original_source")
        if not source or source not in TARGET_SOURCES:
            continue
            
        inspected_count += 1
        conversations = row.get("conversations") or row.get("messages") or []
        if not conversations:
            continue
            
        conversation_text = json.dumps(conversations).lower()
        
        if len(conversation_text) < 6000:
            continue
            
        matched_rust = [k for k in RUST_KEYWORDS if k in conversation_text]
        matched_autonomy = [k for k in AUTONOMY_KEYWORDS if k in conversation_text]
        
        if matched_rust and matched_autonomy:
            saved_count += 1
            data_entry = {
                "id": saved_count,
                "source": source,
                "data_quality_tier": "ultra_premium_elite",
                "total_characters": len(conversation_text),
                "matched_rust_tags": matched_rust,
                "matched_autonomy_tags": matched_autonomy,
                "conversations": conversations
            }
            premium_dataset.append(data_entry)
            print(f"[ELITE DATA] Ke-{saved_count} | Panjang: {len(conversation_text)} | Diperiksa: {inspected_count}")
            
        if saved_count >= TARGET_LIMIT:
            break

    output_file = "elite_rust_autonomous_data.jsonl"
    print(f"\nMenyimpan {len(premium_dataset)} baris ke {output_file}...")
    with open(output_file, "w", encoding="utf-8") as f:
        for trace in premium_dataset:
            f.write(json.dumps(trace) + "\n")
    print(f"Sukses! Fail disimpan di: {os.path.abspath(output_file)}")

if __name__ == "__main__":
    run_ultra_premium_filter()
