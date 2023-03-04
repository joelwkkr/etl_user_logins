import psycopg2
from Cryptodome.Cipher import AES
import string, random
import subprocess
import json
from datetime import date
from base64 import b64decode, b64encode


# Normally you obviously wouldn't create your key here, and you wouldn't create a new key for each run, certainly, as should you ever be inclined to decrypt you need the original. SQS suggests AWS, so I would probably suggest KMS for key maintenance and access rights control
def createkey():
	#key = ''.join(random.choices(string.ascii_letters+string.digits, k=32)).encode()
	#iv = ''.join(random.choices(string.ascii_letters+string.digits, k=16)).encode()
	key = b'7iF0pE0dtqLbiPdv80QOgbrcDxzRG0Tj'
	iv = b'69YTjPk9uYVAyNqq'
	return key, iv

def maskvalue(val, key):
	cipher = AES.new(key, AES.MODE_SIV)
	return cipher.encrypt_and_digest(val.encode())

def unmaskvalue(val, key, tag):
	cipher = AES.new(key, AES.MODE_SIV)
	return cipher.decrypt_and_verify(val, tag).decode()

def initiatedbconnection():
	return psycopg2.connect(user = 'postgres', password = 'postgres', host = 'localhost', port = '5432', database = 'postgres')

# return a CLI request for SQS records. It would probably be better to implement this with something like boto3, but that doesn't seem like an option with awslocal
def retrieveAWSCLISQS(clistring):
	return subprocess.run(clistring, capture_output = True, shell = True) 




try:

	awsLocalSQS = 'awslocal.bat sqs receive-message --queue-url http://localhost:4566/000000000000/login-queue --max-number-of-messages=10'
	crkey, iv = createkey() 

	cmdout = retrieveAWSCLISQS(awsLocalSQS)  #receive output of awslocal receive-message

	dbconnection = initiatedbconnection()
	cursor = dbconnection.cursor()

	x = 0

	# Keep running queries against Localstack SQS until it has no more records to dispense 
	# Not actually sure what an empty SQS returns
	while cmdout is not None:

		messagesjson = json.loads(cmdout.stdout.decode()) #parse output as json, into dict type
		messages = messagesjson['Messages']

		#construct one insert statement for each message
		for x in messages:
			body = json.loads(x['Body'])

			user_id = body['user_id']
			device_type = body['device_type']

			masked_ip, masked_ip_tag = maskvalue(body['ip'], crkey)
			masked_ip = str(masked_ip).replace("'", "''") # make a string with single quotes compatible with postgres insert

			masked_device_id, masked_device_id_tag = maskvalue(body['device_id'], crkey)
			masked_device_id = str(masked_device_id).replace("'", "''") # make a string with single quotes compatible with postgres insert

			locale = body['locale']
			app_version = body['app_version']

			# construct insert
			insertstring = f"insert into user_logins (user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date) values ('{user_id}', '{device_type}', '{masked_ip}', '{masked_device_id}', '{locale}', '{app_version}', '{date.today()}');"

			#print(insertstring)
			cursor.execute(insertstring)

		dbconnection.commit()
		cmdout = retrieveAWSCLISQS(awsLocalSQS) #receive output of awslocal receive-message
		print(cmdout)

	dbconnection.commit()
	cursor.close()
	dbconnection.close()


except(Exception) as error:
	print(error)

finally:
	if dbconnection:
		cursor.close()
		dbconnection.close()
		print("DB Connection Terminated.")



