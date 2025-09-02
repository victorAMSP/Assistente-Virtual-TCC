import spacy
import re
import difflib
from datetime import datetime
from typing import Dict, List, Optional, Any

class ProcessadorComandoService:
    def __init__(self):
        # Carrega spaCy 
        try:
            self.nlp = spacy.load("pt_core_news_sm")
        except:
            import os
            os.system("python -m spacy download pt_core_news_sm")
            self.nlp = spacy.load("pt_core_news_sm")

        # -------- Intents: palavras-chave e regex (ATUALIZADO) --------
        self.concluir_keywords = [
            "concluir", "concluí", "conclui", "concluido", "concluído",
            "finalizar", "finalizei", "finaliza", "terminei", "fiz", "já fiz",
            "marcar como concluído", "marcar como concluido", "feito"
        ]

        # Ampliado para cobrir variações de “me lembre depois”
        self.adiar_keywords = [
            "adiar", "adiei", "adiar o", "adiar a", "snooze",
            "lembrar depois", "lembre depois", "lembra depois",
            "lembre-me depois", "lembra-me depois", "me lembre depois", "me lembra depois",
            "mais tarde", "postergar", "posterga"
        ]
        # Regex robusto para formas “me lembre/lembra/lembre-me/lembra-me depois”
        self.regex_lembre_depois = re.compile(
            r"\b(?:me\s+)?lembre(?:-me)?\s+depois\b|\b(?:me\s+)?lembra(?:-me)?\s+depois\b|\blembrar\s+depois\b",
            re.IGNORECASE
        )

        # “em 10 min”, “em 15 minutos”
        self.regex_minutos_adiar = re.compile(r"\bem\s+(\d{1,3})\s*(?:min|minuto|minutos)\b", re.IGNORECASE)
        # “id 12”, “#12”, “(12)”, ou número solto (evitando horários)
        self.regex_id = re.compile(r"(?:id\s*|#|\()(\d+)\)?", re.IGNORECASE)

       
        self.regex_horario = re.compile(r"(\d{1,2})[:h](\d{0,2})")

        self.verbos_ignore = {
            "lembre", "lembrar", "avisa", "avisar", "coloca", "colocar",
            "registrar", "adicionar", "bote", "bota", "põe"
        }

        self.categorias_keywords = {
            "beber": "hidratação", "hidratar": "hidratação", "água": "hidratação", "suco": "hidratação",
            "correr": "exercício", "corrida": "exercício", "academia": "exercício", "musculação": "exercício",
            "exercício": "exercício", "caminhada": "exercício", "jogar bola": "exercício",
            "dormir": "sono", "sono": "sono", "descansar": "sono",
            "comer": "alimentação", "almoçar": "alimentação", "jantar": "alimentação", "café": "alimentação",
            "vitamina": "saúde", "remédio": "saúde", "medicamento": "saúde", "consultar": "saúde", "tomar": "saúde",
            "meditar": "bem-estar", "ler": "lazer", "estudar": "produtividade", "revisar": "produtividade"
        }

        self.palavras_validas = list(self.categorias_keywords.keys()) + list(self.verbos_ignore) + [
            "agenda", "remédio", "vitamina", "água", "beber", "tomar", "corrida", "musculação"
        ]
        self.palavras_validas += [
            "agua", "aguá", "remedio", "remédios", "academia", "musculacao", "corrida", "vitamina", "sono",
            "dormir", "comida", "cafe", "suco", "ler", "estudo", "meditacao", "caminhada"
        ]

        self.comandos_sociais = [
            "bom dia", "boa tarde", "boa noite", "olá", "oi", "e aí", "fala comigo",
            "tudo bem", "como vai", "tá aí?", "está aí?",
            "o que tenho hoje", "me avisa o que falta", "qual o próximo hábito", "próximo hábito",
            "tem algo agora", "hábitos de hoje"
        ]

        self.frases_vagas = [
            "coloca isso", "coloca aí", "isso aí", "adiciona aí", "adiciona isso",
            "bota qualquer coisa", "qualquer coisa", "alguma coisa", "algo aí", "a parada", "aquele negócio"
        ]

        self.habitos_existentes: List[str] = []

    # -------------------- HELPERS --------------------
    def _contains_any(self, text: str, keywords: List[str]) -> bool:
        t = text.lower()
        return any(k in t for k in keywords)

    def _extrair_id(self, texto: str) -> Optional[int]:
        m = self.regex_id.search(texto)
        if m:
            try:
                return int(m.group(1))
            except:
                return None
        # número solto, evitando padrões de horário
        m2 = re.search(r"\b(\d+)\b", texto)
        if m2 and not re.search(r"\d{1,2}[:h]\d{0,2}", texto):
            try:
                return int(m2.group(1))
            except:
                return None
        return None

    def _extrair_minutos_adiar(self, texto: str, default_minutos: int = 15) -> int:
        m = self.regex_minutos_adiar.search(texto)
        if m:
            try:
                val = int(m.group(1))
                return max(1, min(val, 1440))
            except:
                return default_minutos
        return default_minutos

    def configurar_habitos_existentes(self, habitos: List[str]):
        self.habitos_existentes = habitos

    def corrigir_palavra(self, palavra: str) -> str:
        candidatos = difflib.get_close_matches(palavra.lower(), self.palavras_validas, n=1, cutoff=0.7)
        return candidatos[0] if candidatos else palavra

    def corrigir_frase(self, texto: str) -> str:
        palavras = texto.split()
        frase_corrigida = []
        for palavra in palavras:
            if palavra.isdigit() or re.match(r"\d{1,2}[:h]\d{0,2}", palavra):
                frase_corrigida.append(palavra)
            elif len(palavra) > 12 and palavra.lower() not in self.palavras_validas:
                frase_corrigida.append(palavra)
            else:
                frase_corrigida.append(self.corrigir_palavra(palavra))
        return " ".join(frase_corrigida)

    def extrair_horario(self, texto: str) -> Optional[str]:
        texto = texto.lower()
        match = self.regex_horario.search(texto)
        if match:
            hora = match.group(1)
            minuto = match.group(2) if match.group(2) else "00"
            return f"{int(hora):02d}h{int(minuto):02d}"
        if "meio-dia" in texto:
            return "12h00"
        if "meia-noite" in texto:
            return "00h00"
        for hora_texto, valor in {
            "uma": 1, "duas": 2, "três": 3, "quatro": 4,
            "cinco": 5, "seis": 6, "sete": 7, "oito": 8,
            "nove": 9, "dez": 10, "onze": 11
        }.items():
            if f"{hora_texto} da manhã" in texto:
                return f"{valor:02d}h00"
            if f"{hora_texto} da tarde" in texto:
                return f"{valor+12:02d}h00"
        return None

    def sugerir_horario(self) -> str:
        hora_atual = datetime.now().hour
        if hora_atual < 10:
            return "10h00"
        elif hora_atual < 14:
            return "14h00"
        elif hora_atual < 18:
            return "18h00"
        else:
            return "20h00"

    def extrair_categoria(self, acao: str) -> str:
        for palavra, categoria in self.categorias_keywords.items():
            if palavra in acao.lower():
                return categoria
        return "geral"

    def dividir_em_acoes(self, texto: str) -> List[str]:
        return re.split(r"\be\b|,| e então | e depois ", texto)

    def verificar_habito_existente(self, nova_acao: str) -> bool:
        doc_novo = self.nlp(nova_acao.lower())
        for habito in self.habitos_existentes:
            doc_existente = self.nlp(habito.lower())
            if doc_novo.similarity(doc_existente) > 0.85:
                return True
        return False

    def extrair_acao(self, frase: str) -> str:
        doc = self.nlp(frase)
        tokens_filtrados = [
            token.text for token in doc
            if token.pos_ in ["VERB", "NOUN", "PROPN"]
            and token.lemma_.lower() not in self.verbos_ignore
            and not re.match(r"^\d{1,2}$", token.text)
            and not re.match(r"^\d{1,2}[:h]\d{0,2}$", token.text)
        ]
        if not tokens_filtrados:
            subs = [t.text for t in doc if t.pos_ in ["NOUN", "PROPN"]]
            acao_bruta = " ".join(subs).strip() if subs else doc[-1].text
        else:
            acao_bruta = " ".join(tokens_filtrados).strip()
        acao_corrigida = self.corrigir_frase(acao_bruta)
        acao_limpa = " ".join([p for p in acao_corrigida.split() if p.lower() != "agenda"])
        return acao_limpa

    # -------------------- ENTRYPOINT --------------------
    def processar(self, frase: str) -> List[Dict[str, Any]]:
        """
        Retorna uma lista de comandos estruturados.
        Casos especiais:
          - __social__: comandos sociais / próximos hábitos
          - __concluir__: intenção de marcar como concluído (pode conter habito_id)
          - __adiar__: intenção de adiar (pode conter habito_id e minutos)
        Caso contrário, retorna hábitos a cadastrar com {acao, horario, categoria}.
        """
        frase_original = frase or ""
        frase_lower = frase_original.lower().strip()
        frase_corrigida = self.corrigir_frase(frase_original)

        # 1) Comandos sociais
        if any(c in frase_lower for c in self.comandos_sociais):
            return [{"acao": "__social__", "horario": "", "categoria": frase_lower}]

        # 2) Frases vagas (não dá para entender)
        if any(v in frase_lower for v in self.frases_vagas):
            return [{"acao": "", "horario": "", "categoria": ""}]

        # 3) INTENT: CONCLUIR
        if self._contains_any(frase_lower, self.concluir_keywords):
            habito_id = self._extrair_id(frase_lower)
            return [{"acao": "__concluir__", "habito_id": habito_id}]

        # 4) INTENT: ADIAR (snooze) 
        if self._contains_any(frase_lower, self.adiar_keywords) or self.regex_lembre_depois.search(frase_lower):
            habito_id = self._extrair_id(frase_lower)  # pode ser None
            minutos = self._extrair_minutos_adiar(frase_lower, default_minutos=15)
            return [{"acao": "__adiar__", "habito_id": habito_id, "minutos": minutos}]

        # 5) Cadastro de novos hábitos (múltiplas ações)
        acoes_texto = self.dividir_em_acoes(frase_corrigida)
        resultados = []
        for acao_texto in acoes_texto:
            acao = self.extrair_acao(acao_texto)
            if not acao or any(p in acao for p in ["isso", "aí", "coisa", "algo"]):
                continue
            if self.verificar_habito_existente(acao):
                continue
            horario = self.extrair_horario(acao_texto) or self.sugerir_horario()
            categoria = self.extrair_categoria(acao)
            resultados.append({"acao": acao.lower(), "horario": horario, "categoria": categoria})

        return resultados