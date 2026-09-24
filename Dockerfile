# L'image du logiciel des prix : le noyau C compilé et testé dans un premier étage, et seulement la roue
# installée dans l'image finale.
#
#   docker build -t vesuve vesuve/                        (--build-arg ENCRE=1 pour torch et le modèle d'encre)
#   docker run --rm --user "$(id -u):$(id -g)" -v "$PWD/sorties:/sorties" vesuve
#                                                         la démo : Grand Prize et Progress
#   docker run --rm --user "$(id -u):$(id -g)" -v "$PWD/sorties:/sorties" -v <data/ de LplVesuvius>:/donnees:ro \
#       vesuve demo --sortie /sorties --donnees /donnees  les quatre prix
#
# ⚠ `--user` : sans lui, les sorties écrites dans le dossier monté appartiennent à root.
#
# ⚠ Configuration requise : x86-64 ou arm64, 2 Gio de mémoire, aucun GPU. Le réseau n'est demandé que pour lire
# le bucket public (--lire, la carte d'encre, la surface certifiée) ; sans lui, chaque étage distant le dit et le
# pipeline va au bout de ce qu'il sait faire.

FROM python:3.13-slim AS construire
RUN apt-get update && apt-get install -y --no-install-recommends gcc make libc6-dev \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /vesuve
COPY . .
# Le noyau d'abord, et ses tests sous sanitizers : une image dont le noyau échoue ne se construit pas.
RUN make test && make && pip wheel --no-cache-dir --no-deps -w /roues .

FROM python:3.13-slim
ARG ENCRE=0
COPY --from=construire /roues /roues
RUN pip install --no-cache-dir /roues/*.whl && rm -rf /roues \
    && if [ "$ENCRE" = "1" ]; then pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch \
       && pip install --no-cache-dir "transformers>=4.46,<5" "timesformer-pytorch>=0.4"; fi
WORKDIR /travail
ENTRYPOINT ["vesuve"]
CMD ["demo", "--sortie", "/sorties", "--cache", "/tmp/cache"]
