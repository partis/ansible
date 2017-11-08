#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule

import requests
import json

forum_sentry_argument_spec = dict(
  sentryProtocol        = dict( type ='str',  default='http', choices=['http', 'https'] ),
  sentryHost            = dict( type ='str',  required=True ),
  sentryPort            = dict( type ='int',  default=80 ),
  sentryUsername        = dict( type ='str',  required=True ),
  sentryPassword        = dict( type ='str',  required=True ),
  state                 = dict( type ='str',  default='present', choices=['present', 'absent'] )
)

class AnsibleForumSentry( object ):


  def __init__( self , module , path ):
    self.module = module
    self.result = { 'changed': False }
    self.path = path

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


  def apply(self):

    policy = self.checkPolicy( self.module.params['name'] )

    if policy.status_code == 200:
      if self.module.params['state'] == 'present':
        self.updatePolicy( policy.content )
      else:
        self.deletePolicy()
    elif policy.status_code == 404:
      if self.module.params['state'] == 'present':
        self.createPolicy()
    else:
      self.module.fail_json( msg='AnsibleForumSentry module failed. Forum Sentry returned HTTP Status Code ' + str( policy ) )

    self.module.exit_json(**self.result)
