import json

with open(r'C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        if data.get('step_index') in [12248, 12249, 12250, 12251]:
            print(f"Step {data.get('step_index')}:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
