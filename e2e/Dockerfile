FROM mcr.microsoft.com/playwright:v1.59.1

RUN --mount=type=cache,target=/root/.npm \
    npm update -g npm && \
    npm install -g pnpm

WORKDIR /app

RUN mkdir -p /app/test-results && chown pwuser:pwuser /app/test-results

RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    --mount=type=bind,source=package.json,target=package.json \
    --mount=type=bind,source=pnpm-lock.yaml,target=pnpm-lock.yaml \
    pnpm install --frozen-lockfile

COPY --chown=pwuser:pwuser . .

USER pwuser

CMD ["sleep", "infinity" ]
