"""TODO"""
import getpass
import logging
import os
import shlex
import threading
from binascii import hexlify

import paramiko
from paramiko.util import u
from sftpserver.stub_sftp import StubSFTPServer

from decorators import cls_func_wrapper, func_wrapper
from utils import exec_command

logger = logging.getLogger(__name__)

USER_HOME = os.path.expanduser('~')
USER = getpass.getuser()


@cls_func_wrapper(func_wrapper, logger=logger)
class Server(paramiko.ServerInterface):
    """TODO"""
    good_priv_key = paramiko.RSAKey(filename=f"{USER_HOME}/.ssh/id_rsa")

    def __init__(self):
        self.event = threading.Event()

    def get_allowed_auths(self, username):
        return "publickey"

    def check_auth_publickey(self, username, key):
        logger.info(
                "Auth attempt with key: %s",
                u(hexlify(key.get_fingerprint()))
        )
        if (username == USER) and (key == self.good_priv_key):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_env_request(self, channel, name, value):
        return True

    def check_channel_pty_request(
        self, channel, term, width, height, pixelwidth, pixelheight, modes
    ):
        # pylint: disable=too-many-arguments
        return True

    def check_channel_exec_request(self, channel, command):
        logger.info("Command submitted: %s", command)
        command_s = shlex.split(command.decode('utf-8'), posix=True)
        threading.Thread(
            target=exec_command,
            args=(channel, command_s,)
        ).start()
        self.event.set()
        return True


class SFTPServer(StubSFTPServer):
    """TODO"""

    ROOT = '/'
    logger.debug("ROOT is: %s", ROOT)
