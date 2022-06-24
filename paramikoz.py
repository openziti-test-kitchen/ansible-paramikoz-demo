"""OpenZiti paramiko connection plugin wrapper"""
import os

import openziti
from ansible.plugins.connection.paramiko_ssh import \
    Connection as ParamikoConnection

DOCUMENTATION = '''
    extends_documentation_fragment: paramiko_doc_fragment
    options:
      ziti_identities:
        description: ziti identities to use for connection
        default: null
        env:
          - name: ANSIBLE_ZITI_IDENTITIES
        ini:
          - section: paramikoz_connection
            key: ziti_identities
        vars:
          - name: ziti_identities
        required: true
        type: pathlist

      ziti_log_level:
        description: verbosity of ziti library
        default: 0
        env:
          - name: ANSIBLE_ZITI_LOG_LEVEL
        ini:
          - section: paramikoz_connection
            key: ziti_log_level
        vars:
          - name: ziti_log_level
        required: false
        type: integer
'''


class Connection(ParamikoConnection):
    '''Ziti based connection wrapper for paramiko_ssh'''
    # pylint: disable=import-outside-toplevel

    transport = 'paramikoz'

    def _connect(self):
        '''Wrap connection activation object with ziti'''

        self.log_level = self.get_option('ziti_log_level')
        if os.getenv('ZITI_LOG') is None:
            os.environ['ZITI_LOG'] = str(self.log_level)
        self.identities = self.get_option('ziti_identities')
        for identity in self.identities:
            openziti.load(identity)

        with openziti.monkeypatch():
            super()._connect()
