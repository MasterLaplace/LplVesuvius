# `inference/` — l'environnement CPU, gardé comme **témoin**

Ce dossier ne porte **aucun code**. Il porte un environnement, et c'est tout son rôle.

## Pourquoi il existe

C'est l'environnement dans lequel la détection d'encre a d'abord tourné, **sur CPU**.
Il est conservé parce que le passage à l'iGPU Intel Arc a été validé **contre lui** :
commit `ea1cde9`, *« iGPU Arc via WSL2, ×4,5 à sortie identique »*. Sans un
environnement CPU qui tourne encore, cette égalité ne serait plus rejouable — et une
accélération dont on ne peut plus vérifier qu'elle ne change pas le résultat n'est pas
une accélération, c'est un changement de méthode non mesuré.

## ⚠ Le code vit **une seule fois**, et pas ici

`inference_xpu/src/infer_ink.py` prend `--device {cpu,xpu}` et **défaute à `cpu`**. Le
même fichier sert donc les deux chemins.

Jusqu'au 2026-08-19 ce dossier portait une **copie octet pour octet** de ce script.
Deux copies d'un même script sont deux occasions de diverger, et celle-ci n'avait même
pas de raison d'être : le script gérait déjà les deux appareils. La copie est
supprimée.

## ⚠ Le venv n'est plus gardé chaud (2026-08-25)

Ce dossier a longtemps été **emprunté** par 25 sites d'appel — figures, mosaïque, batteries —
au motif écrit partout que c'était *le seul environnement porteur de Pillow*. C'était **faux** :
la racine déclare `pillow>=10.0`. Et c'était **nuisible**, parce qu'`inference/` n'a pas
`numcodecs` : c'est exactement ce trou qui a fait rendre vides tous les chunks *blosc* d'une
prédiction, et conclure — en le mesurant, en l'écrivant — qu'une graine n'était pas couverte
(cf. la docstring de `analysis/src/zarr_depth.py`). Une panne d'installation avait pris la
forme d'un fait sur le rouleau.

Les 25 emprunts sont repointés sur la **racine**, qui porte PIL, numcodecs, numpy, scipy et
tifffile — strictement plus. Le `.venv` d'ici est supprimé : garder chaud 4 Gio de paquets pour
un rôle de témoin qu'on exerce deux fois par an ne se justifie pas.

⭐ **Le rôle, lui, ne change pas.** `pyproject.toml` et `uv.lock` restent versionnés, donc le
témoin est **rejouable à la commande près** — c'est ce qui compte, pas la présence du venv sur
le disque. Un `uv sync` le reconstruit.

⚠ Ce que la suppression libère vraiment : **0,08 Gio tout de suite**, et 4,09 Gio de plus
seulement après un `uv cache prune`, parce qu'`uv` installe en **liens durs** vers son cache.
Mesuré par `analysis/src/poids_recuperable.py`, pas estimé par `du`, qui se trompe ici d'un
facteur quatre.

## Lancer le chemin CPU

```bash
cd inference
uv sync
uv run python ../inference_xpu/src/infer_ink.py --device cpu ...
```

Ce qui diffère entre les deux dossiers est **uniquement** le `pyproject.toml` :
ici `torch` générique + OpenVINO/ONNX ; là-bas `torch==2.9.1+xpu` depuis l'index
PyTorch XPU. C'est la seule chose qu'un environnement a le droit de porter.
