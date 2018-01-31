 #!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.forumsentry import forum_sentry_argument_spec
from ansible.module_utils.forumsentry import AnsibleForumSentry

def main():

  rest_context = '/restApi/v1.0/policies/amqp10ListenerPolicies'

  module_args = dict(
    name                                = dict(type ='str',  required=True),
    aclPolicy                           = dict(type ='str',  default=''),
    description                         = dict(type ='str',  default=''),
    enabled                             = dict(type ='bool', default=True),
    errorTemplate                       = dict(type ='str',  default=''),
    ipAclPolicy                         = dict(type ='str',  default=''),
    ip 		                        = dict(type ='str',  required=True),
    useSsl                              = dict(type ='bool', default=False),
    sslPolicy                           = dict(type ='str',  default=''),
    saslMechanism                       = dict(type ='str', default='NONE', choices=['NONE', 'ANONYMOUS', 'PLAIN', 'CRAM_MD5', 'EXTERNAL']),
    port                                = dict(type ='int',  default=5672),
    readTimeoutMillis                   = dict(type ='int',  default=0),
    useDeviceIp                         = dict(type ='bool', default=True),
    interface                           = dict(type ='str',  default='WAN', choices=['WAN', 'LAN'])
  )

  update_skip_list = []

  # merge argument_spec from module_utils/forumsentry.py
  module_args.update(forum_sentry_argument_spec)

  module = AnsibleModule(
    argument_spec=module_args,
    supports_check_mode=True
  )

  forum = AnsibleForumSentry(module, rest_context, update_skip_list)

  result = dict(changed=False)

  if module.check_mode:
    return result

  # Port must be declared if state is present
  if module.params['state'] == 'present':
    if module.params['port'] is None:
      module.fail_json(msg='Attribute `port` must be defined when state=absent')

  # SSL Termination Policy must be defined if Listener is HTTPS
  if module.params['useSsl'] == True:
    if module.params['sslPolicy'] is None:
      module.fail_json(msg='Attribute `sslPolicy` must be defined when useSsl=true')

  forum.applyPolicy()

if __name__ == '__main__':
  main()
