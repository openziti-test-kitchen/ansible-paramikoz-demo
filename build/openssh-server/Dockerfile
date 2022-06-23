ARG UBUNTU_VERSION=latest
ARG SSHD_USER=ziggy

FROM ubuntu:$UBUNTU_VERSION
ARG SSHD_USER

EXPOSE 22

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get -qq install \
        openssh-server \
    && rm -rf rm -rf /var/lib/apt/lists/* \
    && mkdir -p /run/sshd 

RUN adduser --disabled-password --gecos '' ${SSHD_USER} \
    && echo "%${SSHD_USER} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers \
    && install -d -m 0700 -o ${SSHD_USER} -g ${SSHD_USER} /home/${SSHD_USER}/.ssh

COPY --chmod=600 --chown=${SSHD_USER}:${SSHD_USER} secrets/ssh/ziggy_id_rsa.pub /home/${SSHD_USER}/.ssh/authorized_keys
COPY --chmod=600 --chown=${SSHD_USER}:${SSHD_USER} secrets/ssh/ziggy_id_rsa /home/${SSHD_USER}/.ssh/id_rsa

CMD ["/usr/sbin/sshd", "-D", "-e", "-o", "ListenAddress=0.0.0.0", "-o", "PasswordAuthentication=no"]
