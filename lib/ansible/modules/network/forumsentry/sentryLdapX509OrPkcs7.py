#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.forumsentry import forum_sentry_argument_spec
from ansible.module_utils.forumsentry import forum_sentry_required_together
from ansible.module_utils.forumsentry import AnsibleForumSentry

def main():

  module_args = dict(
    name			= dict( type ='str' ),
    ldapAttribute		= dict( type ='str' ),
    ldapQuery			= dict( type ='str' ),
    ldapServer			= dict( type ='str' ),
    port			= dict( type ='int' ),
    authenticateServer		= dict( type ='bool' ),
    createSignerGroup 		= dict( type ='bool' ),
    user			= dict( type ='str' ),
    password			= dict( type ='str' ),
    useSSL			= dict( type ='bool' )
  )

  module_args.update(forum_sentry_argument_spec)

  sentry_required_if = [
    [ 'state' , 'present' , [ 'name' , 'ldapAttribute' , 'ldapQuery' , 'ldapServer' , 'port' ] ] ,
    [ 'state' , 'absent' , [ 'name' ] ]
  ]

  ldapX509OrPkcs7_required_together = [
    [ 'user', 'password' ]
  ]

  module = AnsibleModule(
    argument_spec=module_args,
    supports_check_mode=True,
    required_if=sentry_required_if,
    required_together=forum_sentry_required_together + ldapX509OrPkcs7_required_together
  )
  
  forum = AnsibleForumSentry( module )

  if module.check_mode:
    return result
 
  httpService_KeyPair = '/restApi/v1.0/policies/keyPairs'
  httpService_Certificates = '/restApi/v1.0/policies/x509Certificates'
  httpService_SignerGroups = '/restApi/v1.0/policies/signerGroups'
  httpService_LdapX509OrPkcs7 = '/restApi/v1.0/policies/keyPairs/import/ldapX509OrPkcs7'

  if module.params['state'] == 'present': 
    forum.importSentryObject( httpService_LdapX509OrPkcs7 )
  else:
    signerGroups = forum.getSentryObject( httpService_SignerGroups , module.params['name'] )
    certificates = forum.getSentryObject( httpService_Certificates , module.params['name'] )
    keyPairs = forum.getSentryObject( httpService_KeyPair , module.params['name'] )

    if signerGroups:
      for signerGroup in signerGroups:
        forum.deleteSentryObject( httpService_SignerGroups  , signerGroup ) 

    if certificates:
      for certificate in certificates:
        forum.deleteSentryObject( httpService_Certificates  , certificate )

    if keyPairs:
      for keyPair in keyPairs:
        forum.deleteSentryObject( httpService_KeyPair  , keyPair )

  module.exit_json(**forum.result)

if __name__ == '__main__':
  main()
