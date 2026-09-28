# The image of the prize software: the C core built and tested in a first stage, and only the wheel installed in the
# final image.
#
#   docker build -t vesuve .                               (--build-arg INK=1 for torch and the ink model)
#   docker run --rm --user "$(id -u):$(id -g)" -v "$PWD/outputs:/outputs" vesuve
#                                                          the demo: Grand Prize and Progress
#   docker run --rm --user "$(id -u):$(id -g)" -v "$PWD/outputs:/outputs" -v <data/ of the experimental branch>:/data:ro \
#       vesuve demo --output /outputs --data /data         the four prizes
#
# ⚠ `--user`: without it, the outputs written into the mounted folder belong to root.
#
#   docker build --target render -t vesuve:render .      the same program on top of ScrollPrize/villa's image, which
#                                                          carries vc_render_tifxyz: what `grand-prize --render` needs
#
# ⚠ Requirements: x86-64 or arm64, 2 GiB of memory, no GPU. The network is only asked for to read the public bucket
# (--read, the ink map, the certified surface); without it, each remote stage says so and the pipeline goes as far as
# it can.

FROM python:3.13-slim AS build
RUN apt-get update && apt-get install -y --no-install-recommends gcc make libc6-dev \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /vesuve
COPY . .
# The core first, and its tests under sanitizers: an image whose core fails does not build.
RUN make test && make && pip wheel --no-cache-dir --no-deps -w /wheels .

# The renderer is the community's, as it ships: the program is installed on top of its image rather than the
# renderer rebuilt here. Its own entry point is replaced by the program's.
FROM ghcr.io/scrollprize/villa/volume-cartographer:edge AS render
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-venv \
    && rm -rf /var/lib/apt/lists/*
COPY --from=build /wheels /wheels
RUN python3 -m venv /opt/vesuve && /opt/vesuve/bin/pip install --no-cache-dir /wheels/*.whl && rm -rf /wheels
ENV PATH=/opt/vesuve/bin:$PATH
WORKDIR /work
ENTRYPOINT ["vesuve"]
CMD ["grand-prize", "--render", "--output", "/outputs", "--cache", "/cache"]

FROM python:3.13-slim
ARG INK=0
COPY --from=build /wheels /wheels
RUN pip install --no-cache-dir /wheels/*.whl && rm -rf /wheels \
    && if [ "$INK" = "1" ]; then pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch \
       && pip install --no-cache-dir "transformers>=4.46,<5" "timesformer-pytorch>=0.4"; fi
WORKDIR /work
ENTRYPOINT ["vesuve"]
CMD ["demo", "--output", "/outputs", "--cache", "/tmp/cache"]
