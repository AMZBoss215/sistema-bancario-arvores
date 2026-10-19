from __future__ import annotations
from typing import Optional, List, Tuple
from modelos import ContaBancaria, NoAVL, EstatisticasOperacao


class ArvoreAVL:
    def __init__(self, modo_detalhado: bool = False) -> None:
        self.raiz: Optional[NoAVL] = None
        self.quantidade_nos: int = 0
        self.modo_detalhado: bool = modo_detalhado
        self.estatisticas: EstatisticasOperacao = EstatisticasOperacao()

    @property
    def tamanho(self) -> int:
        return self.quantidade_nos

    @property
    def altura(self) -> int:
        return NoAVL.get_altura(self.raiz)

    @property
    def esta_vazia(self) -> bool:
        return self.raiz is None

    def _rotacao_simples_direita(self, k2: NoAVL) -> NoAVL:
        k1 = k2.esquerda
        k2.esquerda = k1.direita
        k1.direita = k2
        k2.atualizar_altura()
        k1.atualizar_altura()
        self.estatisticas.rotacoes_simples_direita += 1
        if self.modo_detalhado:
            self.estatisticas.registrar_log(
                f"[AVL] Rotacao Simples a Direita (LL) em conta {k2.chave}. Nova raiz da subarvore: {k1.chave}"
            )
        return k1

    def _rotacao_simples_esquerda(self, k1: NoAVL) -> NoAVL:
        k2 = k1.direita
        k1.direita = k2.esquerda
        k2.esquerda = k1
        k1.atualizar_altura()
        k2.atualizar_altura()
        self.estatisticas.rotacoes_simples_esquerda += 1
        if self.modo_detalhado:
            self.estatisticas.registrar_log(
                f"[AVL] Rotacao Simples a Esquerda (RR) em conta {k1.chave}. Nova raiz da subarvore: {k2.chave}"
            )
        return k2

    def _rotacao_dupla_esquerda_direita(self, k3: NoAVL) -> NoAVL:
        if self.modo_detalhado:
            self.estatisticas.registrar_log(
                f"[AVL] Rotacao Dupla Esquerda-Direita (LR) em conta {k3.chave}: passo 1 (SE no filho {k3.esquerda.chave})"
            )
        k1 = k3.esquerda
        k2 = k1.direita
        k1.direita = k2.esquerda
        k2.esquerda = k1
        k1.atualizar_altura()
        k2.atualizar_altura()
        k3.esquerda = k2

        if self.modo_detalhado:
            self.estatisticas.registrar_log(
                f"[AVL] Rotacao Dupla Esquerda-Direita (LR) em conta {k3.chave}: passo 2 (SD no no {k3.chave})"
            )
        y = k3.esquerda
        k3.esquerda = y.direita
        y.direita = k3
        k3.atualizar_altura()
        y.atualizar_altura()

        self.estatisticas.rotacoes_duplas_esq_dir += 1
        return y

    def _rotacao_dupla_direita_esquerda(self, k1: NoAVL) -> NoAVL:
        if self.modo_detalhado:
            self.estatisticas.registrar_log(
                f"[AVL] Rotacao Dupla Direita-Esquerda (RL) em conta {k1.chave}: passo 1 (SD no filho {k1.direita.chave})"
            )
        k3 = k1.direita
        k2 = k3.esquerda
        k3.esquerda = k2.direita
        k2.direita = k3
        k3.atualizar_altura()
        k2.atualizar_altura()
        k1.direita = k2

        if self.modo_detalhado:
            self.estatisticas.registrar_log(
                f"[AVL] Rotacao Dupla Direita-Esquerda (RL) em conta {k1.chave}: passo 2 (SE no no {k1.chave})"
            )
        y = k1.direita
        k1.direita = y.esquerda
        y.esquerda = k1
        k1.atualizar_altura()
        y.atualizar_altura()

        self.estatisticas.rotacoes_duplas_dir_esq += 1
        return y

    def _rebalancear(self, no: NoAVL) -> NoAVL:
        no.atualizar_altura()
        fb = no.fator_balanceamento

        if fb > 1:
            if no.esquerda is not None and no.esquerda.fator_balanceamento >= 0:
                return self._rotacao_simples_direita(no)
            else:
                return self._rotacao_dupla_esquerda_direita(no)

        if fb < -1:
            if no.direita is not None and no.direita.fator_balanceamento <= 0:
                return self._rotacao_simples_esquerda(no)
            else:
                return self._rotacao_dupla_direita_esquerda(no)

        return no

    def inserir(self, conta: ContaBancaria) -> bool:
        inserido = False

        def _inserir_rec(no_atual: Optional[NoAVL]) -> Optional[NoAVL]:
            nonlocal inserido
            if no_atual is None:
                inserido = True
                self.quantidade_nos += 1
                if self.modo_detalhado:
                    self.estatisticas.registrar_log(
                        f"[AVL] Insercao da conta {conta.numero_conta} como novo no folha."
                    )
                return NoAVL(conta)

            if conta.numero_conta < no_atual.chave:
                no_atual.esquerda = _inserir_rec(no_atual.esquerda)
            elif conta.numero_conta > no_atual.chave:
                no_atual.direita = _inserir_rec(no_atual.direita)
            else:
                inserido = False
                if self.modo_detalhado:
                    self.estatisticas.registrar_log(
                        f"[AVL] Falha na insercao: Conta com numero {conta.numero_conta} ja existente."
                    )
                return no_atual

            return self._rebalancear(no_atual)

        self.raiz = _inserir_rec(self.raiz)
        return inserido

    def _menor_no(self, no: NoAVL) -> NoAVL:
        atual = no
        while atual.esquerda is not None:
            atual = atual.esquerda
        return atual

    def remover(self, numero_conta: int) -> Optional[ContaBancaria]:
        removido: Optional[ContaBancaria] = None

        def _remover_rec(no_atual: Optional[NoAVL], chave_alvo: int) -> Optional[NoAVL]:
            nonlocal removido
            if no_atual is None:
                return None

            if chave_alvo < no_atual.chave:
                no_atual.esquerda = _remover_rec(no_atual.esquerda, chave_alvo)
            elif chave_alvo > no_atual.chave:
                no_atual.direita = _remover_rec(no_atual.direita, chave_alvo)
            else:
                if removido is None:
                    removido = no_atual.conta
                    self.quantidade_nos -= 1
                    if self.modo_detalhado:
                        self.estatisticas.registrar_log(
                            f"[AVL] Conta {numero_conta} localizada para remocao."
                        )

                if no_atual.esquerda is None:
                    return no_atual.direita
                elif no_atual.direita is None:
                    return no_atual.esquerda

                sucessor = self._menor_no(no_atual.direita)
                no_atual.conta = sucessor.conta
                if self.modo_detalhado:
                    self.estatisticas.registrar_log(
                        f"[AVL] No com dois filhos substituido pelo sucessor em-ordem (conta {sucessor.chave})."
                    )
                no_atual.direita = _remover_rec(no_atual.direita, sucessor.chave)

            return self._rebalancear(no_atual)

        self.raiz = _remover_rec(self.raiz, numero_conta)
        return removido

    def buscar(self, numero_conta: int) -> Optional[ContaBancaria]:
        atual = self.raiz
        while atual is not None:
            self.estatisticas.comparacoes += 1
            self.estatisticas.nos_visitados += 1
            if numero_conta == atual.chave:
                return atual.conta
            elif numero_conta < atual.chave:
                atual = atual.esquerda
            else:
                atual = atual.direita
        return None

    def obter_menor(self) -> Optional[ContaBancaria]:
        if self.raiz is None:
            return None
        return self._menor_no(self.raiz).conta

    def obter_maior(self) -> Optional[ContaBancaria]:
        if self.raiz is None:
            return None
        atual = self.raiz
        while atual.direita is not None:
            atual = atual.direita
        return atual.conta

    def caminhamento_em_ordem(self) -> List[ContaBancaria]:
        resultado: List[ContaBancaria] = []

        def _in_order(no: Optional[NoAVL]) -> None:
            if no is not None:
                _in_order(no.esquerda)
                resultado.append(no.conta)
                _in_order(no.direita)

        _in_order(self.raiz)
        return resultado

    def caminhamento_pre_ordem(self) -> List[ContaBancaria]:
        resultado: List[ContaBancaria] = []

        def _pre_order(no: Optional[NoAVL]) -> None:
            if no is not None:
                resultado.append(no.conta)
                _pre_order(no.esquerda)
                _pre_order(no.direita)

        _pre_order(self.raiz)
        return resultado

    def caminhamento_pos_ordem(self) -> List[ContaBancaria]:
        resultado: List[ContaBancaria] = []

        def _pos_order(no: Optional[NoAVL]) -> None:
            if no is not None:
                _pos_order(no.esquerda)
                _pos_order(no.direita)
                resultado.append(no.conta)

        _pos_order(self.raiz)
        return resultado

    def validar_propriedades(self) -> Tuple[bool, str]:
        def _validar_no(
            no: Optional[NoAVL],
            min_val: Optional[int],
            max_val: Optional[int]
        ) -> Tuple[bool, str]:
            if no is None:
                return True, ""

            if min_val is not None and no.chave <= min_val:
                return False, f"Violacao da propriedade de ABB: chave {no.chave} <= minimo permitido {min_val}"
            if max_val is not None and no.chave >= max_val:
                return False, f"Violacao da propriedade de ABB: chave {no.chave} >= maximo permitido {max_val}"

            alt_esq = NoAVL.get_altura(no.esquerda)
            alt_dir = NoAVL.get_altura(no.direita)
            alt_esperada = 1 + max(alt_esq, alt_dir)

            if no.altura != alt_esperada:
                return False, f"Altura inconsistente no no {no.chave}: gravada={no.altura}, calculada={alt_esperada}"

            fb = alt_esq - alt_dir
            if abs(fb) > 1:
                return False, f"Desbalanceamento detectado no no {no.chave}: FB={fb} fora do intervalo [-1, 1]"

            valido_esq, erro_esq = _validar_no(no.esquerda, min_val, no.chave)
            if not valido_esq:
                return False, erro_esq

            valido_dir, erro_dir = _validar_no(no.direita, no.chave, max_val)
            if not valido_dir:
                return False, erro_dir

            return True, ""

        if self.raiz is None:
            return True, "Arvore vazia e valida."
        valido, msg = _validar_no(self.raiz, None, None)
        if valido:
            return True, "Todas as propriedades da Arvore AVL estao satisfeitas com sucesso."
        return False, msg

    def exibir_arvore(self) -> None:
        if self.raiz is None:
            print("Arvore AVL vazia.")
            return

        def _imprimir(no: Optional[NoAVL], prefixo: str = "", eh_filho_direito: bool = True) -> None:
            if no is not None:
                ramo = "\\-- " if eh_filho_direito else "+-- "
                print(f"{prefixo}{ramo}[Conta {no.chave} | h={no.altura} | FB={no.fator_balanceamento}] {no.conta.titular}")
                novo_prefixo = prefixo + ("    " if eh_filho_direito else "|   ")
                if no.esquerda is not None or no.direita is not None:
                    if no.esquerda is not None:
                        _imprimir(no.esquerda, novo_prefixo, False)
                    else:
                        print(f"{novo_prefixo}+-- [NIL]")
                    if no.direita is not None:
                        _imprimir(no.direita, novo_prefixo, True)
                    else:
                        print(f"{novo_prefixo}\\-- [NIL]")

        print(f"=== Estrutura da Arvore AVL (Total de Nos: {self.quantidade_nos}, Altura: {self.altura}) ===")
        print(f"[Raiz: Conta {self.raiz.chave} | h={self.raiz.altura} | FB={self.raiz.fator_balanceamento}] {self.raiz.conta.titular}")
        if self.raiz.esquerda is not None:
            _imprimir(self.raiz.esquerda, "", False)
        elif self.raiz.direita is not None:
            print("+-- [NIL]")
        if self.raiz.direita is not None:
            _imprimir(self.raiz.direita, "", True)
        elif self.raiz.esquerda is not None:
            print("\\-- [NIL]")
