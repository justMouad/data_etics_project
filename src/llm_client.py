import os
import re
import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
_client = None
_dernier_appel = 0.0


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        cle = os.getenv("LLM_API_KEY")
        if not cle:
            raise RuntimeError("LLM_API_KEY est absente de .env")
        base_url = (os.getenv("BASE_URL") or "").strip() or None
        _client = OpenAI(api_key=cle, base_url=base_url)
    return _client


def _attendre_intervalle():
    """Espace les appels pour rester sous la limite de requêtes par minute."""
    global _dernier_appel
    intervalle = float(os.getenv("MIN_INTERVAL") or 13)  # 5 requêtes/min -> 12 s minimum
    ecoule = time.monotonic() - _dernier_appel
    if ecoule < intervalle:
        time.sleep(intervalle - ecoule)
    _dernier_appel = time.monotonic()


def _delai_conseille(erreur: Exception, tentative: int) -> float:
    """Lit le délai demandé par le serveur ; sinon utilise une attente croissante."""
    message = str(erreur)
    m = re.search(r"retry in ([\d.]+)s", message) or re.search(r"retryDelay'?\"?: '?(\d+)s", message)
    if m:
        return float(m.group(1)) + 2
    if "503" in message or "UNAVAILABLE" in message:
        return 10 * tentative
    return 5 * tentative


def appeler_llm(systeme: str, utilisateur: str, modele: str | None = None,
                temperature: float | None = None, essais: int = 5) -> str:
    """Appelle le LLM et renvoie la réponse brute (JSON demandé)."""
    modele = modele or os.getenv("LLM_MODEL", "gpt-4o-mini")
    if temperature is None:
        temperature = float(os.getenv("TEMPERATURE") or 0)

    for n in range(1, essais + 1):
        _attendre_intervalle()
        try:
            reponse = _get_client().chat.completions.create(
                model=modele,
                temperature=temperature,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": systeme},
                    {"role": "user", "content": utilisateur},
                ],
            )
            return reponse.choices[0].message.content
        except Exception as e:
            if n == essais:
                raise
            pause = _delai_conseille(e, n)
            code = "429 (quota)" if "429" in str(e) else "503 (surcharge)" if "503" in str(e) else "erreur"
            print(f"   appel LLM échoué : {code}. Pause de {pause:.0f}s, essai {n + 1}/{essais}...")
            time.sleep(pause)