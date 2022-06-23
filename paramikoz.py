"""OpenZiti paramiko connection plugin wrapper"""
import os

import yaml
from ansible.plugins.connection.paramiko_ssh import (
    DOCUMENTATION as PARAMIKO_SSH_DOC,
    Connection as ParamikoConnection
)

import openziti

plugin_doc = yaml.full_load(PARAMIKO_SSH_DOC)

EXT_MSG = 'Extended by OpenZiti.'

EXT_OPTS = {
    "ziti_identities": {
        "description": "ziti identities to use for connection",
        "default": None,
        "env": [{"name": "ANSIBLE_ZITI_IDENTITIES"}],
        "ini": [{"section": "paramikoz_connection", "key": "ziti_identities"}],
        "var": [{"name": "ziti_identities"}],
        "required": True,
        "type": "pathlist",
        "version_added": "1.0'"
    },
    "ziti_log_level": {
        "description": "verbosity of ziti library",
        "default": 0,
        "env": [{"name": "ANSIBLE_ZITI_LOG_LEVEL"}],
        "ini": [{"section": "paramikoz_connection", "key": "ziti_log_level"}],
        "var": [{"name": "ziti_log"}],
        "required": False,
        "type": "integer",
        "version_added": "1.0"
    }
}

plugin_doc['author'] += f" - {EXT_MSG}"
plugin_doc['name'] = 'paramikoz'
plugin_doc['short_description'] += f". {EXT_MSG}"
plugin_doc['description'].append(EXT_MSG)
plugin_doc['options'] = {**plugin_doc['options'], **EXT_OPTS}

DOCUMENTATION = yaml.dump(plugin_doc)


class Connection(ParamikoConnection):
    '''Ziti based connection wrapper for paramiko_ssh'''
    # pylint: disable=import-outside-toplevel

    transport = 'paramikoz'

    def __init__(self, *args, **kwargs):
        """init wrapper"""
        super().__init__(*args, **kwargs)
        self.log_level = self.get_option('ziti_log_level')
        if os.getenv('ZITI_LOG') is None:
            os.environ['ZITI_LOG'] = str(self.log_level)
        self.identities = self.get_option('ziti_identities')
        for identity in self.identities:
            openziti.load(identity)

    def _connect(self):
        '''Wrap connection activation object with ziti'''

        with openziti.monkeypatch():
            super()._connect()
