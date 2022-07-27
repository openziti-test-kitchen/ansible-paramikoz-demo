ARG PYTHON_VERSION=latest
ARG SSHD_USER=ziggy
ARG DOCKER_BUILD_DIR=.
FROM python:$PYTHON_VERSION AS server
ARG SSHD_USER
ARG DOCKER_BUILD_DIR

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
  sudo \
  && rm -rf /var/lib/apt/lists/*

RUN adduser --disabled-password --gecos '' ${SSHD_USER} \ 
&& echo "%${SSHD_USER} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers \
&& install -d -m 0700 -o ${SSHD_USER} -g ${SSHD_USER} /home/${SSHD_USER}/.ssh

USER $SSHD_USER

ENV PATH="/home/${SSHD_USER}/.local/bin:${PATH}"
RUN python -m pip install --no-cache-dir --upgrade --user pip

COPY ${DOCKER_BUILD_DIR}/requirements.txt .
RUN python -m pip install --no-cache-dir --user -r requirements.txt

COPY ${DOCKER_BUILD_DIR}/src/ .

COPY secrets/ssh/ziggy_id_rsa.pub /home/${SSHD_USER}/.ssh/authorized_keys
COPY secrets/ssh/ziggy_id_rsa /home/${SSHD_USER}/.ssh/id_rsa
COPY secrets/sshd/host_key_file.key .
COPY secrets/identities/ssh_server_2.json .

USER root

RUN chmod 600 /home/${SSHD_USER}/.ssh/authorized_keys \
    && chown ${SSHD_USER}:${SSHD_USER} /home/${SSHD_USER}/.ssh/authorized_keys \
    && chmod 600 /home/${SSHD_USER}/.ssh/id_rsa \
    && chown ${SSHD_USER}:${SSHD_USER} /home/${SSHD_USER}/.ssh/id_rsa \
    && chmod 600 ./host_key_file.key \
    && chown ${SSHD_USER}:${SSHD_USER} ./host_key_file.key \
    && chmod 600 ./ssh_server_2.json \
    && chown ${SSHD_USER}:${SSHD_USER} ./ssh_server_2.json

USER $SSHD_USER

CMD ["/bin/bash", "-c", "exec python paramikoz_sshd.py -k ${SSHD_HOST_KEY_FILE} -l ${SSHD_LOG_LEVEL} -i ${ZITI_IDENTITY_FILE} -s \"${ZITI_SDK_SERVICE}\""]
