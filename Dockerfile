FROM python:3.9.11-alpine as prod

    RUN adduser -D wikicrawl
    USER wikicrawl
    WORKDIR /home/wikicrawl

    ENV PATH="/home/wikicrawl/.local/bin:${PATH}"
    RUN python -m pip --disable-pip-version-check install --upgrade pip 

    RUN mkdir -p /tmp/wikicrawl
    COPY --chown=wikicrawl:wikicrawl ./.build/wikicrawl_*-0.1.0-py3-none-any.whl /tmp/wikicrawl/

    RUN pip install --user \
        /tmp/wikicrawl/wikicrawl_core-0.1.0-py3-none-any.whl \
        /tmp/wikicrawl/wikicrawl_crawl-0.1.0-py3-none-any.whl \
        /tmp/wikicrawl/wikicrawl_database-0.1.0-py3-none-any.whl \
        /tmp/wikicrawl/wikicrawl_workers-0.1.0-py3-none-any.whl

FROM prod as dockercompose

    COPY --chown=wikicrawl:wikicrawl ./scripts/startup /home/wikicrawl/startup
    ADD --chown=wikicrawl:wikicrawl https://github.com/ufoscout/docker-compose-wait/releases/download/2.9.0/wait /home/wikicrawl/wait
    RUN chmod +x /home/wikicrawl/wait /home/wikicrawl/startup

    RUN rm -rf /tmp/wikicrawl
