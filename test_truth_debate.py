#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests de régression pour truth-debate.py — échec fermé (fail-closed).

Aucun test n'effectue d'appel réseau réel : `urllib.request.urlopen` est
systématiquement remplacé par un faux qui simule succès ou échec.
"""

import importlib.util
import io
import os
import sys
import unittest.suite
import unittest
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(HERE, "truth-debate.py")


def _load():
    spec = importlib.util.spec_from_file_location("truth_debate", MOD)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


truth = _load()


class FakeResponse:
    def __init__(self, body):
        self._body = body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self):
        return self._body


def _ok_response(content="Verdict : INCERTAIN"):
    import json
    payload = {"choices": [{"message": {"content": content}}]}
    return FakeResponse(json.dumps(payload).encode("utf-8"))


class TestFailClosed(unittest.TestCase):
    def setUp(self):
        # Sans clé, aucun appel réseau ne doit être tenté.
        self._old_key = os.environ.get("DEEPSEEK_API_KEY")
        self._old_key2 = os.environ.get("OPENAI_API_KEY")
        os.environ.pop("DEEPSEEK_API_KEY", None)
        os.environ.pop("OPENAI_API_KEY", None)
        self._old_urlopen = truth.urllib.request.urlopen
        self.calls = []
        truth.API_KEY = "test-cle"  # simule une clé présente

    def tearDown(self):
        truth.urllib.request.urlopen = self._old_urlopen
        truth.API_KEY = ""
        if self._old_key:
            os.environ["DEEPSEEK_API_KEY"] = self._old_key
        if self._old_key2:
            os.environ["OPENAI_API_KEY"] = self._old_key2

    def _simulate(self, factory):
        """Remplace urlopen par `factory(attempt)` pour simuler le réseau."""
        def fake_urlopen(req, **kw):
            self.calls.append(req.full_url)
            return factory(len(self.calls))
        truth.urllib.request.urlopen = fake_urlopen

    def test_no_api_key_means_failure_without_network(self):
        """Sans clé, aucun réseau : main() sort non-nul sans appeler urlopen."""
        truth.API_KEY = ""
        truth.urllib.request.urlopen = lambda req, **kw: (_ for _ in ()).throw(
            AssertionError("aucun appel réseau attendu sans clé"))
        with redirect_stdout(io.StringIO()) as out:
            code = truth.main(["truth-debate.py", "affirmation"])
        self.assertNotEqual(code, 0)
        self.assertIn("DEEPSEEK_API_KEY", out.getvalue())

    def test_defender_failure_raises_and_main_is_nonzero(self):
        """Si le 1er agent (defender) échoue toujours → échec fermé, code non nul."""
        def always_fail(attempt):
            raise OSError("connexion refusée (simulé)")
        self._simulate(always_fail)
        with redirect_stdout(io.StringIO()):
            code = truth.main(["truth-debate.py", "affirmation"])
        self.assertNotEqual(code, 0, "échec agent doit produire un code de retour non nul")
        self.assertGreaterEqual(len(self.calls), 1)
        # Aucun appel réseau réel n'a été fait.
        for url in self.calls:
            self.assertTrue(url.startswith("https://api.deepseek.com"), url)

    def test_second_agent_failure_fails_closed(self):
        """defender OK mais challenger échoue → le débat s'arrête, code non nul,
        et AUCUN verdict n'est produit ni affiché."""
        outcomes = iter([_ok_response("Arguments : ... Score 8/10")])
        def seq(attempt):
            if len(self.calls) <= 1:
                return _ok_response("Arguments : ... Score 8/10")
            raise OSError("quota dépassé (simulé)")
        self._simulate(seq)
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = truth.main(["truth-debate.py", "affirmation"])
        out = buf.getvalue()
        self.assertNotEqual(code, 0)
        # Echec fermé : pas de synthèse ni de verdict triomphant.
        self.assertIn("ÉCHEC FERMÉ", out)
        self.assertNotIn("TROUVÉ", out)
        self.assertNotIn("Verdict final", out)

    def test_failed_agent_does_not_pretend_truth(self):
        """debate() lève une AgentAPIError en cas d'échec → jamais de dict 'verdict'."""
        def always_fail(attempt):
            raise TimeoutError("timeout (simulé)")
        self._simulate(always_fail)
        with self.assertRaises(truth.AgentAPIError), redirect_stdout(io.StringIO()):
            truth.debate("affirmation")

    def test_all_success_produces_verdict(self):
        """Chemin nominal : tous les agents répondent → verdict rendu, code 0."""
        def always_ok(attempt):
            return _ok_response("Verdict : INCERTAIN")
        self._simulate(always_ok)
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = truth.main(["truth-debate.py", "affirmation"])
        self.assertEqual(code, 0)
        self.assertIn("📋 SYNTHÈSE", buf.getvalue())
        self.assertIn("Verdict : INCERTAIN", buf.getvalue())


class TestNoSecretInSource(unittest.TestCase):
    def test_no_hardcoded_secret(self):
        """Aucune vraie clé API (≥20 caractères) en dur dans le script."""
        import re
        with open(MOD, encoding="utf-8") as fh:
            src = fh.read()
        # 'sk-...' est un placeholder de doc ; une vraie clé a beaucoup plus de caractères.
        self.assertIsNone(re.search(r"sk-[A-Za-z0-9]{20,}", src))
        self.assertNotIn("API_KEY = \"sk-", src)


if __name__ == "__main__":
    unittest.main(verbosity=2)
