#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: forumsentry_listener.py

short_description: Does stuff to forum sentry listener policies

version_added: "2.4"

description:
    - "Does stuff to forum sentry listener policies"

options:
    name:
        description:
            - This is the msg to send to the sample module
        required: true
    new:
        description:
            - Control to demo if the result of this module is changed or not
        required: false

extends_documentation_fragment:

author:
    - Andrew Partis (@partis)
'''

EXAMPLES = '''
# Pass in a msg
- name: Test with a msg
  my_new_test_module:
    name: hello world

# pass in a msg and have changed true
- name: Test with a msg and changed output
  my_new_test_module:
    name: hello world
    new: true

# fail the module
- name: Test failure of the module
  my_new_test_module:
    name: fail me
'''

RETURN = '''
original_msg:
    description: The original name param that was passed in
    type: str
msg:
    description: The output msg that the sample module generates
'''

from ansible.module_utils.basic import AnsibleModule
import requests
from requests.auth import HTTPDigestAuth
import json

def run_module():
    # define the available arguments/parameters that a user can pass to
    # the module
    module_args = dict(
	name=dict(type='str', required=True),
	type=dict(type='str', required=False, default='http'),
	policy=dict(type='str', required=False, default="{\"name\": \"newListenerPolicy\"}"),
	server=dict(type='str', required=False, default='127.0.0.1'),
        port=dict(type='int', required=False, default=1234),
        secure=dict(type='bool', required=False, default=False),
        username=dict(type='str', required=False, default='admin'),
        password=dict(type='str', required=False, default='password'),
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        msg=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        return result

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)

    #check for an existing policy
    url = "http://"

    if(module.params['secure']): 
	url = "https://"

    url += module.params['server'] + ":" + str(module.params['port']) + "/restApi/v1.0/policies/" + module.params['type'] + "ListenerPolicies"

    response = requests.get(url + "/" + module.params['name'] ,auth=(module.params['username'], module.params['password']), verify=True)

    #if the policy already exists we need to check if it is the same as what has been passed, if not then update the server
    if(response.ok):
        data = json.loads(response.content)

        #parse policy and loop through each attribute to compare with whats returned from server

        policyJson = json.loads(module.params['policy'])

        for attrib in policyJson:
	    if(policyJson[attrib] != data[attrib]):
                #print data[attrib]
		#print data
                data[attrib] = policyJson[attrib]
                #print data[attrib]
		#print json.dumps(data)
                putHeaders = {'Content-Type': 'application/json'}

                putResponse = requests.put(url + "/" + module.params['name'], auth=(module.params['username'], module.params['password']), verify=True, data=json.dumps(data), headers=putHeaders)

                if(putResponse.ok):
                    putData = json.loads(putResponse.content)

                    result['msg'] = putData
                
                    if(policyJson[attrib] != putData[attrib]):
                        module.fail_json(msg='Property: ' + attrib + ' has not updated', **result)
		    else:
                        result['changed'] = True
		    #print putData
                else:
                    result['msg'] = putResponse.content
                    module.fail_json(**result)

    #if the policy doesnt currently exist then post the policy data passed to the server to create the policy
    elif(response.status_code == 404):

        postHeaders = {'Content-Type': 'application/json'}

	postResponse = requests.post(url,auth=(module.params['username'], module.params['password']), verify=True, data=module.params['policy'], headers=postHeaders)

        #if the policy creates successfully then set changed status to true
	if(postResponse.ok):
	    postData = json.loads(postResponse.content)

            result['changed'] = True
	    result['msg'] = postData
        else:
            result['msg'] = postResponse.content
            module.fail_json(**result)
    else:
        result['msg'] = postResponse.content
        module.fail_json(**result)

    # use whatever logic you need to determine whether or not this module
    # made any modifications to your target

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the msg and the result
    #if module.params['name'] == 'fail me':
     #   module.fail_json(msg='You requested this to fail', **result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
