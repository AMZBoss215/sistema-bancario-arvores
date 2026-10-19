from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union, List


@dataclass
class ContaBancaria:
    numero_conta: int
    titular: str
    agencia: str
    tipo: str
    saldo: float = 0.0

    def __post_init__(self) -> None:
        if not isinstance(self.numero_conta, int):
            raise TypeError("O número da conta deve ser um valor inteiro.")
        if self.numero_conta <= 0:
            raise ValueError("O número da conta deve ser um inteiro positivo.")

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
        return f"[{self.numero_conta} | {self.titular}]"


class NoAVL:
    def __init__(
        self,
        conta: ContaBancaria,
        esquerda: Optional[NoAVL] = None,
        direita: Optional[NoAVL] = None
    ) -> None:
        self.conta: ContaBancaria = conta
        self.esquerda: Optional[NoAVL] = esquerda
        self.direita: Optional[NoAVL] = direita
        self.altura: int = 0

    @property
    def chave(self) -> int:
        return self.conta.numero_conta

    @staticmethod
    def get_altura(no: Optional[NoAVL]) -> int:
        return no.altura if no is not None else -1

    def atualizar_altura(self) -> None:
        alt_esq = NoAVL.get_altura(self.esquerda)
        alt_dir = NoAVL.get_altura(self.direita)
        self.altura = 1 + max(alt_esq, alt_dir)

    @property
    def fator_balanceamento(self) -> int:
        return NoAVL.get_altura(self.esquerda) - NoAVL.get_altura(self.direita)

    def __repr__(self) -> str:
        return f"NoAVL({self.chave}, h={self.altura}, FB={self.fator_balanceamento})"


class Cor(Enum):
    VERMELHO = "VERMELHO"
    PRETO = "PRETO"


class NoRB:
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
        return self.conta is None

    def __repr__(self) -> str:
        if self.eh_nil:
            return "NIL(PRETO)"
        cor_tag = "V" if self.cor == Cor.VERMELHO else "P"
        return f"NoRB({self.chave}, cor={cor_tag})"


@dataclass
class EstatisticasOperacao:
    rotacoes_simples_esquerda: int = 0
    rotacoes_simples_direita: int = 0
    rotacoes_duplas_esq_dir: int = 0
    rotacoes_duplas_dir_esq: int = 0
    recoloracoes: int = 0
    comparacoes: int = 0
    nos_visitados: int = 0
    logs_detalhados: List[str] = field(default_factory=list)

    @property
    def total_rotacoes(self) -> int:
        return (
            self.rotacoes_simples_esquerda
            + self.rotacoes_simples_direita
            + (self.rotacoes_duplas_esq_dir * 2)
            + (self.rotacoes_duplas_dir_esq * 2)
        )

    def registrar_log(self, mensagem: str) -> None:
        self.logs_detalhados.append(mensagem)

    def resetar(self) -> None:
        self.rotacoes_simples_esquerda = 0
        self.rotacoes_simples_direita = 0
        self.rotacoes_duplas_esq_dir = 0
        self.rotacoes_duplas_dir_esq = 0
        self.recoloracoes = 0
        self.comparacoes = 0
        self.nos_visitados = 0
        self.logs_detalhados.clear()
