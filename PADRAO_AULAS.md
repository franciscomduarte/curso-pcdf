# PADRÃO DE CONSTRUÇÃO DAS AULAS

## 1. OBJETIVO

Este documento define o padrão estrutural que deve ser seguido na criação das aulas.

Toda nova aula deve manter consistência com as demais aulas do curso.

---

# 2. ESTRUTURA OBRIGATÓRIA

Sempre que aplicável, uma aula deve conter:

1. Identificação
2. Problema/contextualização
3. Objetivos
4. Pré-requisitos
5. Conceitos fundamentais
6. Arquitetura ou modelo conceitual
7. Demonstração
8. Laboratório básico
9. Laboratório intermediário
10. Desafio avançado
11. Segurança
12. Debriefing
13. Avaliação
14. Transferência
15. Checklist
16. Referências

---

# 3. IDENTIFICAÇÃO

Incluir:

* título;
* número;
* unidade;
* duração;
* nível;
* pré-requisitos;
* tecnologias utilizadas.

---

# 4. CONTEXTUALIZAÇÃO

Começar apresentando:

* problema;
* cenário;
* necessidade;
* consequência;
* pergunta orientadora.

Evitar iniciar diretamente com definições técnicas.

---

# 5. OBJETIVOS

Apresentar entre 3 e 6 objetivos de aprendizagem.

Preferir verbos observáveis:

* implementar;
* analisar;
* comparar;
* configurar;
* diagnosticar;
* avaliar;
* projetar;
* justificar.

---

# 6. PRÉ-REQUISITOS

Informar claramente:

* conhecimentos;
* linguagens;
* ferramentas;
* conceitos;
* configuração de ambiente.

Não exigir conhecimento que a aula não tenha declarado.

---

# 7. CONCEITOS

Apresentar os conceitos em ordem crescente de complexidade.

Para conceitos importantes, utilizar:

**Definição → Exemplo → Contraexemplo → Aplicação**

---

# 8. ARQUITETURA

Quando a aula envolver sistemas, apresentar:

* componentes;
* responsabilidades;
* fluxo;
* entradas;
* saídas;
* dependências;
* pontos de falha.

Sempre que possível, utilizar diagramas.

---

# 9. DEMONSTRAÇÃO

A demonstração deve mostrar o conceito funcionando.

Evite demonstrações excessivamente longas.

O instrutor deve explicar:

* o que está fazendo;
* por que está fazendo;
* o que espera acontecer;
* como verificar o resultado.

---

# 10. LABORATÓRIO BÁSICO

Objetivo:

**primeiro contato com o conceito.**

Deve possuir instruções suficientemente claras para reduzir barreiras iniciais.

---

# 11. LABORATÓRIO INTERMEDIÁRIO

Objetivo:

**adaptar o conhecimento.**

O estudante deve modificar a solução inicial.

Evitar simplesmente repetir o laboratório básico.

---

# 12. DESAFIO AVANÇADO

Objetivo:

**desenvolver autonomia e tomada de decisão.**

O desafio deve apresentar requisitos, mas não necessariamente fornecer todos os passos.

Sempre que possível, exigir:

* decisão arquitetural;
* tratamento de erro;
* testes;
* segurança;
* justificativa.

---

# 13. SEGURANÇA

A seção de segurança deve ser contextualizada com o conteúdo da aula.

Evitar incluir apenas uma lista genérica.

Perguntar:

> "Como este conceito poderia ser utilizado de maneira insegura?"

E:

> "Como projetar a solução de forma mais segura?"

---

# 14. DEBRIEFING

Toda aula prática deve possuir um momento de reflexão.

Perguntas recomendadas:

* O que aprendemos?
* O que funcionou?
* O que falhou?
* Por que falhou?
* Que decisão foi mais importante?
* O que mudaria em produção?
* Quando não utilizaríamos essa abordagem?

---

# 15. AVALIAÇÃO

A avaliação deve conter, quando possível:

### Questões conceituais

Verificam compreensão.

### Questões práticas

Verificam aplicação.

### Problemas de diagnóstico

Verificam capacidade de encontrar erros.

### Problemas de transferência

Verificam aplicação em contexto novo.

### Justificativa

Verifica capacidade de explicar decisões.

---

# 16. CHECKPOINTS

Em aulas extensas, inserir checkpoints.

Exemplo:

> CHECKPOINT 1 — Você consegue explicar o conceito sem consultar o material?

> CHECKPOINT 2 — Você consegue executar a solução?

> CHECKPOINT 3 — Você consegue modificar a solução?

> CHECKPOINT 4 — Você consegue explicar por que ela funciona?

---

# 17. PROTÓTIPO E PRODUÇÃO

Quando houver código didático, indicar explicitamente:

> **Contexto didático**

e, quando necessário:

> **Em produção seria necessário...**

---

# 18. CÓDIGO

Todo código publicado deve:

* ser executável;
* ser consistente;
* possuir dependências identificadas;
* utilizar comandos válidos;
* evitar práticas inseguras;
* possuir instruções de execução;
* apresentar resultado esperado.

---

# 19. TECNOLOGIAS

Registrar:

* tecnologia;
* versão;
* finalidade;
* dependências;
* documentação oficial.

Evitar dependências desnecessárias.

---

# 20. REFERÊNCIAS

Priorizar:

1. documentação oficial;
2. especificações;
3. padrões;
4. artigos acadêmicos;
5. fontes institucionais;
6. materiais reconhecidos.

Não utilizar blogs aleatórios como autoridade principal para conceitos críticos.

---

# 21. CONTINUIDADE

Toda aula deve indicar:

### Recuperação

O que veio antes?

### Evolução

O que está sendo acrescentado?

### Preparação

O que será necessário depois?

---

# 22. REGRA DE OURO

Uma nova aula deve parecer parte do mesmo curso.

Ela pode introduzir novos conceitos e tecnologias, mas deve preservar:

* identidade;
* linguagem;
* estrutura;
* progressão;
* padrão de exercícios;
* padrão de avaliação;
* padrão visual;
* padrão de segurança.