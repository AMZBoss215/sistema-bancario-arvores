from __future__ import annotations
from typing import Optional, List, Tuple
from modelos import ContaBancaria, NoRB, Cor, EstatisticasOperacao


class ArvoreRubroNegra:
    def __init__(self, modo_detalhado: bool = False) -> None:
        self.NIL: NoRB = NoRB(conta=None, cor=Cor.PRETO)
        self.NIL.esquerda = self.NIL
        self.NIL.direita = self.NIL
        self.NIL.pai = self.NIL
        self.raiz: NoRB = self.NIL
        self.quantidade_nos: int = 0
        self.modo_detalhado: bool = modo_detalhado
        self.estatisticas: EstatisticasOperacao = EstatisticasOperacao()

    @property
    def tamanho(self) -> int:
        return self.quantidade_nos

    @property
    def esta_vazia(self) -> bool:
        return self.raiz == self.NIL

    @property
    def altura(self) -> int:
        def _calc_altura(no: NoRB) -> int:
            if no == self.NIL:
                return -1
            return 1 + max(_calc_altura(no.esquerda), _calc_altura(no.direita))
        return _calc_altura(self.raiz)

    def calcular_altura_negra(self) -> int:
        no = self.raiz
        bh = 0
        while no != self.NIL:
            if no.cor == Cor.PRETO:
                bh += 1
            no = no.esquerda
        return bh

    def renderizar_subarvore(self, raiz_local: NoRB, marcador_raiz: str = "[RAIZ]") -> str:
        linhas: List[str] = []

        def _imprimir(no: NoRB, prefixo: str = "", eh_esq: Optional[bool] = None) -> None:
            if no == self.NIL:
                return

            if no.direita != self.NIL:
                _imprimir(no.direita, prefixo + ("|       " if eh_esq is True else "        "), False)

            if eh_esq is None:
                marcador = f"{marcador_raiz} "
            elif eh_esq is False:
                marcador = "/---[D] "
            else:
                marcador = "\\---[E] "

            cor_tag = "PRETO" if no.cor == Cor.PRETO else "VERM"
            linhas.append(f"{prefixo}{marcador}({no.chave}) [{cor_tag}] {no.conta.titular}")

            if no.esquerda != self.NIL:
                _imprimir(no.esquerda, prefixo + ("|       " if eh_esq is False else "        "), True)

        _imprimir(raiz_local)
        return "\n".join(linhas)

    def _rotacao_esquerda(self, x: NoRB) -> None:
        y = x.direita
        x.direita = y.esquerda
        if y.esquerda != self.NIL:
            y.esquerda.pai = x
        y.pai = x.pai
        if x.pai == self.NIL:
            self.raiz = y
        elif x == x.pai.esquerda:
            x.pai.esquerda = y
        else:
            x.pai.direita = y
        y.esquerda = x
        x.pai = y
        self.estatisticas.rotacoes_simples_esquerda += 1

    def _rotacao_direita(self, y: NoRB) -> None:
        x = y.esquerda
        y.esquerda = x.direita
        if x.direita != self.NIL:
            x.direita.pai = y
        x.pai = y.pai
        if y.pai == self.NIL:
            self.raiz = x
        elif y == y.pai.direita:
            y.pai.direita = x
        else:
            y.pai.esquerda = x
        x.direita = y
        y.pai = x
        self.estatisticas.rotacoes_simples_direita += 1

    def buscar(self, numero_conta: int) -> Optional[ContaBancaria]:
        atual = self.raiz
        while atual != self.NIL:
            self.estatisticas.comparacoes += 1
            self.estatisticas.nos_visitados += 1
            if numero_conta == atual.chave:
                return atual.conta
            elif numero_conta < atual.chave:
                atual = atual.esquerda
            else:
                atual = atual.direita
        return None

    def _menor_no(self, no: NoRB) -> NoRB:
        atual = no
        while atual.esquerda != self.NIL:
            atual = atual.esquerda
        return atual

    def _maior_no(self, no: NoRB) -> NoRB:
        atual = no
        while atual.direita != self.NIL:
            atual = atual.direita
        return atual

    def obter_menor(self) -> Optional[ContaBancaria]:
        if self.raiz == self.NIL:
            return None
        return self._menor_no(self.raiz).conta

    def obter_maior(self) -> Optional[ContaBancaria]:
        if self.raiz == self.NIL:
            return None
        return self._maior_no(self.raiz).conta

    def caminhamento_em_ordem(self) -> List[ContaBancaria]:
        resultado: List[ContaBancaria] = []

        def _in_order(no: NoRB) -> None:
            if no != self.NIL:
                _in_order(no.esquerda)
                resultado.append(no.conta)
                _in_order(no.direita)

        _in_order(self.raiz)
        return resultado

    def caminhamento_pre_ordem(self) -> List[ContaBancaria]:
        resultado: List[ContaBancaria] = []

        def _pre_order(no: NoRB) -> None:
            if no != self.NIL:
                resultado.append(no.conta)
                _pre_order(no.esquerda)
                _pre_order(no.direita)

        _pre_order(self.raiz)
        return resultado

    def caminhamento_pos_ordem(self) -> List[ContaBancaria]:
        resultado: List[ContaBancaria] = []

        def _pos_order(no: NoRB) -> None:
            if no != self.NIL:
                _pos_order(no.esquerda)
                _pos_order(no.direita)
                resultado.append(no.conta)

        _pos_order(self.raiz)
        return resultado

    def inserir(self, conta: ContaBancaria) -> bool:
        if self.buscar(conta.numero_conta) is not None:
            if self.modo_detalhado:
                self.estatisticas.registrar_log(
                    f"[RUBRO-NEGRA] Falha na insercao: Conta com numero {conta.numero_conta} ja existente."
                )
            return False

        z = NoRB(conta=conta, cor=Cor.VERMELHO, esquerda=self.NIL, direita=self.NIL, pai=self.NIL)
        y = self.NIL
        x = self.raiz

        while x != self.NIL:
            y = x
            if z.chave < x.chave:
                x = x.esquerda
            else:
                x = x.direita

        z.pai = y
        if y == self.NIL:
            self.raiz = z
        elif z.chave < y.chave:
            y.esquerda = z
        else:
            y.direita = z

        self.quantidade_nos += 1

        if self.modo_detalhado:
            self.estatisticas.registrar_log(
                f"[RUBRO-NEGRA] Insercao da conta {conta.numero_conta} ({conta.titular}) como novo no VERMELHO."
            )

        self._inserir_fixup(z)
        return True

    def _inserir_fixup(self, z: NoRB) -> None:
        while z.pai.cor == Cor.VERMELHO:
            if z.pai == z.pai.pai.esquerda:
                u = z.pai.pai.direita
                if u.cor == Cor.VERMELHO:
                    antes_txt = self.renderizar_subarvore(z.pai.pai) if self.modo_detalhado else ""
                    z.pai.cor = Cor.PRETO
                    u.cor = Cor.PRETO
                    z.pai.pai.cor = Cor.VERMELHO
                    self.estatisticas.recoloracoes += 3
                    if self.modo_detalhado:
                        depois_txt = self.renderizar_subarvore(z.pai.pai)
                        msg = (
                            f"[REBALANCEAMENTO RUBRO-NEGRA - CASO 1: TIO VERMELHO]\n"
                            f"  * Conflito Vermelho-Vermelho: No ({z.chave}) e Pai ({z.pai.chave})\n"
                            f"  * Tio ({u.chave}) e Vermelho -> Aplicada Recoloracao:\n"
                            f"      - Pai ({z.pai.chave}) passa a ser PRETO\n"
                            f"      - Tio ({u.chave}) passa a ser PRETO\n"
                            f"      - Avo ({z.pai.pai.chave}) passa a ser VERMELHO\n\n"
                            f"  >>> Subarvore ANTES da Recoloracao:\n"
                            + "\n".join("    " + l for l in antes_txt.splitlines()) +
                            f"\n\n  >>> Subarvore DEPOIS da Recoloracao:\n"
                            + "\n".join("    " + l for l in depois_txt.splitlines())
                        )
                        self.estatisticas.registrar_log(msg)
                    z = z.pai.pai
                else:
                    if z == z.pai.direita:
                        antes_txt = self.renderizar_subarvore(z.pai.pai) if self.modo_detalhado else ""
                        z = z.pai
                        self._rotacao_esquerda(z)
                        if self.modo_detalhado:
                            depois_txt = self.renderizar_subarvore(z.pai.pai)
                            msg = (
                                f"[REBALANCEAMENTO RUBRO-NEGRA - CASO 2: TIO PRETO EM ZIGUE-ZAGUE (LR)]\n"
                                f"  * Conflito no No ({z.direita.chave}) com Pai ({z.chave})\n"
                                f"  * Passo 1: Rotacao a Esquerda no Pai ({z.chave}) -> Alinhamento em Caso LL\n\n"
                                f"  >>> Subarvore ANTES da Rotacao:\n"
                                + "\n".join("    " + l for l in antes_txt.splitlines()) +
                                f"\n\n  >>> Subarvore APOS PASSO 1 (Alinhada em LL):\n"
                                + "\n".join("    " + l for l in depois_txt.splitlines())
                            )
                            self.estatisticas.registrar_log(msg)
                    antes_txt = self.renderizar_subarvore(z.pai.pai) if self.modo_detalhado else ""
                    avo = z.pai.pai
                    pai = z.pai
                    pai.cor = Cor.PRETO
                    avo.cor = Cor.VERMELHO
                    self.estatisticas.recoloracoes += 2
                    self._rotacao_direita(avo)
                    if self.modo_detalhado:
                        depois_txt = self.renderizar_subarvore(pai)
                        msg = (
                            f"[REBALANCEAMENTO RUBRO-NEGRA - CASO 3: TIO PRETO EM LINHA RETA (LL)]\n"
                            f"  * Conflito no No ({z.chave}) com Pai ({pai.chave})\n"
                            f"  * Acao: Rotacao a Direita no Avo ({avo.chave}) e Ajuste de Cores:\n"
                            f"      - Pai ({pai.chave}) passa a ser PRETO\n"
                            f"      - Avo ({avo.chave}) passa a ser VERMELHO\n\n"
                            f"  >>> Subarvore ANTES da Rotacao e Recoloracao:\n"
                            + "\n".join("    " + l for l in antes_txt.splitlines()) +
                            f"\n\n  >>> Subarvore DEPOIS da Rotacao e Recoloracao (Balanceada):\n"
                            + "\n".join("    " + l for l in depois_txt.splitlines())
                        )
                        self.estatisticas.registrar_log(msg)
            else:
                u = z.pai.pai.esquerda
                if u.cor == Cor.VERMELHO:
                    antes_txt = self.renderizar_subarvore(z.pai.pai) if self.modo_detalhado else ""
                    z.pai.cor = Cor.PRETO
                    u.cor = Cor.PRETO
                    z.pai.pai.cor = Cor.VERMELHO
                    self.estatisticas.recoloracoes += 3
                    if self.modo_detalhado:
                        depois_txt = self.renderizar_subarvore(z.pai.pai)
                        msg = (
                            f"[REBALANCEAMENTO RUBRO-NEGRA - CASO 1: TIO VERMELHO]\n"
                            f"  * Conflito Vermelho-Vermelho: No ({z.chave}) e Pai ({z.pai.chave})\n"
                            f"  * Tio ({u.chave}) e Vermelho -> Aplicada Recoloracao:\n"
                            f"      - Pai ({z.pai.chave}) passa a ser PRETO\n"
                            f"      - Tio ({u.chave}) passa a ser PRETO\n"
                            f"      - Avo ({z.pai.pai.chave}) passa a ser VERMELHO\n\n"
                            f"  >>> Subarvore ANTES da Recoloracao:\n"
                            + "\n".join("    " + l for l in antes_txt.splitlines()) +
                            f"\n\n  >>> Subarvore DEPOIS da Recoloracao:\n"
                            + "\n".join("    " + l for l in depois_txt.splitlines())
                        )
                        self.estatisticas.registrar_log(msg)
                    z = z.pai.pai
                else:
                    if z == z.pai.esquerda:
                        antes_txt = self.renderizar_subarvore(z.pai.pai) if self.modo_detalhado else ""
                        z = z.pai
                        self._rotacao_direita(z)
                        if self.modo_detalhado:
                            depois_txt = self.renderizar_subarvore(z.pai.pai)
                            msg = (
                                f"[REBALANCEAMENTO RUBRO-NEGRA - CASO 2: TIO PRETO EM ZIGUE-ZAGUE (RL)]\n"
                                f"  * Conflito no No ({z.esquerda.chave}) com Pai ({z.chave})\n"
                                f"  * Passo 1: Rotacao a Direita no Pai ({z.chave}) -> Alinhamento em Caso RR\n\n"
                                f"  >>> Subarvore ANTES da Rotacao:\n"
                                + "\n".join("    " + l for l in antes_txt.splitlines()) +
                                f"\n\n  >>> Subarvore APOS PASSO 1 (Alinhada em RR):\n"
                                + "\n".join("    " + l for l in depois_txt.splitlines())
                            )
                            self.estatisticas.registrar_log(msg)
                    antes_txt = self.renderizar_subarvore(z.pai.pai) if self.modo_detalhado else ""
                    avo = z.pai.pai
                    pai = z.pai
                    pai.cor = Cor.PRETO
                    avo.cor = Cor.VERMELHO
                    self.estatisticas.recoloracoes += 2
                    self._rotacao_esquerda(avo)
                    if self.modo_detalhado:
                        depois_txt = self.renderizar_subarvore(pai)
                        msg = (
                            f"[REBALANCEAMENTO RUBRO-NEGRA - CASO 3: TIO PRETO EM LINHA RETA (RR)]\n"
                            f"  * Conflito no No ({z.chave}) com Pai ({pai.chave})\n"
                            f"  * Acao: Rotacao a Esquerda no Avo ({avo.chave}) e Ajuste de Cores:\n"
                            f"      - Pai ({pai.chave}) passa a ser PRETO\n"
                            f"      - Avo ({avo.chave}) passa a ser VERMELHO\n\n"
                            f"  >>> Subarvore ANTES da Rotacao e Recoloracao:\n"
                            + "\n".join("    " + l for l in antes_txt.splitlines()) +
                            f"\n\n  >>> Subarvore DEPOIS da Rotacao e Recoloracao (Balanceada):\n"
                            + "\n".join("    " + l for l in depois_txt.splitlines())
                        )
                        self.estatisticas.registrar_log(msg)

        if self.raiz.cor != Cor.PRETO:
            self.raiz.cor = Cor.PRETO
            self.estatisticas.recoloracoes += 1
            if self.modo_detalhado:
                self.estatisticas.registrar_log(
                    f"[RUBRO-NEGRA] Raiz ({self.raiz.chave}) recolorida para PRETO para satisfazer a Propriedade 2."
                )

    def _transplant(self, u: NoRB, v: NoRB) -> None:
        if u.pai == self.NIL:
            self.raiz = v
        elif u == u.pai.esquerda:
            u.pai.esquerda = v
        else:
            u.pai.direita = v
        v.pai = u.pai

    def remover(self, numero_conta: int) -> Optional[ContaBancaria]:
        z = self.raiz
        while z != self.NIL and z.chave != numero_conta:
            if numero_conta < z.chave:
                z = z.esquerda
            else:
                z = z.direita

        if z == self.NIL:
            return None

        conta_removida = z.conta
        self.quantidade_nos -= 1

        if self.modo_detalhado:
            self.estatisticas.registrar_log(
                f"[RUBRO-NEGRA] Conta {numero_conta} localizada para remocao."
            )

        y = z
        y_cor_original = y.cor

        if z.esquerda == self.NIL:
            x = z.direita
            self._transplant(z, z.direita)
        elif z.direita == self.NIL:
            x = z.esquerda
            self._transplant(z, z.esquerda)
        else:
            y = self._menor_no(z.direita)
            y_cor_original = y.cor
            x = y.direita
            if y.pai == z:
                x.pai = y
            else:
                self._transplant(y, y.direita)
                y.direita = z.direita
                y.direita.pai = y
            self._transplant(z, y)
            y.esquerda = z.esquerda
            y.esquerda.pai = y
            y.cor = z.cor

        if y_cor_original == Cor.PRETO:
            self._remover_fixup(x)

        return conta_removida

    def _remover_fixup(self, x: NoRB) -> None:
        while x != self.raiz and x.cor == Cor.PRETO:
            if x == x.pai.esquerda:
                w = x.pai.direita
                if w.cor == Cor.VERMELHO:
                    w.cor = Cor.PRETO
                    x.pai.cor = Cor.VERMELHO
                    self.estatisticas.recoloracoes += 2
                    self._rotacao_esquerda(x.pai)
                    if self.modo_detalhado:
                        self.estatisticas.registrar_log(
                            f"[REMOCAO RUBRO-NEGRA - CASO 1: IRMAO VERMELHO] Rotacao a Esquerda no Pai ({x.pai.chave}) e inversao de cores."
                        )
                    w = x.pai.direita

                if w.esquerda.cor == Cor.PRETO and w.direita.cor == Cor.PRETO:
                    w.cor = Cor.VERMELHO
                    self.estatisticas.recoloracoes += 1
                    if self.modo_detalhado:
                        self.estatisticas.registrar_log(
                            f"[REMOCAO RUBRO-NEGRA - CASO 2: IRMAO PRETO COM AMBOS FILHOS PRETOS] Irmao ({w.chave if w != self.NIL else 'NIL'}) recolorido para VERMELHO."
                        )
                    x = x.pai
                else:
                    if w.direita.cor == Cor.PRETO:
                        w.esquerda.cor = Cor.PRETO
                        w.cor = Cor.VERMELHO
                        self.estatisticas.recoloracoes += 2
                        self._rotacao_direita(w)
                        if self.modo_detalhado:
                            self.estatisticas.registrar_log(
                                f"[REMOCAO RUBRO-NEGRA - CASO 3: IRMAO PRETO COM FILHO DIREITO PRETO] Rotacao a Direita no Irmao ({w.chave if w != self.NIL else 'NIL'})."
                            )
                        w = x.pai.direita

                    w.cor = x.pai.cor
                    x.pai.cor = Cor.PRETO
                    w.direita.cor = Cor.PRETO
                    self.estatisticas.recoloracoes += 3
                    self._rotacao_esquerda(x.pai)
                    if self.modo_detalhado:
                        self.estatisticas.registrar_log(
                            f"[REMOCAO RUBRO-NEGRA - CASO 4: IRMAO PRETO COM FILHO DIREITO VERMELHO] Rotacao a Esquerda no Pai ({x.pai.chave}) e resolucao do duplo preto."
                        )
                    x = self.raiz
            else:
                w = x.pai.esquerda
                if w.cor == Cor.VERMELHO:
                    w.cor = Cor.PRETO
                    x.pai.cor = Cor.VERMELHO
                    self.estatisticas.recoloracoes += 2
                    self._rotacao_direita(x.pai)
                    if self.modo_detalhado:
                        self.estatisticas.registrar_log(
                            f"[REMOCAO RUBRO-NEGRA - CASO 1: IRMAO VERMELHO] Rotacao a Direita no Pai ({x.pai.chave}) e inversao de cores."
                        )
                    w = x.pai.esquerda

                if w.direita.cor == Cor.PRETO and w.esquerda.cor == Cor.PRETO:
                    w.cor = Cor.VERMELHO
                    self.estatisticas.recoloracoes += 1
                    if self.modo_detalhado:
                        self.estatisticas.registrar_log(
                            f"[REMOCAO RUBRO-NEGRA - CASO 2: IRMAO PRETO COM AMBOS FILHOS PRETOS] Irmao ({w.chave if w != self.NIL else 'NIL'}) recolorido para VERMELHO."
                        )
                    x = x.pai
                else:
                    if w.esquerda.cor == Cor.PRETO:
                        w.direita.cor = Cor.PRETO
                        w.cor = Cor.VERMELHO
                        self.estatisticas.recoloracoes += 2
                        self._rotacao_esquerda(w)
                        if self.modo_detalhado:
                            self.estatisticas.registrar_log(
                                f"[REMOCAO RUBRO-NEGRA - CASO 3: IRMAO PRETO COM FILHO ESQUERDO PRETO] Rotacao a Esquerda no Irmao ({w.chave if w != self.NIL else 'NIL'})."
                            )
                        w = x.pai.esquerda

                    w.cor = x.pai.cor
                    x.pai.cor = Cor.PRETO
                    w.esquerda.cor = Cor.PRETO
                    self.estatisticas.recoloracoes += 3
                    self._rotacao_direita(x.pai)
                    if self.modo_detalhado:
                        self.estatisticas.registrar_log(
                            f"[REMOCAO RUBRO-NEGRA - CASO 4: IRMAO PRETO COM FILHO ESQUERDO VERMELHO] Rotacao a Direita no Pai ({x.pai.chave}) e resolucao do duplo preto."
                        )
                    x = self.raiz

        if x.cor != Cor.PRETO:
            x.cor = Cor.PRETO
            self.estatisticas.recoloracoes += 1

    def validar_propriedades(self) -> Tuple[bool, str]:
        if self.raiz == self.NIL:
            return True, "Arvore vazia e valida (raiz e sentinela NIL pretos)."

        if self.raiz.cor != Cor.PRETO:
            return False, f"Violacao da Propriedade 2: A raiz ({self.raiz.chave}) deve ser PRETA, mas e {self.raiz.cor.value}."

        if self.NIL.cor != Cor.PRETO:
            return False, "Violacao da Propriedade 3: O sentinela NIL deve ser PRETO."

        erro: Optional[str] = None
        altura_negra_esperada: Optional[int] = None

        def _validar_no(no: NoRB, min_val: Optional[int], max_val: Optional[int], bh_atual: int) -> bool:
            nonlocal erro, altura_negra_esperada
            if erro is not None:
                return False

            if no == self.NIL:
                if altura_negra_esperada is None:
                    altura_negra_esperada = bh_atual
                elif bh_atual != altura_negra_esperada:
                    erro = f"Violacao da Propriedade 5: Caminhos com alturas negras divergentes (esperada: {altura_negra_esperada}, encontrada: {bh_atual})."
                    return False
                return True

            if no.cor not in (Cor.VERMELHO, Cor.PRETO):
                erro = f"Violacao da Propriedade 1: No ({no.chave}) com cor invalida {no.cor}."
                return False

            if min_val is not None and no.chave <= min_val:
                erro = f"Violacao da propriedade de ABB: Chave {no.chave} <= minimo permitido {min_val}."
                return False
            if max_val is not None and no.chave >= max_val:
                erro = f"Violacao da propriedade de ABB: Chave {no.chave} >= maximo permitido {max_val}."
                return False

            if no.cor == Cor.VERMELHO:
                if no.esquerda.cor == Cor.VERMELHO:
                    erro = f"Violacao da Propriedade 4: No VERMELHO ({no.chave}) possui filho esquerdo VERMELHO ({no.esquerda.chave})."
                    return False
                if no.direita.cor == Cor.VERMELHO:
                    erro = f"Violacao da Propriedade 4: No VERMELHO ({no.chave}) possui filho direito VERMELHO ({no.direita.chave})."
                    return False

            proximo_bh = bh_atual + (1 if no.cor == Cor.PRETO else 0)

            if not _validar_no(no.esquerda, min_val, no.chave, proximo_bh):
                return False
            if not _validar_no(no.direita, no.chave, max_val, proximo_bh):
                return False

            return True

        valido = _validar_no(self.raiz, None, None, 0)
        if not valido or erro is not None:
            return False, erro if erro else "Violacao detectada nas propriedades da Arvore Rubro-Negra."

        return True, f"Todas as 5 propriedades Rubro-Negras estao satisfeitas com sucesso (Altura Negra bh={altura_negra_esperada})."

    def exibir_arvore(self) -> None:
        if self.raiz == self.NIL:
            print("[Arvore Rubro-Negra Vazia]")
            return

        def _imprimir_horizontal(no: NoRB, prefixo: str = "", eh_esq: Optional[bool] = None) -> None:
            if no == self.NIL:
                return

            if no.direita != self.NIL:
                _imprimir_horizontal(no.direita, prefixo + ("|       " if eh_esq is True else "        "), False)

            if eh_esq is None:
                marcador = "[RAIZ] "
            elif eh_esq is False:
                marcador = "/---[D] "
            else:
                marcador = "\\---[E] "

            cor_tag = "PRETO" if no.cor == Cor.PRETO else "VERM"
            print(f"{prefixo}{marcador}({no.chave}) [{cor_tag}] {no.conta.titular}")

            if no.esquerda != self.NIL:
                _imprimir_horizontal(no.esquerda, prefixo + ("|       " if eh_esq is False else "        "), True)

        print(f"=== ESTRUTURA VISUAL DA ARVORE RUBRO-NEGRA (Total de Nos: {self.quantidade_nos}, Altura: {self.altura}, Altura Negra: {self.calcular_altura_negra()}) ===")
        print("Legenda: /---[D] Subarvore Direita | \\---[E] Subarvore Esquerda | [PRETO] No Preto | [VERM] No Vermelho\n")
        _imprimir_horizontal(self.raiz)
