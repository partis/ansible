#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.forumsentry import forum_sentry_argument_spec
from ansible.module_utils.forumsentry import AnsibleForumSentry

def main():

  rest_context = '/restApi/v1.0/policies/certificates'

  module_args = dict(
    id			= dict( type ='str',  	required=True ),
    name        = dict( type='str',     default=id),
    state		= dict( type ='str',    default='absent', choices=['absent'] )
  )

  update_skip_list = []

  # merge argument_spec from module_utils/fortios.py
  module_args.update(forum_sentry_argument_spec)

  module = AnsibleModule(
    argument_spec=module_args,
    supports_check_mode=True
  )

  forum = AnsibleForumSentry(module, rest_context, update_skip_list)

  result = dict(changed=False)

  if module.check_mode:
    return result

  forum.applyPolicy()

if __name__ == '__main__':
  main()
