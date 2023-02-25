from importlib import util
import argparse

DEBUG = "INFO"

argument_parser = argparse.ArgumentParser()
verbosity_group = argument_parser.add_mutually_exclusive_group()
verbosity_group.add_argument("-v", "--verbosity", type=str, choices=["DEBUG", "INFO", "ERRORONLY"], default="INFO", help="increase output verbosity")
verbosity_group.add_argument("-q", "--quiet", action="store_true", help="run script without output")
argument_parser.add_argument("-d", "--ndays", type=int, default=1, help="specify number of days to request (0 < ndays < 7)")

def pprint(string, level):

	if DEBUG == "DEBUG":
		print(string)
	elif DEBUG == "INFO" and level in ("INFO", "ERROR"):
		print(string)
	elif DEBUG == "ERRORONLY" and level in ("ERROR"):
		print(string)
	else:
		pass

def check_module(module_name):

	'''
	Function which check if module exists in your Python environment using "util".

		Paremeters:
			module_name (str): Name of the module you want to check

		Returns:
			int: 0 if exists, 1 otherwise.
	'''

	exists = util.find_spec(module_name) is not None
	if not exists:
		pprint(""" Module "{0}" does not exist """.format(module_name).center(100, '!'), "ERROR")
		return 1
	pprint(""" Module "{0}" does exist """.format(module_name).center(100, '-'), "DEBUG")
	return 0

def do_import(modules_list):

	"""
	Function which check if all modules sent in parameters can be import with success.

		Parameters:
			modules_list (list): List of all modules name you want to check

		Returns:
			bool: True if all modules can be imported successfully, False otherwise.
	"""

	for module in modules_list:
		try:
			exec("import {0}".format(module))
		except Exception as error:
			pprint(""" Error importing {0}'s module. Check the error bellow : """.format(module).center(100, '!'), "ERROR")
			pprint(""" {0} """.format(error.msg).center(100, ' '), "ERROR")
			return False
		else:
			pprint(""" Module {0} can be imported """.format(module).center(100, '-'), "DEBUG")
	return True

def check_import(modules_list):

	'''
	Function which check if all modules sent in parameters exists in your Python environment using check_module() function.

		Parameters:
			modules_list (list): List of all modules name you want to check

		Return:
			bool: True if all modules exist and can be imported successfully, False otherwise.
	'''

	# Use validation incremental int to check if every module in the list is installed. If validation >= 1, it means that one or more module is not OK.

	validation = 0
	for module in modules_list:
		validation += check_module(module)

	if validation != 0:
		pprint(""" One or more module does not exist """.center(100, '!'), "ERROR")
		return False
	pprint(""" Modules installation : Success """.center(100, '-'), "DEBUG")

	if do_import(modules_list):
		pprint(""" Modules importation : Success """.center(100, '-'), "DEBUG")
		return True
	pprint(""" Module importation : Failed """.center(100, '!'), "ERROR")

def get_OpenCTI_IPv4(flag = "", filters = "[]", IPs = {}, progress_bar = None):

	"""
	Function which retrieve IPv4 information in OpenCTI.

		Parameters:
			flag (str): flag which is used in the pagination of API response.
			filters (str): filters you want to apply to your request. Please the the OpenCTI GraphQL documentation if you want to know how.
			IPs (dict): dictionary used in the recursivity of the function to aggregate all the result.
			progress_bar (tqdm): progress bar display during the retrieval of datas

		Returns:
			bool: True if execution is successful, False otherwise.
			dict: datas get from OpenCTI :
				{
					str: {str: int}
				}
				for example :
				{
					"127.0.0.1": {"score": 50}
				}
	"""

	import requests, variables, secrets, json
	from tqdm import tqdm

	# If/Else to display debug information on the first recursion
	if flag == "":
		pprint(""" URL requested : {0} """.format(variables.OpenCTI_URL).center(100, '-'), "DEBUG")
		pprint(""" Query of the request : """.center(100, '-'), "DEBUG")
		pprint("{0}".format(variables.query_IPv4.format(flag, filters)), "DEBUG")

	# Configure parameters of the post request
	OpenCTI_request_URL = variables.OpenCTI_URL
	OpenCTI_request_query = {'query': variables.query_IPv4.format(flag, filters)}
	OpenCTI_request_headers = {'Authorization': 'Bearer {0}'.format(secrets.OpenCTI_TOKEN)}
	OpenCTI_request = requests.post(OpenCTI_request_URL, json=OpenCTI_request_query, headers=OpenCTI_request_headers)

	# If/Else regarding the status code response
	if OpenCTI_request.status_code != 200:
		pprint(""" Request : Failed | error code : {0} """.format(OpenCTI_request.status_code).center(100, '!'), "ERROR")
		pprint("{0}".format(OpenCTI_request.text), "ERROR")
		return False, {}

	# Converting request response to json format
	OpenCTI_request_json = json.loads(OpenCTI_request.text)

	# Catch regarding the API response (you can have an http 200 but the API returns errors)
	try:
		OpenCTI_request_json_error_message = OpenCTI_request_json["errors"][0]["message"]
		OpenCTI_request_json_error_code = OpenCTI_request_json["errors"][0]["data"]["http_status"]
	except KeyError:
		pass
	else:
		pprint(""" Request : Failed | error code : {0} """.format(OpenCTI_request_json_error_code).center(100, '!'), "ERROR")
		pprint("{0}".format(OpenCTI_request_json_error_message), "ERROR")
		return False, {}


	"""
	Response format example :
	"data": {
	    "stixCyberObservables": {
	      "pageInfo": {
	        "startCursor": <str>,
	        "endCursor": <str>,
	        "hasNextPage": <bool>,
	        "hasPreviousPage": <bool>,
	        "globalCount": <int>
	      },
	      "edges": [
	        {
	          "node": {
	            "id": <str>,
	            "entity_type": <str>,
	            "created_at": <str>,
	            "updated_at": <str>,
	            "observable_value": <str>,
	            "x_opencti_score": <int>,
	            "creator": {
	              "entity_type": <str>,
	              "name": <str>
	            },
	            "objectLabel": {
	              "edges": [
	                {
	                  "node": {
	                    "value": <str>
	                  }
	                }
	              ]
	            }
	          }
	        }
	      ]
	    }
	  }
	}
	"""

	# Retrieve macro datas of the response
	OpenCTI_request_hasNextPage = OpenCTI_request_json["data"]["stixCyberObservables"]["pageInfo"]["hasNextPage"]
	OpenCTI_request_elementsCount = len(OpenCTI_request_json["data"]["stixCyberObservables"]["edges"])
	OpenCTI_request_globalCount = OpenCTI_request_json["data"]["stixCyberObservables"]["pageInfo"]["globalCount"]

	# If/Else to display debug information on the first recursion and use the correct progress bar init
	if flag == "":
		pprint(""" Number of IPv4 retrieve : {0} """.format(OpenCTI_request_globalCount).center(100, '-'), "DEBUG")
		progress_bar_tmp = tqdm(total=OpenCTI_request_globalCount)
	else:
		progress_bar_tmp = progress_bar

	# Make a copy of the aggregate IPv4 dict so you can add datas
	IPs_tmp = IPs.copy()

	# Loop into the results of this recursion response
	for IP in range(OpenCTI_request_elementsCount):
		IP_score = OpenCTI_request_json["data"]["stixCyberObservables"]["edges"][IP]["node"]["x_opencti_score"]

		# Sometimes you don't have score for an IP, you can set a fix value like 50
		if IP_score is None:
			IP_score = 50

		# Add the IP in the aggregate dict with a dict containing the score as value
		IPs_tmp[OpenCTI_request_json["data"]["stixCyberObservables"]["edges"][IP]["node"]["observable_value"]] = {'score' : IP_score}

		# Update the progress bar of 1 element
		progress_bar_tmp.update(1)

	# If/Else to recurse or not regarding the API response
	if OpenCTI_request_hasNextPage:
		# Set the flag parameter for the next recursion
		OpenCTI_request_endCursor = OpenCTI_request_json["data"]["stixCyberObservables"]["pageInfo"]["endCursor"]
		return get_OpenCTI_IPv4(OpenCTI_request_endCursor, filters, IPs_tmp, progress_bar_tmp)

	# For the boolean returns value, we check if the number of keys in the dict is the same as the number return in the API response
	return (True and (len(IPs_tmp.keys()) == OpenCTI_request_globalCount)), IPs_tmp

def get_QRadar_IPv4(map_name = "Malicious - IP"):

	"""
	Function which retrieve dataset of a QRadar referential.

		Parameters:
			map_name (str): Name of the referential name in QRadar environment

		Returns:
			bool: True if execution is successful, False otherwise.
			dict: datas of the referential in the following format :
				{
					str: int
				}
				for example :
				{
					"127.0.0.1": 50
				}
	"""

	import requests, variables, secrets, json, urllib3
	
	# Ignore SSL Warning
	urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) 
	pprint(""" URL requested : {0}""".format(variables.QRadar_URL.format("")).center(100, '-'), "DEBUG")
	pprint(""" API endpoint : {0}""".format("reference_data/maps/" + map_name).center(100, '-'), "DEBUG")

	# Configure header with QRadar TOKEN
	QRadar_request_headers = {
	    'SEC':'{0}'.format(secrets.QRadar_TOKEN),
	    'Content-Type':'application/json',
	    'accept':'application/json'
	}

	pprint(""" Request headers : """.center(100, '-').format(str(QRadar_request_headers)), "DEBUG")

	# Request QRadar API endpoint without SSL
	QRadar_request_URL = variables.QRadar_URL.format("reference_data/maps/" + map_name)
	QRadar_request = requests.get(QRadar_request_URL, headers=QRadar_request_headers, verify=False)

	# If/Else regarding the status code response
	if QRadar_request.status_code != 200:
		pprint(""" Request : Failed | error code : {0} """.format(QRadar_request.status_code).center(100, '!'), "ERROR")
		pprint("{0}".format(QRadar_request.text), "ERROR")
		return False, {}

	# Converting request response to json format
	QRadar_request_json = json.loads(QRadar_request.text)

	"""
	Response format example :
	{
	  "timeout_type": "FIRST_SEEN",
	  "number_of_elements": <int>,
	  "data": {
	    "<IP>": {
	      "last_seen": <EPOCH TIME>,
	      "first_seen": <EPOCH TIME>,
	      "source": "reference data api",
	      "value": "<IP Score>"
	    },
	  "creation_time": <EPOCH TIME>,
	  "value_label": "Risk Score",
	  "name": "map_name",
	  "element_type": "NUM"
	}
	"""

	# If/Else regarding if referential contains 0 element
	if QRadar_request_json["number_of_elements"] == 0:
		return True, {}

	return True, {IP:QRadar_request_json["data"][IP]["value"] for IP in QRadar_request_json["data"].keys()}
	
def upload_IPv4_to_QRadar(IPs_to_upload, map_name = "Malicious - IP"):

	"""
	Function which upload IPv4 to a QRadar referential.

		Parameters:
			IPs_to_upload (dict): List of the IP to upload in QRadar
				{
					str: {str: int}
				}
				for example :
				{
					"127.0.0.1": {"score": 50}
				}
			map_name (str): Name of the referential name in QRadar environment

		Returns:
			bool: True if execution is successful, False otherwise.
	"""

	import requests, variables, secrets, urllib3

	# Ignore SSL Warning
	urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
	pprint(""" URL requested : {0}""".format(variables.QRadar_URL.format("")).center(100, '-'), "DEBUG")
	pprint(""" API endpoint : {0}""".format("reference_data/maps/bulk_load/" + map_name).center(100, '-'), "DEBUG")

	"""
	Format data payload for the post request using the following format :
	{
		str: str
	}
	for example :
	{
		"127.0.0.1": "50"
	}
	"""
	IPs_to_upload_format = {IP:str(IPs_to_upload[IP]['score']) for IP in IPs_to_upload.keys()}

	pprint(""" Data of the request : """.center(100, '-'), "DEBUG")
	pprint("{0}".format(IPs_to_upload_format), "DEBUG")

	# Configure header with QRadar TOKEN
	QRadar_request_headers = {
	    'SEC':'{0}'.format(secrets.QRadar_TOKEN),
	    'Content-Type':'application/json',
	    'accept':'application/json'
	}

	pprint(""" Request headers : """.format(str(QRadar_request_headers)).center(100, '-'), "DEBUG")

	# Request QRadar API endpoint without SSL
	QRadar_request_URL = variables.QRadar_URL.format("reference_data/maps/bulk_load/" + map_name)
	QRadar_request = requests.post(QRadar_request_URL, data=str(IPs_to_upload_format), headers=QRadar_request_headers, verify=False)

	# If/Else regarding the status code response
	if QRadar_request.status_code != 200:
		pprint(""" Request : Failed | error code : {0} """.format(QRadar_request.status_code).center(100, '!'), "ERROR")
		pprint("{0}".format(QRadar_request.text), "ERROR")
		return False

	return True

def delete_QRadar_IPv4(IPs_to_delete, IPs_in_QRadar, map_name = "Malicious - IP"):

	"""
	Function which delete entry in QRadar referential pass in parameter.
	Deletion API endpoint can only suppress entry one by one and you need to specify the key correct value to do the suppression.

		Parameters:
			IPs_to_delete (list): List of IPv4 you want to delete (the referential keys)
				[
					str
				]
				for example :
				[
					"127.0.0.1"
				]
			IPs_in_QRadar (dict): datas of the referential in the following format :
				{
					str: int
				}
				for example :
				{
					"127.0.0.1": 50
				}
			map_name (str): Name of the referential name in QRadar environment

		Returns:
			bool: True if execution is successful, False otherwise.
	"""

	import requests, variables, secrets, urllib3
	from tqdm import tqdm

	# Ignore SSL Warning
	urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
	pprint(""" URL requested : {0}""".format(variables.QRadar_URL.format("")).center(100, '-'), "DEBUG")
	pprint(""" API endpoint : reference_data/maps/{0}/<IP>?value=<SCORE>""".format(map_name).center(100, '-'), "DEBUG")

	# Configure header with QRadar TOKEN
	QRadar_request_headers = {
	    'SEC':'{0}'.format(secrets.QRadar_TOKEN),
	    'Content-Type':'application/json',
	    'accept':'application/json'
	}

	pprint(""" Request headers : """.format(str(QRadar_request_headers)).center(100, '-'), "DEBUG")

	# Setup the maximum value for the loop deletion
	IPs_to_delete_count = len(IPs_to_delete)
	pprint(""" Suppression of {0} IP(s) of "{1}" referential :""".format(IPs_to_delete_count,map_name), "DEBUG")

	progress_bar = tqdm(total=IPs_to_delete_count)

	# Loop into all the IPv4 you have to delete
	for IP_to_delete in IPs_to_delete:
		# Setup the URL for each iteration because you pass the key and value in the URL
		QRadar_request_URL = variables.QRadar_URL.format("reference_data/maps/{0}/{1}?value={2}".format(map_name, IP_to_delete, IPs_in_QRadar[IP_to_delete]))
		# Request QRadar API endpoint without SSL
		QRadar_request = requests.delete(QRadar_request_URL, headers=QRadar_request_headers, verify=False)

		# If/Else regarding the status code response
		if QRadar_request.status_code != 200:
			pprint(""" Request : Failed | error code : {0} """.format(QRadar_request.status_code).center(100, '!'), "ERROR")
			pprint("{0}".format(QRadar_request.text), "ERROR")

		progress_bar.update(1)

	return True

def verifiy_IPv4_score(IPs_to_verify, map_name = "Malicious - IP"):

	"""
	Function which verify IPv4 datas in QRadar referential. It delete IPv4 with a score bellow or equal 50 and update score which are changed.

		Parameters:
			IPs_to_verify (dict): Dict of IPv4 in the QRadar referential you want to verify
				{
					str: int
				}
				for example :
				{
					"127.0.0.1": 50
				}
			map_name (str): Name of the referential name in QRadar environment

		Returns:
			bool: True if execution is successful, False otherwise.
	"""

	import variables

	# Format OpenCTI filter and replace single quote with double, here an example : ["IP1", "IP2"]
	OpenCTI_request_filters = variables.IP_query_filter.format(str([IP for IP in IPs_to_verify.keys()])).replace('\'', '\"')

	# Retrieve OpenCTI informations for all IPv4 in QRadar referential
	get_OpenCTI_IPv4_execution, get_OpenCTI_IPv4_IPs = get_OpenCTI_IPv4(filters = OpenCTI_request_filters)
	# If/Else regarding the status of the execution
	if not get_OpenCTI_IPv4_execution:
		pprint(""" Retrieve IPv4 datas on OpenCTI : Failed """.center(100, "!"), "ERROR")
		return False
	pprint(""" Retrieve IPv4 datas on OpenCTI : Success """.center(100, "="), "DEBUG")

	# Setup the list of IPv4 to remove from QRadar referential and the dict of IPv4 and score that need update
	IPv4_to_remove = []
	IPv4_to_update = {} # We use a dict to fit the upload_IPv4_to_QRadar() parameter
	# Loop into all the IPv4
	for IP in get_OpenCTI_IPv4_IPs.keys():
		# Setup variables for old IPv4 score and the new one
		old_score = IPs_to_verify[IP]
		new_score = get_OpenCTI_IPv4_IPs[IP]['score']
		# Switch/case to remove IPv4 from referential if the score is bellow or equal 50, update the score in QRadar if the new score is different from the older or do nothing
		if new_score <= 50:
			IPv4_to_remove.append(IP)
		elif old_score != new_score:
			IPv4_to_update[IP] = {'score': new_score}
		else:
			continue

	# Delete IPv4 aggregate in the list by calling the delete_QRadar_IPv4() function
	delete_QRadar_IPv4_execution = delete_QRadar_IPv4(IPv4_to_remove, IPs_to_verify, map_name)
	if not delete_QRadar_IPv4_execution:
		pprint(""" IPv4 deletion in QRadar : Failed """.center(100, "!"), "ERROR")
		return False
	pprint(""" IPv4 deletion in QRadar : Success """.center(100, "="), "DEBUG")

	# Update IPv4 aggregate in the dict by calling the upload_IPv4_to_QRadar() function
	upload_IPv4_to_QRadar_execution = upload_IPv4_to_QRadar(IPv4_to_update, map_name)
	if not upload_IPv4_to_QRadar_execution:
		pprint(""" IPv4 upload in QRadar : Failed """.center(100, "!"), "ERROR")
		return False
	pprint(""" IPv4 upload in QRadar : Success """.center(100, "="), "DEBUG")

	return True

def main(ndays = 1):

	'''
	Main function of the program. It executes the following 5 steps :
	1. Check modules installation
	2. Get IPv4 list in QRadar referential (all)
	3. Get IPv4 list in OpenCTI database (last n days)
	4. Upload IPv4 of OpenCTI in QRadar referential (duplicates will be ignorate)
	5. Clean QRadar IPv4's which are not accurate anymore (score is less or equal than 50 over 100)

		Parameters:
			ndays (int): Number of day you want to have in your OpenCTI research. If you execute your script every day or more frequently, leave it as default (1)
			debug_level (str): Level of debug logs you will have ("NONE", "INFO", "DEBUG", "ERRORONLY"). By default, it's "INFO" logging only
	'''

	# First step, check modules installation state

	pprint(" Modules checks ".center(100, "="), "INFO")
	module_list = ["requests", "json", "secrets", "variables", "tqdm", "urllib3", "datetime"]
	check_import_execution = check_import(module_list)
	if not check_import_execution:
		pprint(""" Modules checks : Failed """.center(100, '!'), "ERROR")
		return
	pprint(""" Modules checks : Success """.center(100, '='), "INFO")

	import variables, datetime

	# Second step, get QRadar IPv4 list

	pprint(""" Get IPv4 of QRadar stored in {0} """.format(variables.QRadar_referential_name).center(100, "="), "INFO")
	get_QRadar_IPv4_execution, QRadar_IPs = get_QRadar_IPv4(variables.QRadar_referential_name)
	if not get_QRadar_IPv4_execution:
		pprint("""Retrieval of IPv4 in QRadar : Failed """.center(100, '!'), "ERROR")
		return
	pprint(""" Retrieval of IPv4 in QRadar : Success """.center(100, "="), "INFO")

	# Third step, get last n days IPv4 in OpenCTI database
	
	# Get the date of n days ago in the correct format
	date_last_ndays = (datetime.date.today() - datetime.timedelta(days = ndays)).strftime("%Y-%m-%d") 
	get_OpenCTI_IPv4_execution, OpenCTI_IPs = get_OpenCTI_IPv4(filters = variables.default_query_filter.format(date_last_ndays))
	if not get_OpenCTI_IPv4_execution:
		pprint(""" Retrieval of IPv4 in OpenCTI : Failed """.center(100, "!"), "ERROR")
		return
	pprint(""" Retrieval of IPv4 in OpenCTI : Success """.center(100, "="), "INFO")

	# Fourth step, upload OpenCTI's IPv4 in QRadar referential

	# For the uploading we used the OpenCTI IPv4 retrieved
	upload_QRadar_IPv4_to_QRadar_execution = upload_IPv4_to_QRadar(OpenCTI_IPs, map_name=variables.QRadar_referential_name)
	if not upload_QRadar_IPv4_to_QRadar_execution:
		pprint(""" Upload of IPv4 in QRadar : Failed """.center(100, '!'), "ERROR")
		return
	pprint(""" Upload of IPv4 in QRadar : Success """.center(100, "="), "INFO")

	# Fifth step, clean IPv4 in QRadar referential which aren't accurate anymore (OpenCTI score >= 50)

	if len(QRadar_IPs.keys()) > 0: # We must have at least 1 IPv4 in QRadar referential
		verifiy_IPv4_score_execution = verifiy_IPv4_score(QRadar_IPs, variables.QRadar_referential_name)
		if not verifiy_IPv4_score_execution:
			pprint(""" Cleaning of IPv4 in QRadar : Failed """.center(100, '!'), "ERROR")
			return
		pprint(""" Cleaning of IPv4 in QRadar : Success """.center(100, "="), "INFO")

def check_args(arg_ndays):
	if not 0 < arg_ndays < 7:
		raise argparse.ArgumentTypeError("0 < ndays < 7")
	return

if __name__ == '__main__':

	program_args = argument_parser.parse_args()
	check_args(program_args.ndays)
	
	if program_args.quiet:
		DEBUG = ""
	else:
		DEBUG = program_args.verbosity
	
	pprint(""" Script start """.center(100, "="), "INFO")

	main(ndays=program_args.ndays)

	pprint(""" Script end """.center(100, "="), "INFO")