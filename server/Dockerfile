FROM python:3.9.7-slim
COPY server /
RUN mkdir -p /shared-volume/locks
RUN python -m unittest tests/test_common.py
ENTRYPOINT ["/bin/sh"]
