# agents/agent_coding_local.py
"""
Local-only CLI agent: reads a prompt, uses a local HF transformer model to produce code,
extracts code blocks and writes them to files.

Usage examples:
  python agents/agent_coding_local.py "Write a python file that prints Hello"
  python agents/agent_coding_local.py --model gpt2-medium "write code..."

Requires: transformers, torch
Optional (better results): use a dedicated code model you have downloaded.
"""

import os
import re
import sys
import argparse

SYSTEM_PROMPT = (
    "You are a helpful assistant that ONLY outputs code when asked to 'write code'. "
    "When asked to produce a file, respond with a single fenced code block containing "
    "the file contents. If multiple files are requested, prefix each block with a "
    "comment line `# filename: <name>` just above the code block."
)


def generate_code_local(prompt: str, model_name: str = "gpt2", temperature: float = 0.2, max_new_tokens: int = 512) -> str:
    """
    Generate text using a local Hugging Face transformers model.
    This uses the pipeline API for simplicity. Ensure transformers and torch are installed.
    The function prepends the system prompt to guide the model.
    """
    try:
        from transformers import pipeline
        import torch
    except Exception as e:
        raise RuntimeError("Install dependencies: pip install transformers torch") from e

    device = 0 if torch.cuda.is_available() else -1
    # Create a text-generation pipeline. The model_name should be a locally available model or a model id.
    generator = pipeline(
        "text-generation",
        model=model_name,
        tokenizer=model_name,
        device=device,
    )

    full_prompt = SYSTEM_PROMPT + "\n\n" + prompt.strip() + "\n\n"
    # generate
    out = generator(
        full_prompt,
        max_new_tokens=max_new_tokens,
        do_sample=True,
        temperature=temperature,
        top_p=0.95,
        # ensure we have an eos token to avoid warnings for some models
        pad_token_id=generator.tokenizer.eos_token_id,
    )

    generated = out[0]["generated_text"]
    # remove the prompt prefix if present
    if generated.startswith(full_prompt):
        generated = generated[len(full_prompt) :]

    return generated.strip()


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
        files = [("generated_1.py", text if text.endswith("\n") else text + "\n")]
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
    parser = argparse.ArgumentParser(description="Local agent that turns prompts into code files.")
    parser.add_argument("prompt", nargs="?", help="Prompt text (if omitted, will read from stdin)")
    parser.add_argument("--model", default="gpt2", help="Local HF model id (e.g., gpt2, gpt2-medium, or a code model)")
    parser.add_argument("--out", default=".", help="Output directory for generated files")
    parser.add_argument("--temperature", type=float, default=0.2, help="Sampling temperature")
    parser.add_argument("--max-tokens", type=int, default=512, help="Max tokens to generate")
    args = parser.parse_args()

    if args.prompt:
        prompt = args.prompt
    else:
        prompt = sys.stdin.read().strip()
        if not prompt:
            parser.error("No prompt provided (positional or via stdin).")

    resp_text = generate_code_local(prompt, model_name=args.model, temperature=args.temperature, max_new_tokens=args.max_tokens)
    files = extract_code_blocks(resp_text)
    written = write_files(files, out_dir=args.out)
    print("Wrote files:")
    for p in written:
        print(" -", p)


if __name__ == "__main__":
    main()
