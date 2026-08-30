# DESIGN INSTRUCIONAL — PADRÃO DO CURSO

## 1. PROPÓSITO

Este documento define os princípios de Design Instrucional que devem orientar a criação, revisão e evolução de todas as aulas deste curso.

Todo conteúdo produzido deve priorizar:

* aprendizagem significativa;
* aplicação prática;
* progressão de complexidade;
* desenvolvimento de competências;
* aprendizagem baseada em problemas;
* experimentação;
* reflexão;
* transferência do conhecimento;
* segurança;
* acessibilidade;
* atualização tecnológica.

O objetivo não é simplesmente produzir aulas com bom conteúdo, mas criar experiências que permitam ao estudante **compreender, aplicar, analisar, avaliar e criar**.

---

# 2. PRINCÍPIO FUNDAMENTAL

Toda aula deve responder claramente a cinco perguntas:

1. **Por que o estudante precisa aprender isso?**
2. **O que exatamente ele precisa aprender?**
3. **Como ele vai praticar?**
4. **Como saberemos se ele aprendeu?**
5. **Como ele utilizará esse conhecimento em um contexto diferente?**

Se uma aula não responder satisfatoriamente às cinco perguntas, ela deve ser revisada.

---

# 3. MODELO PEDAGÓGICO

A estrutura pedagógica preferencial é:

**Problema → Contextualização → Conceito → Demonstração → Prática → Experimentação → Desafio → Debriefing → Avaliação → Transferência**

Não é obrigatório que todas as etapas tenham o mesmo tamanho, mas todas devem ser consideradas no planejamento.

---

# 4. APRENDIZAGEM BASEADA EM PROBLEMAS

Sempre que possível, introduza o conteúdo a partir de um problema.

Evite iniciar uma aula técnica diretamente com:

> "Hoje vamos aprender X."

Prefira:

> "Temos este problema. Como poderíamos resolvê-lo?"

Depois introduza o conceito necessário para resolver o problema.

A tecnologia deve aparecer como **meio para resolver o problema**, e não como finalidade da aula.

---

# 5. OBJETIVOS DE APRENDIZAGEM

Os objetivos devem ser:

* específicos;
* observáveis;
* mensuráveis;
* relevantes;
* compatíveis com a carga horária;
* compatíveis com o nível do estudante.

Evite verbos vagos como:

* entender;
* conhecer;
* aprender;
* saber;
* familiarizar-se.

Prefira:

* explicar;
* implementar;
* comparar;
* analisar;
* diagnosticar;
* configurar;
* projetar;
* avaliar;
* justificar;
* construir.

### Modelo

> Ao final da aula, o estudante será capaz de **[ação observável]**, utilizando **[conhecimento/ferramenta]**, em **[contexto]**, respeitando **[critério ou restrição]**.

---

# 6. TAXONOMIA DE BLOOM

Sempre que possível, distribua os objetivos entre diferentes níveis cognitivos:

### Lembrar

Reconhecer conceitos, termos e definições.

### Compreender

Explicar conceitos com suas próprias palavras.

### Aplicar

Utilizar o conhecimento para resolver um problema.

### Analisar

Identificar relações, causas, componentes e problemas.

### Avaliar

Comparar alternativas e justificar decisões.

### Criar

Projetar ou construir uma solução.

Uma aula técnica avançada não deve limitar-se a lembrar e compreender.

---

# 7. PROGRESSÃO DE COMPLEXIDADE

Sempre que possível, utilizar:

**Básico → Intermediário → Avançado**

### Básico

Reprodução orientada.

### Intermediário

Adaptação e resolução de problemas.

### Avançado

Problema parcialmente aberto, exigindo decisões.

O nível avançado não deve ser apenas "mais código".

Ele deve exigir **mais raciocínio**.

---

# 8. CARGA COGNITIVA

Não confundir quantidade de conteúdo com qualidade de aprendizagem.

Ao planejar uma aula, considere:

* leitura;
* explicação;
* demonstração;
* configuração;
* programação;
* debugging;
* testes;
* discussão;
* reflexão;
* avaliação.

Evite introduzir muitos conceitos novos simultaneamente.

Quando houver alta complexidade, utilize:

* exemplos graduais;
* diagramas;
* analogias;
* decomposição;
* checkpoints;
* exercícios intermediários.

---

# 9. TEORIA E PRÁTICA

Para cada conceito importante, deve existir uma relação:

**Explicar → Demonstrar → Praticar → Avaliar**

Evite longos blocos exclusivamente teóricos.

Em cursos técnicos, o estudante deve experimentar o conceito o mais cedo possível.

---

# 10. APRENDIZAGEM POR EXPERIMENTAÇÃO

O estudante deve ter oportunidades para modificar:

* parâmetros;
* código;
* arquitetura;
* entradas;
* modelos;
* configurações;
* requisitos.

A pergunta pedagógica não deve ser apenas:

> "Faça isso."

Também deve incluir:

> "O que acontece se mudarmos isso?"

---

# 11. ERRO COMO MECANISMO DE APRENDIZAGEM

Sempre que adequado, apresente erros intencionais.

Exemplos:

* configuração incorreta;
* código com bug;
* arquitetura inadequada;
* ferramenta sem autorização;
* loop infinito;
* timeout ausente;
* validação insuficiente;
* prompt injection;
* tratamento de erro inadequado.

O estudante deve aprender a:

**identificar → diagnosticar → corrigir → explicar**

---

# 12. TRANSFERÊNCIA

Toda aula deve buscar pelo menos uma atividade que utilize o conhecimento em contexto diferente daquele apresentado.

Pergunta obrigatória:

> "O estudante conseguiria utilizar esse conhecimento se o problema mudasse?"

Se a resposta for não, a aula precisa de mais atividades de transferência.

---

# 13. TECNOLOGIA

Nunca ensinar uma ferramenta como se ela fosse o conceito.

Sempre separar:

### Conceito

O conhecimento que permanece válido mesmo se a tecnologia mudar.

### Implementação

A forma como determinada tecnologia implementa o conceito.

Exemplo:

**Conceito:** grafos, estados e transições.

**Tecnologia:** framework específico.

O estudante deve compreender o primeiro antes de depender do segundo.

---

# 14. QUANDO NÃO USAR A TECNOLOGIA

Sempre que possível, apresentar situações em que a tecnologia ensinada **não é a melhor solução**.

O estudante deve aprender:

> "Quando usar?"

e também:

> "Quando não usar?"

---

# 15. SEGURANÇA E RESPONSABILIDADE

Segurança não deve ser tratada apenas em uma aula específica.

Ela deve aparecer transversalmente.

Quando aplicável, abordar:

* autenticação;
* autorização;
* menor privilégio;
* proteção de credenciais;
* validação de entradas;
* prompt injection;
* excessive agency;
* vazamento de dados;
* auditoria;
* rastreabilidade;
* supervisão humana;
* privacidade;
* LGPD.

---

# 16. PROTÓTIPO × PRODUÇÃO

Toda simplificação didática relevante deve ser identificada.

Quando um exemplo não estiver pronto para produção, explicar:

* o que foi simplificado;
* por que foi simplificado;
* o que seria necessário em produção;
* quais riscos existem.

---

# 17. CONTINUIDADE ENTRE AULAS

Cada aula deve:

### Recuperar

Conhecimentos relevantes de aulas anteriores.

### Evoluir

Adicionar novos conceitos ou aumentar a complexidade.

### Preparar

Criar conhecimento necessário para a próxima aula.

Sempre que houver um projeto longitudinal, ele deve evoluir progressivamente.

---

# 18. INSTRUÇÃO PARA AGENTES

Ao criar ou revisar uma aula:

1. Leia este documento.
2. Leia `PADRAO_AULAS.md`.
3. Leia `RUBRICA_AULAS.md`.
4. Leia `GUIA_AVALIACAO.md`.
5. Consulte `CHECKLIST_PUBLICACAO.md`.
6. Analise as aulas anterior e posterior, quando disponíveis.
7. Identifique lacunas.
8. Proponha melhorias.
9. Só depois produza ou altere o conteúdo.

Nunca priorize estética ou quantidade de conteúdo em detrimento da aprendizagem.