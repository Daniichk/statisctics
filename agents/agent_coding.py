# agents/agent_coding.py
"""
Simple CLI agent: reads a prompt, asks an LLM to produce Python code,
extracts code blocks and writes them to a file.
Requires OPENAI_API_KEY env var and `openai` python package.
"""

import os
import re
import sys
import argparse
import openai

SYSTEM_PROMPT = (
    "You are a helpful assistant that ONLY outputs code when asked to 'write code'. "
    "When asked to produce a file, respond with a single fenced code block containing "
    "the file contents. If multiple files are requested, prefix each block with a "
    "comment line `# filename: <name>` just above the code block."
)

def generate_code(prompt: str, model: str = "gpt-4", temperature: float = 0.2) -> str:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        raise RuntimeError("Set OPENAI_API_KEY environment variable.")
    resp = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        max_tokens=3000,
    )
    return resp["choices"][0]["message"]["content"]

def extract_code_blocks(text: str):
    # captures optional filename comment then the fenced code block
    pattern = re.compile(
        r"(?:#\s*filename:\s*(?P<fname>[^\n\r]+)\s*)?```(?:python)?\n(?P<code>.*?)(?:\n)?```",
        re.DOTALL | re.IGNORECASE,
    )
    matches = pattern.finditer(text)
    files = []
    for i, m in enumerate(matches, start=1):
        fname = m.group("fname") or f"generated_{i}.py"
        code = m.group("code").rstrip() + "\n"
        files.append((fname.strip(), code))
    # If no fenced blocks, treat whole response as a single file
    if not files and text.strip():
        files = [("generated_1.py", text)]
    return files

def write_files(files, out_dir="."):
    os.makedirs(out_dir, exist_ok=True)
    written = []
    for fname, code in files:
        path = os.path.join(out_dir, fname)
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)
        written.append(path)
    return written

def main():
    parser = argparse.ArgumentParser(description="Agent that turns prompts into code files.")
    parser.add_argument("prompt", nargs="?", help="Prompt text (if omitted, will read from stdin)")
    parser.add_argument("--model", default="gpt-4", help="Model to call")
    parser.add_argument("--out", default=".", help="Output directory for generated files")
    args = parser.parse_args()

    if args.prompt:
        prompt = args.prompt
    else:
        prompt = sys.stdin.read().strip()
        if not prompt:
            parser.error("No prompt provided (positional or via stdin).")

    resp_text = generate_code(prompt, model=args.model)
    files = extract_code_blocks(resp_text)
    written = write_files(files, out_dir=args.out)
    print("Wrote files:")
    for p in written:
        print(" -", p)

if __name__ == "__main__":
    main()
