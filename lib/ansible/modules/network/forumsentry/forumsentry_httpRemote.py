 #!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.forumsentry import forum_sentry_argument_spec
from ansible.module_utils.forumsentry import AnsibleForumSentry

def main():

  rest_context = '/restApi/v1.0/policies/httpRemotePolicies'

  module_args = dict(
    name                                = dict(type ='str',  required=True),
    proxyPolicy                         = dict(type ='str',  default=''),
    remoteAuthentication                = dict(type ='str',  default='NONE', choices=['NONE', 'STATIC', 'DYNAMIC', 'PROPAGATE']),
    enabled                             = dict(type ='bool', default=True),
    processResponse                     = dict(type ='bool', default=False),
    enableSSL                           = dict(type ='bool', default=False),
    SSLInitiationPolicy                 = dict(type ='str',  default=''),
    useChunking                         = dict(type ='bool', default=False),
    remotePort                          = dict(type ='int',  required=True),
    remoteServer                        = dict(type ='str',  required=True),
    tcpReadTimeout                      = dict(type ='int',  default=0),
    tcpConnectionTimeout                = dict(type ='int',  default=0),
    useBasicAuth                        = dict(type ='bool', default=False)
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
    if module.params['remotePort'] is None:
      module.fail_json(msg='Attribute `remotePort` must be defined when state=absent')
    if module.params['remoteServer'] is None:
      module.fail_json(msg='Attribute `remoteServer` must be defined when state=absent')

  # SSL Termination Policy must be defined if Listener is HTTPS
  if module.params['enableSSL'] == True:
    if module.params['SSLInitiationPolicy'] is None:
      module.fail_json(msg='Attribute `SSLInitiationPolicy` must be defined when enableSSL=true')

  forum.applyPolicy()

if __name__ == '__main__':
  main()
