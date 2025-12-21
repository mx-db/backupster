FROM node:22-bookworm AS build_bw

WORKDIR /usr/src/bw

RUN git clone --depth 1 --branch cli-v2025.10.0 https://github.com/bitwarden/clients.git \
    && cd clients \
    && npm ci \
    && cd apps/cli \
    && npm run "dist:oss:lin-arm64"


FROM python:3.12

RUN curl -LO https://github.com/getsops/sops/releases/download/v3.11.0/sops-v3.11.0.linux.arm64
RUN mv sops-v3.11.0.linux.arm64 /usr/local/bin/sops
RUN chmod +x /usr/local/bin/sops

# Install pipx
RUN pip install pipx && pipx ensurepath

# Install vdirsyncer using pipx
RUN pipx install vdirsyncer

# Install bitwarden cli using the prebuilt binary
COPY --from=build_bw  /usr/src/bw/clients/apps/cli/dist/oss/linux-arm64/bw /usr/local/bin/bw

WORKDIR /usr/src/app

COPY ./src .

RUN pip install -r requirements.txt

CMD tail -f /dev/null