"""Le journal : structuré, corrélé, filtré par niveau, et jamais sur la sortie standard."""
import io

import pytest

from vesuve.journal import Journal


def test_une_ligne_porte_son_code_son_run_et_ses_champs():
    f = io.StringIO()
    Journal(f, "INFO", run="ab12").warn("CHUNK_REFUSE", cy=99, cx=71, raison="absent du dépôt")
    assert f.getvalue() == "WARN  CHUNK_REFUSE run=ab12 cy=99 cx=71 raison='absent du dépôt'\n"


def test_le_niveau_filtre_sans_rien_reconstruire(monkeypatch):
    f = io.StringIO()
    monkeypatch.setenv("VESUVE_JOURNAL", "WARN")
    j = Journal(f)
    j.info("BAVARD")
    j.error("GRAVE", quoi="x")
    assert "BAVARD" not in f.getvalue() and "GRAVE" in f.getvalue()


def test_un_niveau_inconnu_est_refuse_par_son_nom():
    with pytest.raises(ValueError, match="BAVARD"):
        Journal(io.StringIO(), "BAVARD")


def test_rien_ne_va_sur_la_sortie_standard(capsys):
    Journal(niveau="DEBUG").info("TRACE_VISIBLE", n=1)
    sortie = capsys.readouterr()
    assert sortie.out == "" and "TRACE_VISIBLE" in sortie.err
