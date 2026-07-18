# AGENTS.md

## Project

ArmGPT bridges Acorn and Archimedes serial terminals to AI backends. User-facing responses should be short, friendly, and grounded in the project's ARM/Acorn source material.

## Prompt Grounding

- Treat `data/arm_docs/*.txt` as the primary source corpus for ARM, Acorn, Archimedes, RISC OS, and ArmGPT history.
- When changing prompt construction or response generation, preserve explicit retrieval or injection from `data/arm_docs`.
- Do not rely on a model's general memory for project history when repository docs can be used.
- Keep serial responses concise: usually 1-2 sentences.

## Backend Notes

- `arm_gpt_server.py` uses Ollama chat plus embeddings and `data/arm_index.jsonl`.
- `serial_codex_interface.py` shells out to `codex exec` and retrieves lightweight context directly from `data/arm_docs`.
- `serial_llm_interface_lite.py` and `serial_llm_interface.py` are legacy local-model paths.

## Verification

- Run `python3 -m py_compile arm_gpt_server.py build_index.py serial_codex_interface.py serial_llm_interface.py serial_llm_interface_lite.py` after Python changes.
- Run `python3 serial_codex_interface.py --help` after changing the Codex CLI runner.
