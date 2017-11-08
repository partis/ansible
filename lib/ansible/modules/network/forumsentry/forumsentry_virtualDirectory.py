 #!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.forumsentry import forum_sentry_argument_spec
from ansible.module_utils.forumsentry import AnsibleForumSentry

def main():

  module_args = dict(
    name                                = dict(type ='str',  required=True),
    remotePath                          = dict(type ='str',  default=''),
    responseProcessType                 = dict(type ='str',  default='TASK_LIST_GROUP', choices=['TASK_LIST', 'TASK_LIST_GROUP']),
    requestProcessType                  = dict(type ='str',  default='TASK_LIST_GROUP', choices=['TASK_LIST', 'TASK_LIST_GROUP']),
    listenerPolicy                      = dict(type ='str',  required=True),
    virtualPath                         = dict(type ='str',  default=''),
    remotePolicy                        = dict(type ='str',  default=''),
    description                         = dict(type ='str',  default=''),
    requestProcess                      = dict(type ='str',  default=''),
    responseProcess                     = dict(type ='str',  default=''),
    type                                = dict(type ='str',  require=True),
    parent                              = dict(type ='str',  require=True),
    aclPolicy                           = dict(type ='str',  default=''),
    virtualHost                         = dict(type ='str',  default=''),
    enabled                             = dict(type ='bool',  default=True),
    errorTemplate                       = dict(type ='str',  default=''),
    useRemotePolicy                     = dict(type ='bool',  default=True)
  )

  # merge argument_spec from module_utils/forumsentry.py
  module_args.update(forum_sentry_argument_spec)

  module = AnsibleModule(
    argument_spec=module_args,
    supports_check_mode=True
  )

  rest_context = '/restApi/v1.0/policies/' + module.params['type'] + 'Policies/' + module.params['parent'] + '/virtualDirectories'

  update_skip_list = []

  forum = AnsibleForumSentry(module, rest_context, update_skip_list)

  result = dict(changed=False)

  if module.check_mode:
    return result

  # Remote must be declared if useRemote is true
  if module.params['useRemotePolicy'] == True:
    if module.params['remotePolicy'] is None:
      module.fail_json(msg='Attribute `remotePolicy` must be defined when useRemotePolicy=True')

  forum.applyPolicy()

if __name__ == '__main__':
  main()
