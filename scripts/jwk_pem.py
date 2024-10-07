import jwcrypto.jwk as jwk
import requests
import argparse
arg_parser = argparse.ArgumentParser(description='JWK to PEM conversion tool')
arg_parser.add_argument('--jwk_uri', dest='jwk_uri', help='specify jwk uri', required=True)
args = arg_parser.parse_args()                        
print("Fetching JWKS from {}".format(args.jwk_uri))
request = requests.get(args.jwk_uri, verify=False)
jwks = request.json()
key_json = jwks['keys'][0] 
key = jwk.JWK(**key_json)
pub_pem = key.export_to_pem()
print(pub_pem)
#f = open("out.txt", "w")
#f.write(pub_pem.decode())
#f.close()

## python3 jwk_pem.py --jwk_uri <jwk-uri>