ARG BW_VERSION=v2025.12.0
ARG SOPS_VERSION=v3.11.0

FROM node:22-bookworm AS build_bw

ARG TARGETARCH
ARG BW_VERSION

WORKDIR /usr/src/bw

RUN git clone --depth 1 --branch "cli-${BW_VERSION}" https://github.com/bitwarden/clients.git \
    && cd clients \
    && npm ci \
    && cd apps/cli \
    && npm run "dist:oss:lin-${TARGETARCH}" ; 
FROM python:3.12

ARG TARGETARCH
ARG SOPS_VERSION

RUN curl -LO "https://github.com/getsops/sops/releases/download/${SOPS_VERSION}/sops-${SOPS_VERSION}.linux.${TARGETARCH}"
RUN mv "sops-${SOPS_VERSION}.linux.${TARGETARCH}" /usr/local/bin/sops
RUN chmod +x /usr/local/bin/sops

# Install pipx
RUN pip install pipx && pipx ensurepath

# Install vdirsyncer using pipx
RUN pipx install vdirsyncer

# Install bitwarden cli using the prebuilt binary
COPY --from=build_bw /usr/src/bw/clients/apps/cli/dist/oss/linux-${TARGETARCH}/bw /usr/local/bin/bw

WORKDIR /usr/src/app

COPY ./src .

RUN pip install -r requirements.txt

CMD tail -f /dev/null