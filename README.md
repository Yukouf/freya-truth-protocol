# ⚖️ Freya Truth Protocol

**Trois rôles IA confrontent une affirmation pour produire un verdict argumenté.**

Tu donnes une affirmation. Trois agents IA débattent :

| Agent | Rôle |
|---|---|
| 🟢 **Defender** | Défend l'affirmation avec des preuves |
| 🔴 **Challenger** | La contredit, trouve les failles |
| ⚖️ **Judge** | Tranche : VRAI / FAUX / INCERTAIN + score de confiance |

![Architecture](https://raw.githubusercontent.com/Yukouf/freya-truth-protocol/main/truth-diagram.svg)

## Pourquoi ?

Les LLMs sont entraînés pour être **fluides**, pas **vrais**. Un seul modèle peut affirmer n'importe quoi avec aplomb.

Le protocole fait intervenir trois rôles successifs d'un même modèle : défense,
contradiction et synthèse. Cette confrontation peut faire émerger des objections,
mais elle **ne vérifie pas les sources et n'établit pas une vérité objective**.

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

## Échec fermé (fail-closed)

Ce protocole ne prétend **jamais** établir la vérité. Si l'un des agents ne
répond pas (clé absente, erreur réseau, quota, code non-2xx, réponse vide…),
le débat s'arrête immédiatement et le script sort avec un **code de retour
non nul**, **sans** afficher de synthèse ni de verdict. Aucune clé n'est
utilisée si elle est absente, et aucun appel réseau n'est tenté sans clé.

```bash
# Sans DEEPSEEK_API_KEY / OPENAI_API_KEY
python3 truth-debate.py "L'IA va remplacer les développeurs d'ici 2030"
# → ❌ Définis DEEPSEEK_API_KEY ou OPENAI_API_KEY   (code de retour : 1)
```

## Tests

Les tests (`python3 test_truth_debate.py`) vérifient l'échec fermé **sans
aucun appel réseau réel** : `urllib.request.urlopen` est remplacé par un faux
qui simule succès ou échec.

```bash
python3 test_truth_debate.py
```

Cas couverts : pas de clé (`main` non nul, zéro appel réseau), échec du 1er
agent, échec d'un agent + pas de verdict, `debate()` qui lève `AgentAPIError`
(→ jamais de dict « verdict » terni), chemin nominal → verdict et code 0, et
absence de clé secrète en dur dans le source.

## Compatible avec

- **DeepSeek** (par défaut, pas cher)
- **OpenAI** (GPT-4o, GPT-4)
- **Ollama** (local, gratuit)
- **Groq, Together, Fireworks** — tout ce qui parle OpenAI API

## Structure

```
freya-truth-protocol/
├── truth-debate.py       # Le script principal
├── truth-diagram.svg     # Architecture actuelle
├── RESEARCH_ROADMAP.md   # Audit et feuille de route
├── README.md             # Ce fichier
└── .gitignore
```

## Licence

MIT — fais-en ce que tu veux.
