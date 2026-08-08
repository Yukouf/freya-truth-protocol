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

if not API_KEY:
    print("❌ Définis DEEPSEEK_API_KEY ou OPENAI_API_KEY")
    sys.exit(1)

# ── Appel API ──────────────────────────────────────────────
def ask(agent_name, system_prompt, user_message, temperature=0.7):
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
    req.add_header("Authorization", f"Bearer {API_KEY}")
    req.add_header("Content-Type", "application/json")

    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = json.loads(resp.read())
                return body["choices"][0]["message"]["content"].strip()
        except Exception as e:
            if attempt == 2:
                return f"[ERREUR {agent_name}: {e}]"
            time.sleep(2)

# ── Débat ──────────────────────────────────────────────────
def debate(claim):
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
        f"""Tu es le CHALLENGER. Contredis l'affirmation.
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

    return {"claim": claim, "defense": defender, "challenge": challenger, "verdict": verdict}

# ── CLI ────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 truth-debate.py \"Ton affirmation\"")
        sys.exit(1)
    debate(" ".join(sys.argv[1:]))
