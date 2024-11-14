################################################### Connecting to AWS
import boto3

import json
################################################### Create random name for things
import random
import string

################################################### Parameters for Thing
thingArn = ''
thingId = ''
thingNameFomatter = 'picar_{}'
defaultPolicyName = 'car_policy'
###################################################

def createThing(name_index):
	global thingClient
	thingName = thingNameFomatter.format(name_index)
	thingResponse = thingClient.create_thing(
		thingName = thingNameFomatter.format(name_index)
	)
	data = json.loads(json.dumps(thingResponse, sort_keys=False, indent=4))
	for element in data: 
		if element == 'thingArn':
			thingArn = data['thingArn']
		elif element == 'thingId':
			thingId = data['thingId']
		createCertificate(thingName)

def createCertificate(thingName):
	global thingClient
	certResponse = thingClient.create_keys_and_certificate(
		setAsActive = True
	)
	data = json.loads(json.dumps(certResponse, sort_keys=False, indent=4))
	for element in data: 
		if element == 'certificateArn':
			certificateArn = data['certificateArn']
		elif element == 'keyPair':
			PublicKey = data['keyPair']['PublicKey']
			PrivateKey = data['keyPair']['PrivateKey']
		elif element == 'certificatePem':
			certificatePem = data['certificatePem']
		elif element == 'certificateId':
			certificateId = data['certificateId']
	
						
	with open(thingName + 'public.key', 'w') as outfile:
		outfile.write(PublicKey)
	with open(thingName + 'private.key', 'w') as outfile:
		outfile.write(PrivateKey)
	with open(thingName + 'cert.pem', 'w') as outfile:
		outfile.write(certificatePem)

	response = thingClient.attach_policy(
		policyName = defaultPolicyName,
		target = certificateArn
	)
	response = thingClient.attach_thing_principal(
		thingName = thingName,
		principal = certificateArn
	)

thingClient = boto3.client('iot')
for i in range(5):
	createThing(i)