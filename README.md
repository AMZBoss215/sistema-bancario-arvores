# 🏦 Sistema Bancário — Árvores Balanceadas (AVL e Rubro-Negra)

Trabalho Prático I da disciplina de **Algoritmos e Estruturas de Dados II (AED II)**.

---

## 📌 Visão Geral do Projeto

O objetivo deste projeto é projetar, implementar e comparar experimentalmente duas estruturas de dados balanceadas fundamentais:
- **Árvore AVL** (balanceamento rígido por altura)
- **Árvore Rubro-Negra** (balanceamento baseado em propriedades de cores)

### 🏢 Minimundo Escolhido: Sistema Bancário
- **Entidade:** `Conta` (`ContaBancaria`)
- **Chave Única:** Número da conta (identificador numérico para ordenação e busca)
- **Atributos:**
  - Número da conta
  - Nome do titular
  - Agência
  - Tipo de conta (Corrente / Poupança)
  - Saldo

---

## 📂 Estrutura Modular Planejada

```text
sistema-bancario-arvores/
├── docs/                 # Slides, enunciados e materiais locais (ignorado no Git)
├── modelos.py            # Definição das entidades (ContaBancaria) e nós base
├── avl.py                # Implementação completa da Árvore AVL e rotações
├── rubro_negra.py        # Implementação completa da Árvore Rubro-Negra e recolorações
├── experimentos.py       # Automação de testes e coleta de métricas comparativas
├── main.py               # Interface via terminal (CLI) para navegação interativa
├── .gitignore            # Arquivos e pastas ignorados no versionamento
└── README.md             # Documentação do projeto
```

---

## ⚙️ Pré-requisitos e Execução

- **Python 3.10+**

```bash
# Executar a aplicação interativa (após implementação)
python main.py

# Executar a bateria de experimentos
python experimentos.py
```

---

## 👥 Colaboração e Git

Para manter o repositório organizado e o fluxo de trabalho sem conflitos:
1. Mantenha a branch `main` estável.
2. Crie branches específicas para cada funcionalidade (ex: `feat/modelos-e-avl`, `feat/rubro-negra`, etc.).
3. Realize Pull Requests para revisão antes do merge na `main`.
