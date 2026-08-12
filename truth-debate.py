#!/usr/bin/env python3
"""
⚖️ Freya Truth Protocol — Débat multi-agent

3 agents IA débattent d'une affirmation :
  🟢 Defender  → défend avec des preuves
  🔴 Challenger → contredit, trouve les failles
  ⚖️ Judge     → tranche avec un verdict + score de confiance

Utilisation :
  export DEEPSEEK_API_KEY="sk-..."
  python3 truth-debate.py "Le réchauffement climatique est causé par l'homme"

Fonctionne avec n'importe quel fournisseur compatible OpenAI API :
  - DeepSeek (par défaut)
  - OpenAI
  - Ollama local
  - Groq, Together, etc.

COMPORTEMENT "ÉCHEC FERMÉ" :
Ce protocole ne prétend JAMAIS établir la vérité. Si l'un des agents API ne
répond pas (clé absente, erreur réseau, quota, code non-2xx…), le débat ne
peut pas se poursuivre honnêtement : on s'arrête immédiatement et le script
sort avec un code de retour NON NUL, sans afficher de synthèse ni de verdict.
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error


# ── Configuration ──────────────────────────────────────────
API_KEY = os.environ.get("DEEPSEEK_API_KEY", os.environ.get("OPENAI_API_KEY", ""))
BASE_URL = os.environ.get("TRUTH_API_URL", "https://api.deepseek.com/v1")
MODEL = os.environ.get("TRUTH_MODEL", "deepseek-chat")


class AgentAPIError(RuntimeError):
    """Levée quand un agent n'a pas pu produire de réponse après les retries."""


# ── Appel API ──────────────────────────────────────────────
def ask(agent_name, system_prompt, user_message, temperature=0.7):
    """
    Interroge un modèle. Lève AgentAPIError si le fournisseur ne répond pas
    après MAX_ATTEMPTS tentatives. N'utilise pas la clé si elle est vide.
    """
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": temperature,
        "max_tokens": 800,
    }
    data = json.dumps(payload).encode("utf-8")
    url = f"{BASE_URL}/chat/completions"
    req = urllib.request.Request(url, data=data)
    headers = {}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    req.headers.update(headers)
    req.add_header("Content-Type", "application/json")

    max_attempts = 3
    last_err = None
    for attempt in range(max_attempts):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = json.loads(resp.read())
                content = body["choices"][0]["message"]["content"].strip()
                if not content:
                    raise ValueError("réponse vide du modèle")
                return content
        except Exception as e:  # réseau, HTTP, JSON, réponse vide…
            last_err = e
            if attempt == max_attempts - 1:
                break
            time.sleep(2)

    raise AgentAPIError(
        f"l'agent {agent_name!r} n'a pas répondu après {max_attempts} tentatives "
        f"({MODEL} @ {BASE_URL}) : {last_err}"
    )


# ── Débat ──────────────────────────────────────────────────
def debate(claim):
    """Lance le débat. Lève AgentAPIError dès qu'un agent échoue."""
    print(f"\n{'═' * 60}")
    print(f"🎯 AFFIRMATION : {claim}")
    print(f"{'═' * 60}\n")

    # 🟢 DEFENDER
    print("🟢 DEFENDER — Je défends...")
    defender = ask("defender",
        """Tu es le DEFENDER. Défends l'affirmation de l'utilisateur.
Structure ta réponse :
1. Arguments principaux (2-3)
2. Preuves ou faits connus
3. Score de confiance /10""",
        claim)
    print(defender)
    print(f"\n{'─' * 60}\n")

    # 🔴 CHALLENGER
    print("🔴 CHALLENGER — Je contredis...")
    challenger = ask("challenger",
        """Tu es le CHALLENGER. Contredis l'affirmation.
Trouve les failles, contre-exemples et angles morts.
Structure ta réponse :
1. Failles principales (2-3)
2. Contre-exemples ou nuances
3. Score de contradiction /10""",
        f"AFFIRMATION : {claim}\n\nARGUMENTS DU DEFENDER :\n{defender}",
        temperature=0.6)
    print(challenger)
    print(f"\n{'─' * 60}\n")

    # ⚖️ JUDGE
    print("⚖️  JUDGE — Je tranche...")
    verdict = ask("judge",
        """Tu es le JUDGE. Tranche de façon impartiale.
Donne :
1. Verdict (VRAI / FAUX / INCERTAIN)
2. Score de confiance /10
3. Raisonnement
4. Nuances importantes""",
        f"AFFIRMATION : {claim}\n\nDEFENDER :\n{defender}\n\nCHALLENGER :\n{challenger}",
        temperature=0.3)
    print(verdict)

    # ── Synthèse ──
    print(f"\n{'═' * 60}")
    print("📋 SYNTHÈSE")
    print(f"{'═' * 60}")
    print(f"Affirmation : {claim}\n")
    print(verdict)
    print(f"\n{'═' * 60}")
    print("⚠️  Note : ce débat reflète les réponses des modèles et n'établit")
    print("    pas une vérité objective. Son verdict est une synthèse d'opinions.")

    return {"claim": claim, "defense": defender, "challenge": challenger, "verdict": verdict}


# ── CLI ────────────────────────────────────────────────────
def main(argv=None):
    argv = list(sys.argv if argv is None else argv)
    if len(argv) < 2:
        print("Usage: python3 truth-debate.py \"Ton affirmation\"")
        return 1

    if not API_KEY:
        print("❌ Définis DEEPSEEK_API_KEY ou OPENAI_API_KEY")
        return 1

    claim = " ".join(argv[1:])
    try:
        debate(claim)
    except AgentAPIError as e:
        print(f"\n❌ ÉCHEC FERMÉ — {e}")
        print("   Le débat s'arrête ici : un agent n'a pas répondu. Aucun verdict ne")
        print("   peut être établi de façon fiable. Vérifie clé API / réseau / quota.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
