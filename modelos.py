"""
Módulo de Modelos de Domínio e Estruturas de Nós
Disciplina: Algoritmos e Estruturas de Dados II (AED II) - UFAM
Professor: Alternei Brito

Este módulo implementa:
1. A entidade bancária ContaBancaria (Minimundo: Sistema Bancário).
2. O nó da Árvore AVL (NoAVL) com controle de altura e fator de balanceamento (FB = alt_esq - alt_dir).
3. O nó da Árvore Rubro-Negra (NoRB) com enumeração de Cores e suporte a nó sentinela NIL.
4. A estrutura de Estatisticas para coleta de métricas exigidas nos experimentos e na defesa prática.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union, List


# =====================================================================
# 1. ENTIDADE DO MINIMUNDO: SISTEMA BANCÁRIO
# =====================================================================

@dataclass
class ContaBancaria:
    """
    Representa o registro bancário no sistema.
    
    A chave primária de ordenação é exclusivamente o 'numero_conta'.
    O saldo e demais dados cadastrais são atributos do registro e NÃO
    interferem na posição do nó na árvore (conforme Seção 3 do Enunciado).
    """
    numero_conta: int
    titular: str
    agencia: str
    tipo: str  # Ex.: 'Corrente', 'Poupanca', 'Salario'
    saldo: float = 0.0

    def __post_init__(self) -> None:
        if not isinstance(self.numero_conta, int):
            raise TypeError("O número da conta deve ser um valor inteiro.")
        if self.numero_conta <= 0:
            raise ValueError("O número da conta deve ser um inteiro positivo.")

    # Sobrecarga de operadores de comparação baseados estritamente na chave única
    def __eq__(self, outro: object) -> bool:
        if isinstance(outro, ContaBancaria):
            return self.numero_conta == outro.numero_conta
        if isinstance(outro, int):
            return self.numero_conta == outro
        return False

    def __lt__(self, outro: Union[ContaBancaria, int]) -> bool:
        if isinstance(outro, ContaBancaria):
            return self.numero_conta < outro.numero_conta
        if isinstance(outro, int):
            return self.numero_conta < outro
        return NotImplemented

    def __le__(self, outro: Union[ContaBancaria, int]) -> bool:
        return self < outro or self == outro

    def __gt__(self, outro: Union[ContaBancaria, int]) -> bool:
        if isinstance(outro, ContaBancaria):
            return self.numero_conta > outro.numero_conta
        if isinstance(outro, int):
            return self.numero_conta > outro
        return NotImplemented

    def __ge__(self, outro: Union[ContaBancaria, int]) -> bool:
        return self > outro or self == outro

    def __repr__(self) -> str:
        return (
            f"Conta(num={self.numero_conta}, titular='{self.titular}', "
            f"ag='{self.agencia}', tipo='{self.tipo}', saldo=R${self.saldo:,.2f})"
        )

    def resumo(self) -> str:
        """Formato compacto para visualização em árvores no terminal."""
        return f"[{self.numero_conta} | {self.titular}]"


# =====================================================================
# 2. NÓ DA ÁRVORE AVL
# =====================================================================

class NoAVL:
    """
    Nó para a Árvore AVL.
    
    Convenção de Altura das Aulas do Prof. Alternei (Aulas 3 e 4):
    - Altura de folha = 0 (número de arestas até uma folha).
    - Altura de subárvore vazia (None) = -1.
    - Fator de Balanceamento: FB = altura(subárvore_esquerda) - altura(subárvore_direita).
    - Nó balanceado: FB pertencente a {-1, 0, +1}.
    """
    def __init__(
        self,
        conta: ContaBancaria,
        esquerda: Optional[NoAVL] = None,
        direita: Optional[NoAVL] = None
    ) -> None:
        self.conta: ContaBancaria = conta
        self.esquerda: Optional[NoAVL] = esquerda
        self.direita: Optional[NoAVL] = direita
        self.altura: int = 0  # Inicia como folha (altura 0)

    @property
    def chave(self) -> int:
        return self.conta.numero_conta

    @staticmethod
    def get_altura(no: Optional[NoAVL]) -> int:
        """Retorna a altura do nó; se o nó for None, retorna -1 por convenção de arestas."""
        return no.altura if no is not None else -1

    def atualizar_altura(self) -> None:
        """Recalcula a altura do nó com base nas alturas dos filhos esquerdo e direito."""
        alt_esq = NoAVL.get_altura(self.esquerda)
        alt_dir = NoAVL.get_altura(self.direita)
        self.altura = 1 + max(alt_esq, alt_dir)

    @property
    def fator_balanceamento(self) -> int:
        """
        Calcula o Fator de Balanceamento (FB):
        FB = aE - aD (altura esquerda - altura direita).
        Fiel à fórmula da Aula 4 (Slide 6).
        """
        return NoAVL.get_altura(self.esquerda) - NoAVL.get_altura(self.direita)

    def __repr__(self) -> str:
        return f"NoAVL({self.chave}, h={self.altura}, FB={self.fator_balanceamento})"


# =====================================================================
# 3. NÓ DA ÁRVORE RUBRO-NEGRA
# =====================================================================

class Cor(Enum):
    VERMELHO = "VERMELHO"
    PRETO = "PRETO"


class NoRB:
    """
    Nó para a Árvore Rubro-Negra (Red-Black Tree).
    
    Implementação formal com ponteiro para pai e suporte a nó sentinela NIL compartilhado,
    conforme Aula 5 (Slide 7) e referencial de Cormen et al.
    """
    def __init__(
        self,
        conta: Optional[ContaBancaria] = None,
        cor: Cor = Cor.VERMELHO,
        esquerda: Optional[NoRB] = None,
        direita: Optional[NoRB] = None,
        pai: Optional[NoRB] = None
    ) -> None:
        self.conta: Optional[ContaBancaria] = conta
        self.cor: Cor = cor
        self.esquerda: Optional[NoRB] = esquerda
        self.direita: Optional[NoRB] = direita
        self.pai: Optional[NoRB] = pai

    @property
    def chave(self) -> Optional[int]:
        return self.conta.numero_conta if self.conta is not None else None

    @property
    def eh_nil(self) -> bool:
        """Identifica se este nó é a sentinela NIL."""
        return self.conta is None

    def __repr__(self) -> str:
        if self.eh_nil:
            return "NIL(PRETO)"
        cor_tag = "V" if self.cor == Cor.VERMELHO else "P"
        return f"NoRB({self.chave}, cor={cor_tag})"


# =====================================================================
# 4. ESTATÍSTICAS E LOGS DE OPERAÇÕES
# =====================================================================

@dataclass
class EstatisticasOperacao:
    """
    Armazena métricas e contadores de operações para os experimentos
    e para exibição de relatórios detalhados.
    """
    # Contadores de rotações
    rotacoes_simples_esquerda: int = 0
    rotacoes_simples_direita: int = 0
    rotacoes_duplas_esq_dir: int = 0
    rotacoes_duplas_dir_esq: int = 0

    # Contadores de modificações
    recoloracoes: int = 0

    # Métricas de execução
    comparacoes: int = 0
    nos_visitados: int = 0

    # Histórico de passos para o Modo Detalhado
    logs_detalhados: List[str] = field(default_factory=list)

    @property
    def total_rotacoes(self) -> int:
        """
        Total acumulado de rotações.
        Nota: Rotações duplas contabilizam como 1 operação de rotação dupla
        (composta por 2 rotações simples nos bastidores).
        """
        return (
            self.rotacoes_simples_esquerda
            + self.rotacoes_simples_direita
            + (self.rotacoes_duplas_esq_dir * 2)
            + (self.rotacoes_duplas_dir_esq * 2)
        )

    def registrar_log(self, mensagem: str) -> None:
        """Adiciona uma mensagem de evento ao histórico do modo detalhado."""
        self.logs_detalhados.append(mensagem)

    def resetar(self) -> None:
        """Zera todos os contadores para iniciar uma nova medição isolada."""
        self.rotacoes_simples_esquerda = 0
        self.rotacoes_simples_direita = 0
        self.rotacoes_duplas_esq_dir = 0
        self.rotacoes_duplas_dir_esq = 0
        self.recoloracoes = 0
        self.comparacoes = 0
        self.nos_visitados = 0
        self.logs_detalhados.clear()
