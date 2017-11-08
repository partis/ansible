 #!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.forumsentry import forum_sentry_argument_spec
from ansible.module_utils.forumsentry import AnsibleForumSentry

def main():

  module_args = dict(
    name                                = dict(type ='str',  required=True),
    enabledProtocols                    = dict(type ='str',  default='TLSv1.2', choices=['TLSv1.2', 'TLSv1.1', 'TLSv1', 'SSLv3']),
    keyPair                             = dict(type ='str',  default=''),
    signerGroup                         = dict(type ='str',  required=True),
    description                         = dict(type ='str',  default=''),
    ignoreHostnameVerification          = dict(type ='bool',  default=False)
  )

  # merge argument_spec from module_utils/forumsentry.py
  module_args.update(forum_sentry_argument_spec)

  module = AnsibleModule(
    argument_spec=module_args,
    supports_check_mode=True
  )

  rest_context = '/restApi/v1.0/policies/sslInitiationPolicies'

  update_skip_list = []

  forum = AnsibleForumSentry(module, rest_context, update_skip_list)

  result = dict(changed=False)

  if module.check_mode:
    return result

  forum.applyPolicy()

if __name__ == '__main__':
  main()
