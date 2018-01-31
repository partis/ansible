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
    idpGroup                            = dict(type ='str',  default='Default HTML Policy Group'),
    requestProcess                      = dict(type ='str',  default=''),
    responseProcess                     = dict(type ='str',  default=''),
    type                                = dict(type ='str',  require=True)
  )

  # merge argument_spec from module_utils/forumsentry.py
  module_args.update(forum_sentry_argument_spec)

  module = AnsibleModule(
    argument_spec=module_args,
    supports_check_mode=True
  )

  rest_context = '/restApi/v1.0/policies/' + module.params['type'] + 'Policies'

  update_skip_list = ['listenerPolicy', 'remotePolicy', 'virtualPath', 'remotePath']

  forum = AnsibleForumSentry(module, rest_context, update_skip_list)

  result = dict(changed=False)

  if module.check_mode:
    return result

  forum.applyPolicy()

if __name__ == '__main__':
  main()
