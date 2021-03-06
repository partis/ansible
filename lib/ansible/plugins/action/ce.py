#
# (c) 2016 Red Hat Inc.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import sys
import copy

from ansible import constants as C
from ansible.plugins.action.normal import ActionModule as _ActionModule
from ansible.module_utils.ce import ce_provider_spec
from ansible.module_utils.network_common import load_provider


try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()


class ActionModule(_ActionModule):

    def run(self, tmp=None, task_vars=None):
        if self._play_context.connection != 'local':
            return dict(
                failed=True,
                msg='invalid connection specified, expected connection=local, '
                    'got %s' % self._play_context.connection
            )

        provider = load_provider(ce_provider_spec, self._task.args)
        transport = provider['transport'] or 'cli'

        display.vvvv('connection transport is %s' % transport, self._play_context.remote_addr)

        if transport == 'cli':
            pc = copy.deepcopy(self._play_context)
            pc.connection = 'network_cli'
            pc.network_os = 'ce'
            pc.remote_addr = provider['host'] or self._play_context.remote_addr
            pc.port = int(provider['port'] or self._play_context.port or 22)
            pc.remote_user = provider['username'] or self._play_context.connection_user
            pc.password = provider['password'] or self._play_context.password
            pc.timeout = int(provider['timeout'] or C.PERSISTENT_COMMAND_TIMEOUT)
            self._task.args['provider'] = provider.update(
                host=pc.remote_addr,
                port=pc.port,
                username=pc.remote_user,
                password=pc.password,
                ssh_keyfile=pc.private_key_file
            )
            display.vvv('using connection plugin %s' % pc.connection, pc.remote_addr)
            connection = self._shared_loader_obj.connection_loader.get('persistent', pc, sys.stdin)

            socket_path = connection.run()
            display.vvvv('socket_path: %s' % socket_path, pc.remote_addr)
            if not socket_path:
                return {'failed': True,
                        'msg': 'unable to open shell. Please see: ' +
                               'https://docs.ansible.com/ansible/network_debug_troubleshooting.html#unable-to-open-shell'}

            # make sure we are in the right cli context which should be
            # enable mode and not config module
            rc, out, err = connection.exec_command('prompt()')
            while str(out).strip().endswith(']'):
                display.vvvv('wrong context, sending exit to device', self._play_context.remote_addr)
                connection.exec_command('return')
                rc, out, err = connection.exec_command('prompt()')

            task_vars['ansible_socket'] = socket_path

        # make sure a transport value is set in args
        self._task.args['transport'] = transport

        result = super(ActionModule, self).run(tmp, task_vars)
        return result
