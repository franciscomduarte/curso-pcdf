# Curso PCDF — Sistemas Multiagentes com IA

Material da disciplina **Sistemas Multiagentes com IA** (50h, 70% prática).
Aulas em HTML estático + código Python de exemplo.

**Prof. Francisco Molina Jr**

## Como ver

Abra `index.html` no navegador (ou publique via GitHub Pages).
As aulas ficam em `aulas/` e compartilham o mesmo tema (`assets/`).

## Estrutura

```
curso-pcdf/
├── index.html                      # índice das aulas
├── assets/
│   ├── estilo.css                  # sistema de design (navy/ouro/teal)
│   ├── aula.js                     # progresso de scroll, reveal, realçador Python
│   └── logo-pcdf.png               # brasão oficial da PCDF
├── aulas/
│   ├── aula-01-fundamentos.html    # ✅ pronta
│   └── aula-02-agente-do-zero.html # ✅ pronta
└── codigo/
    └── modulo-02-agente-do-zero/   # código Python da Aula 2 (roda sem chave)
        ├── agente_do_zero.py
        ├── solucao_exercicio.py
        └── README.md
```

## Rodar o código da Aula 2

```bash
cd codigo/modulo-02-agente-do-zero
python agente_do_zero.py          # usa um LLM falso (mock), sem chave de API
```

Para usar o Claude real: `pip install anthropic`, `export ANTHROPIC_API_KEY=...`
e troque a implementação do LLM (ver Aula 2).

## Publicar no GitHub Pages

Settings → Pages → Branch `main` / `/root`. Fica em
`https://franciscomduarte.github.io/curso-pcdf/`.

## Status

- [x] Aula 1 — Fundamentos
- [x] Aula 2 — Agente do zero
- [ ] Aulas 3 a 7
