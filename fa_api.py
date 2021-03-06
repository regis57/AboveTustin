#
# fa_api.py
#
# Sergiusz Paprzycki <serek@walcz.net>
# 

import requests

def FlightInfo(ident, username, apiKey, verbose=0, results=10):
	try:
		fxmlUrl = "https://flightxml.flightaware.com/json/FlightXML3/"
		ident = ident.strip()
		payload = {'ident':ident, 'howMany':results}
		response = requests.get(fxmlUrl + "FlightInfoStatus", params=payload, auth=(username, apiKey))
		output = dict()
		if response.status_code == 200:
			decodedResponse = response.json()
			print(decodedResponse)
			if 'FlightInfoStatusResult' not in decodedResponse:
				return False
			for flight in decodedResponse['FlightInfoStatusResult']['flights']:
				if 'status' not in flight:
					continue
				if flight['status'] == 'On' or flight['status'] == 'En':
					output = {
						"orig_name":flight['origin']['airport_name'],
						"orig_city":flight['origin']['city'],
						"orig_alt":flight['origin']['alternate_ident'],
						"orig_code":flight['origin']['code'],
						"dest_name":flight['destination']['airport_name'],
						"dest_city":flight['destination']['city'],
						"dest_alt":flight['destination']['alternate_ident'],
						"dest_code":flight['destination']['code']
					}
					break
			if verbose:
				return decodedResponse
			else:
				return output
		else:
			return False
	except:
		print("exception in fa_api.FlightInfo()")
		import sys
		print (sys.exc_info()[0])
		return False
