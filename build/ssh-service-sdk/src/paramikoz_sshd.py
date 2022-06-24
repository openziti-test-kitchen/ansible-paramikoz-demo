#!/usr/bin/env python
"""TODO"""
import argparse
import logging
import socket
import sys
import threading
import traceback
import time

import paramiko

import impls
from utils import SSHD_KEYFILE, coloredlogs_install, ensure_private_key_file

from openziti.context import ZitiContext
from openziti.zitisock import ZitiSocket

# pylint: disable=broad-except


class ConnectionHandler(threading.Thread):
    """TODO"""
    def __init__(self, conn, host_key):
        super().__init__(daemon=True)
        self._conn = conn
        self._host_key = host_key

    def run(self):
        try:
            transport = paramiko.Transport(self._conn)
            transport.add_server_key(self._host_key)
            transport.set_subsystem_handler(
                'sftp', paramiko.SFTPServer, impls.SFTPServer
            )

            server = impls.Server()
            try:
                transport.start_server(server=server)
            except paramiko.SSHException:
                logger.fatal("Error starting transport server")
                raise
            channel = transport.accept()
            if channel is None:
                raise RuntimeError("channel failed. check authentication.")
            logger.info("Authentication successful")
            server.event.wait(10)
            if not server.event.is_set():
                logger.error("Server timed out waiting for event flag...")
                server.event.clear()
            while channel.transport.is_active():
                time.sleep(1)
        except Exception as err:
            logger.fatal("Fatal exception in server thread: %s", str(err))
            traceback.print_exc()
            try:
                transport.close()
            except Exception:
                logger.debug("Could not close transport after exception")


def start_server(keyfile, identity, service):
    """TODO"""
    try:
        logger.info("Loading zity identity from file: %s", identity)
        ztx = ZitiContext.from_path(identity)
        sock = ZitiSocket(type=socket.SOCK_STREAM)
        srv_sock = ztx.bind(service, sock=sock)
    except Exception as err:
        logger.fatal("Error creating or binding socket: %s", str(err))
        logger.fatal(
            "keyfile: %s, identity: %s, service: %s",
            keyfile, identity, service
        )
        traceback.print_exc()
        sys.exit(1)

    try:
        srv_sock.listen(20)
        logger.info("Listening for connections...")
    except Exception as err:
        logger.fatal("Error in socket listen: %s", str(err))
        traceback.print_exc()
        sys.exit(1)

    while True:
        try:
            conn, _ = srv_sock.accept()
        except Exception as err:
            logger.fatal("Error in socket accept: %s", str(err))
            traceback.print_exc()
            sys.exit(1)

        host_key = paramiko.RSAKey.from_private_key_file(keyfile)
        server_thread = ConnectionHandler(conn, host_key)
        server_thread.start()


def main():
    """TODO"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--level', '-l', dest='level', default='INFO',
        help='log level'
    )
    parser.add_argument(
        '--host-key-file', '-k', dest='keyfile', metavar='FILE',
        default=SSHD_KEYFILE,
        help='path to server private key'
    )
    parser.add_argument(
        '--identity', '-i', dest='identity', required=True, metavar='FILE',
        help='path to ziti identity file'
    )
    parser.add_argument(
        '--service', '-s', dest='service', required=True,
        help='path to ziti identity file'
    )

    args = parser.parse_args()

    if args.keyfile == SSHD_KEYFILE:
        ensure_private_key_file()

    paramiko_level = getattr(paramiko.common, args.level)
    paramiko.common.logging.basicConfig(level=paramiko_level)

    start_server(args.keyfile, args.identity, args.service)


if __name__ == '__main__':
    coloredlogs_install()
    logger = logging.getLogger(__name__)

    main()
