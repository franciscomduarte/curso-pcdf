# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Course material for **Unidade 8 — Sistemas Multiagentes em Segurança Pública**, a
50h course (10 lessons × 5h) for the Polícia Civil do Distrito Federal (PCDF).
Everything is in **Portuguese (pt-BR)**. It is a **static HTML site** (no build
step) plus a **runnable Python code project per lesson**.

- `index.html` — course index (published via GitHub Pages: branch `main`, `/root`).
- `aulas/aula-0N-slug.html` — a self-contained lesson page.
- `codigo/aula-0N-slug/` — the Python project for that lesson.
- `assets/` — shared `estilo.css`, `aula.js`, `logo-pcdf.png`.

Status: Aulas 1–3 done; 4–10 pending. Fio condutor: a fictional system **SIGMA**
built incrementally across the lessons.

## Authoring workflow (how lessons get made)

Lessons are produced **one at a time**, on the user's command `Gere a Aula N`.
The user's long "PROMPT MESTRE" message defines the spec: pedagogical structure
(§5), per-lesson expectations (§25–34), content rules (§6, §7, §12–16), and
output format (§37: brief plan → full HTML → short tech notes).

1. Copy `aulas/_modelo-aula.html` (the 13-block skeleton) → `aulas/aula-0N-slug.html`.
2. Build the matching `codigo/aula-0N-slug/` project.
3. Update `index.html` (card → "Pronta", progress bar), the previous lesson's
   `.nav-aulas`, `README.md`, and the memory file.
4. Run QA (see below) before calling the lesson done.

### QA agents — run before finalizing a lesson

`.claude/agents/revisor-didatico.md` (didactic quality vs the master prompt) and
`.claude/agents/juiz-exemplos.md` (runs the code, checks HTML claims match
reality). New agent files require a session restart / `/agents` to be invocable
by name; otherwise run the equivalent via a general-purpose agent.

## Non-negotiable conventions

**Visual system — extend, never redesign.** `assets/estilo.css` owns the palette
(navy `--tinta` / ouro `--ouro` / teal `--teal`) and fonts (Fraunces display,
Inter body, JetBrains Mono code). New lesson-specific CSS goes at the end of
`estilo.css` in the same idiom. Reusable components: `.painel`, `.agenda`,
`.aviso` (`.ok`/`.perigo`/`.instrutor`/`.responsavel`), `.diagrama` (inline SVG),
`.mermaid`, `.codigo` (with `.barra` file bar), `.checkpoint` + `ul.lista-check`,
`.nivel` (`.basico`/`.intermediario`/`.avancado`), `.exercicio`, `.problemas`
(table), `.glossario` (`<dl>`), `.refs` (`<ol>`), `.gabarito` (`<details>`),
`.nav-aulas`, `.ancora`, `.grade.col-2`/`.col-3` + `.cartao`.

**`aula.js` behaviour** (loaded by every page): scroll progress bar, reveal-on-
scroll for `.reveal`, a small Python syntax highlighter that runs over
`<pre data-lang="python">` only (bash/yaml/output blocks use plain `<pre>`), and
Mermaid init if the page loaded the lib.

**Mermaid.** `securityLevel: 'strict'` → **no HTML in node labels** (`<br/>`,
`<small>` render literally). Quote any label containing punctuation:
`A["texto: com / pontuação"]`. Each lesson page loads the lib itself, right
before `aula.js`:
`<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>`.
Every diagram (SVG or Mermaid) needs a `<p class="legenda">` or explaining
paragraph immediately after it.

**5-hour agenda must total 300 min.** The `.agenda` list, the per-block
`<p class="rotulo">Bloco N · … · NN min</p>` headers, and the gabarito's
"Tempos (5h = 300 min)" line must be mutually consistent. Avaliação is its own
block (not merged with Debriefing).

**Content rules.** PCDF context, never generic examples. Synthetic data only,
with an explicit `AVISO_DADOS` string / on-page notice. Every lesson includes a
`.aviso responsavel` where an example could be read as an automated decision
about people — the IA is support, never the final authority on autoria, culpa,
indiciamento, prisão, medida cautelar. Security is discussed in *every* lesson
(not deferred to Aula 9). References must be real and primary (spec, official
docs, papers, norms) — verify URLs; cite legislation with a "não é aconselhamento
jurídico" caveat. Instructor notes (`.aviso instrutor`), checkpoints, and the
gabarito are kept separate from student-facing content.

## Code project conventions (`codigo/aula-0N-*/`)

- **Runs offline and deterministically with only `requirements.txt`**
  (`pydantic`, `python-dotenv`, `pytest`). Real integrations (OpenAI, MQTT, gRPC,
  the MCP SDK) go in `requirements-opcionais.txt` and are **always optional**.
- The LLM / transport / server is behind a `typing.Protocol`; ship a
  deterministic `Mock*` implementation plus the real one, selected by the
  **absence of an env var** (e.g. `extrator_padrao()` returns `MockExtrator`
  unless `OPENAI_API_KEY` is set and not the placeholder).
- OpenAI: use `client.responses.parse(..., text_format=PydanticModel)` /
  function calling. **Do not pass `temperature`** — newer models reject it.
  Model via `os.getenv("OPENAI_MODEL", "gpt-4.1-mini")`.
- MCP SDK is pinned `mcp>=1.2,<2` (v2 renamed `FastMCP` → `MCPServer`).
- Portuguese identifiers and docstrings. `from __future__ import annotations` at
  the top (targets 3.11+, must run on 3.10 — local Python is 3.10).
- Each project has its own `.gitignore` (`.venv/`, `.env`, `saida/`, generated
  `*_pb2*.py`, `mosquitto/passwd`). The root `.gitignore` only covers
  `__pycache__/`.
- The lesson HTML shows *real captured output* in terminal `<pre>` blocks —
  re-run and re-capture after changing code. Logging goes to stderr; note that
  in the HTML when showing output.
- **Windows console is cp1252**: never `print()` characters outside it (`≈`, `→`,
  `×`, box-drawing). Use `~`, `->`. Accented Latin (é, ã, ç) is fine. Non-cp1252
  chars are OK in comments/docstrings, just not in stdout.

## Commands

```bash
# View the site — just open index.html in a browser (no build).

# Per-lesson Python project (Windows PowerShell shown; bash: source .venv/bin/activate)
cd codigo/aula-03-mcp-integracao
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -q                                    # all tests (run offline, no keys)
pytest tests/test_mcp.py::test_escopo_nega_e_registra -q   # a single test

# Run a lesson's demos (varies per lesson — see each folder's README.md)
python main.py
python main_escopo.py          # aula 3
python main_lote.py            # aula 1
python main_local.py           # aula 2

# Optional "real integration" paths (need requirements-opcionais.txt, sometimes Docker)
pip install -r requirements-opcionais.txt
python mcp_real/cliente.py             # aula 3 — real MCP over stdio
python grpc_demo/servidor.py & python grpc_demo/cliente.py   # aula 2
docker compose up -d && python main_mqtt.py                  # aula 2 — needs broker
```

HTML sanity check used during authoring (tag balance across the pages):

```bash
python -c "import re;
for f in ['index.html','aulas/aula-03-mcp-integracao.html']:
 s=open(f,encoding='utf-8').read()
 print(f,[(t,len(re.findall(rf'<{t}\\b',s)),len(re.findall(rf'</{t}>',s))) for t in ('div','section','details','pre','table') if len(re.findall(rf'<{t}\\b',s))!=len(re.findall(rf'</{t}>',s))] or 'OK')"
```

## Git

`origin` is currently empty (first push creates `main`). Commit/push only when
the user asks. Do not stage the stray untracked PDF in `assets/`.
