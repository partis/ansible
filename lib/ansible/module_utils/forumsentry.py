#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule

import requests
import json

forum_sentry_argument_spec = dict(
  sentryProtocol	= dict( type ='str',  default='http', choices=['http', 'https'] ),
  sentryHost		= dict( type ='str',  required=True ),
  sentryPort		= dict( type ='int',  default=80 ),
  sentryUsername	= dict( type ='str',  required=True ),
  sentryPassword	= dict( type ='str',  required=True ),
  state			= dict( type ='str',  default='present', choices=['present', 'absent'] ),
  type			= dict( type ='str' )
)

class AnsibleForumSentry( object ):

 
  def __init__( self , module , path , update_skip_list ):
    self.module = module
    self.result = { 'changed': False }
    self.path = path
    self.update_skip_list = update_skip_list

    self.__url = self.module.params['sentryProtocol'] + "://" + self.module.params['sentryHost'] + ":" + str( self.module.params['sentryPort'] ) + self.path


  def deletePolicy( self ):
    httpDelete = requests.delete( self.__url + "/" + self.module.params['name'] , auth=( self.module.params['sentryUsername'] , self.module.params['sentryPassword'] ) , verify=True )
    if ( httpDelete.status_code == 200 ):
      self.result['changed'] = True
    else:
      self.module.fail_json( msg='Failed to delete policy `' + name + '`. Forum Sentry returned HTTP Status Code ' + str( httpDelete.status_code ) )


  def createPolicy( self ):
    jsonMessage={}
    for key in self.module.argument_spec:
      if key not in forum_sentry_argument_spec:
        jsonMessage[key] = self.module.params[key]
        message = json.dumps( jsonMessage )

    httpHeaders = { 'Content-Type': 'application/json' }
    httpPost = requests.post( self.__url , auth=( self.module.params['sentryUsername'] , self.module.params['sentryPassword'] ), verify=True , data=message , headers=httpHeaders )

    if ( httpPost.status_code == 201 ):
      self.result['changed'] = True
    else:
      self.module.fail_json( msg='Failed to create policy `' + self.module.params['name'] + '`. Forum Sentry returned HTTP Status Code ' + str( httpPost.status_code ) )


  def updatePolicy( self , policy ):
    jsonMessage=json.loads(policy)

    for key in self.module.argument_spec:
      if key not in forum_sentry_argument_spec:
        jsonMessage[key] = self.module.params[key]

    for skip in self.update_skip_list:
      del jsonMessage[skip]

    message = json.dumps( jsonMessage )

    httpHeaders = { 'Content-Type': 'application/json' }
    httpPut = requests.put( self.__url + '/' + self.module.params['name'] , auth=( self.module.params['sentryUsername'] , self.module.params['sentryPassword'] ) , verify=True , data=message , headers=httpHeaders )

    if ( httpPut.status_code == 200 ):
      self.result['changed'] = True
    else:
      self.module.fail_json( msg='Failed to update policy `' + self.module.params['name'] + '`. Forum Sentry returned HTTP Status Code ' + str( httpPut.status_code ) ) 


  def checkPolicy( self , name ):
    if name:
      httpGet = requests.get( self.__url + "/" + self.module.params['name'] , auth=( self.module.params['sentryUsername'] , self.module.params['sentryPassword'] ) , verify=True )
      return httpGet
    else:
      self.module.fail_json( msg='Failed to check policy. `name` is undefined' )


  def uploadObject( self ):

    # Because each API in Forum uses a different key to denote a file, we need to record these to make it
    # abstract ( or as much as we can, anyway ).
    fileProperties = { 'keyAndCertificateFile', 'keyFile', 'keyStoreFile', 'certificateFile', 'file' }

    # Dictionary for our Form Values for our Multi-Part Form
    formValues={}    

    # Build a dictionary containing all of the form values from the input arguments in Ansible.
    for key in self.module.argument_spec:
      if ( key not in forum_sentry_argument_spec ) and ( key not in fileProperties ):
        formValues[key] = self.module.params[key]

    # We need to determine what kind of KeyPair Policy we're creating. Then we need to extract the correct
    # Key token to send in the files object in the MultiPart post.
    for attr in fileProperties:
      if attr in self.module.argument_spec:
        fileKey = attr

    # We've found the key, let's get the file and read it in so we can send it as part of the MultiPart
    # post.
    file = open(self.module.params[fileKey], 'rb')

    # Dictionary for our File Values for our Multi-Part Form
    fileValues={ fileKey : file }

    # Now we have everything we need, we can post to Forum Sentry
    try:
        httpPost = requests.post( self.__url + '/import/' + self.module.params['type'] , auth=( self.module.params['sentryUsername'] , self.module.params['sentryPassword'] ), files=fileValues, data=formValues, verify=True )
        return httpPost.status_code
    finally:
      file.close()

  def applyObject(self):
    if self.module.params['state'] == 'present':
      upload = self.uploadObject()
      if ( upload == 202 ):
        self.result['changed'] = True
      elif ( upload == 409 ):
        self.result['changed'] = False
      else:
        self.module.fail_json( msg='Failed to upload object. Forum Sentry returned error: ' + str( httpPost.status_code ) )
    else:
      # Check if there is an associated Signer Group
      # Some Rank Code right here, messy AF ='(
      httpDelete = requests.delete( self.module.params['sentryProtocol'] + "://" + self.module.params['sentryHost'] + ":" + str( self.module.params['sentryPort'] ) + "/restApi/v1.0/policies/signerGroups/" + self.module.params['name'] , auth=( self.module.params['sentryUsername'] , self.module.params['sentryPassword'] ) , verify=True )
      delete = self.deletePolicy()
      if ( delete == 200 ):
        self.result['changed'] = True

    self.module.exit_json(**self.result)

  def applyPolicy(self):

    policy = self.checkPolicy( self.module.params['name'] )

    if policy.status_code == 200:
      if self.module.params['state'] == 'present':
        self.updatePolicy(policy.content)
      else:
        self.deletePolicy()
    elif policy.status_code == 404:
      if self.module.params['state'] == 'present':
        self.createPolicy()
    else:
      self.module.fail_json( msg='AnsibleForumSentry module failed. Forum Sentry returned HTTP Status Code ' + str( policy ) )

    self.module.exit_json(**self.result)
