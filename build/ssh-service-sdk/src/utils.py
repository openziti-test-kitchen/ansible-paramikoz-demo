"""TODO"""
import logging
from os.path import isfile
import subprocess

import coloredlogs
import paramiko

logger = logging.getLogger(__name__)


SSHD_KEYFILE = "paramikoz_sshd.key"


def ensure_private_key_file():
    """TODO"""
    if not isfile(SSHD_KEYFILE):
        logger.warning("Generating RSA keyfile. Things might get weird...")
        key = paramiko.RSAKey.generate(4096)
        key.write_private_key_file(SSHD_KEYFILE)


def coloredlogs_install():
    """TODO"""
    field_styles_overrides = {
        "asctime": {"color": "yellow", "feint": True},
        "levelname": {"bold": True, "color": "magenta"},
        "name": {"color": "white"}
    }

    level_styles_overrides = {
        "debug": {"color": 110}
    }

    coloredlogs.install(
        level='DEBUG',
        fmt="%(asctime)s %(levelname)s %(threadName)s:%(name)s:%(message)s",
        field_styles={
            **coloredlogs.DEFAULT_FIELD_STYLES,
            **field_styles_overrides
        },
        level_styles={
            **coloredlogs.DEFAULT_LEVEL_STYLES,
            **level_styles_overrides
        },
        isatty=True
    )


def exec_command(channel, command):
    """TODO"""
    if command[0] == "ziggywave":
        with open('easteregg', mode='r', encoding='utf-8') as ziggy:
            channel.sendall(ziggy.read())
        channel.send_exit_status(0)
        channel.close()
        return

    try:
        res = subprocess.run(command,
                             shell=False,
                             check=True,
                             text=True,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as err:
        logger.error('exception: %s', str(err))
        channel.sendall(bytes(f'An error occurred: {str(err)}', 'utf-8'))
        channel.send_exit_status(err.returncode)
    else:
        logger.debug("rc=%s: stdout='%s'", res.returncode, res.stdout)
        channel.sendall(bytes(res.stdout, 'utf-8'))
        channel.send_exit_status(res.returncode)
    finally:
        channel.close()
