from ipaddress import IPv6Network
from random import getrandbits

from ansible.errors import AnsibleAction, AnsibleActionFail
from ansible.plugins.action import ActionBase

ULA_BASE = IPv6Network("fd00::/8")

class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp

        try:
            prefixlen = int(self._task.args.get('prefixlen', 64))
            if prefixlen < 48:
                raise AnsibleActionFail('prefixlen must be greater than 48')

            random_ula_net_48 = getrandbits(40) << (128 - 8 - 40)

            if prefixlen == 48:
                random_prefix = 0
            else:
                random_prefix = getrandbits(prefixlen - 48) << (128 - 8 - 40 - (prefixlen - 48))


            base_address = ULA_BASE.network_address + random_ula_net_48 + random_prefix

            result.update(
                address=base_address,
                network=IPv6Network((base_address, prefixlen),
            ))

        except AnsibleAction as e:
            result.update(e.result)

        return result
