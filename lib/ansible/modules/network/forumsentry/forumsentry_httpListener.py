 #!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.forumsentry import forum_sentry_argument_spec
from ansible.module_utils.forumsentry import AnsibleForumSentry

def main():

  rest_context = '/restApi/v1.0/policies/httpListenerPolicies'

  module_args = dict(
    name                                = dict(type ='str',  required=True),
    aclPolicy                           = dict(type ='str',  default=''),
    description                         = dict(type ='str',  default=''),
    enabled                             = dict(type ='bool', default=True),
    errorTemplate                       = dict(type ='str',  default=''),
    ipAclPolicy                         = dict(type ='str',  default=''),
    listenerHost                        = dict(type ='str',  default=''),
    listenerSSLEnabled                  = dict(type ='bool', default=False),
    listenerSSLPolicy                   = dict(type ='str',  default=''),
    passwordAuthenticationRealm         = dict(type ='bool', default=False),
    passwordParameter                   = dict(type ='str',  default=''),
    port                                = dict(type ='int',  default=8080),
    readTimeoutMillis                   = dict(type ='int',  default=0),
    requirePasswordAuthentication       = dict(type ='bool', default=False),
    useBasicAuthentication              = dict(type ='bool', default=False),
    useChunking                         = dict(type ='bool', default=True),
    useCookieAuthentication             = dict(type ='bool', default=False),
    useDeviceIp                         = dict(type ='bool', default=True),
    useDigestAuthentication             = dict(type ='bool', default=False),
    useFormPostAuthentication           = dict(type ='bool', default=False),
    useKerberosAuthentication           = dict(type ='bool', default=False),
    usernameParameter                   = dict(type ='str',  default='')
  )

  update_skip_list = []

  # merge argument_spec from module_utils/fortios.py
  module_args.update(forum_sentry_argument_spec)

  module = AnsibleModule(
    argument_spec=module_args,
    supports_check_mode=True,
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
  if module.params['listenerSSLEnabled'] == True:
    if module.params['listenerSSLPolicy'] is None:
      module.fail_json(msg='Attribute `listenerSSLPolicy` must be defined when listenerSSLEnabled=true')

  forum.applyPolicy()

if __name__ == '__main__':
  main()
