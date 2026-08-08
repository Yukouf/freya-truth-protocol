# ⚖️ Freya Truth Protocol

**3 agents IA qui débattent pour trouver la vérité.**

Tu donnes une affirmation. Trois agents IA débattent :

| Agent | Rôle |
|---|---|
| 🟢 **Defender** | Défend l'affirmation avec des preuves |
| 🔴 **Challenger** | La contredit, trouve les failles |
| ⚖️ **Judge** | Tranche : VRAI / FAUX / INCERTAIN + score de confiance |

## Pourquoi ?

Les LLMs sont entraînés pour être **fluides**, pas **vrais**. Un seul modèle peut affirmer n'importe quoi avec aplomb.

En faisant débattre 3 agents indépendants, on réduit les hallucinations et on obtient un verdict nuancé — pas juste du binaire.

## Installation

```bash
git clone https://github.com/Yukouf/freya-truth-protocol.git
cd freya-truth-protocol
```

## Utilisation

```bash
# Avec DeepSeek (par défaut)
export DEEPSEEK_API_KEY=sk-...
python3 truth-debate.py "L'IA va remplacer les développeurs d'ici 2030"

# Avec OpenAI
export OPENAI_API_KEY=sk-...
export TRUTH_API_URL=https://api.openai.com/v1
export TRUTH_MODEL=gpt-4o
python3 truth-debate.py "Le réchauffement est causé par l'homme"

# Avec Ollama (local)
export TRUTH_API_URL=http://localhost:11434/v1
export TRUTH_MODEL=qwen2.5
export OPENAI_API_KEY=ollama  # Ollama ignore la clé mais le format l'exige
python3 truth-debate.py "Bitcoin dépassera 200k$ en 2025"
```

## Exemple de sortie

```
══════════════════════════════════════════════════════
🎯 AFFIRMATION : L'IA va remplacer les développeurs d'ici 2030
══════════════════════════════════════════════════════

🟢 DEFENDER — Je défends...
Arguments : automatisation massive, scalabilité, no-code...
Score : 8/10

🔴 CHALLENGER — Je contredis...
Failles : confusion assistance/remplacement, legacy code, responsabilité...
Score de contradiction : 7/10

⚖️  JUDGE — Je tranche...
Verdict : INCERTAIN (confiance 7/10)
Les devs CRUD sont menacés, les devs systèmes complexes non.
```

## Compatible avec

- **DeepSeek** (par défaut, pas cher)
- **OpenAI** (GPT-4o, GPT-4)
- **Ollama** (local, gratuit)
- **Groq, Together, Fireworks** — tout ce qui parle OpenAI API

## Structure

```
freya-truth-protocol/
├── truth-debate.py    # Le script principal
├── README.md          # Ce fichier
└── .gitignore
```

## Licence

MIT — fais-en ce que tu veux.
