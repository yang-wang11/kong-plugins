# pip install pyjwt
import jwt
from jwt import InvalidSignatureError, ExpiredSignatureError, DecodeError, InvalidAudienceError

def verify_jwt_rs256(token, public_key):
    try:
        # Decode the token without verifying `aud` first
        decoded_token = jwt.decode(token, public_key, algorithms=["RS256"], options={"verify_aud": False})
        print("JWT is valid!")
        return decoded_token
    except ExpiredSignatureError:
        print("Token has expired!")
    except InvalidSignatureError:
        print("Invalid signature!")
    except InvalidAudienceError as e:
        print(f"Audience verification failed: {e}")
    except DecodeError:
        print("Failed to decode JWT!")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Your JWT token
    token = ""+\
"eyJhbGciOiJSUzI1NiIsImprdSI6Imh0dHBzOi8vc2FwLWhhbmEtY2xvdWQtaGMtY2FuYXJ5LTEuYXV0aGVudGljYXRpb24uc2FwLmhhbmEub25kZW1hbmQuY29tL3Rva2VuX2tleXMiLCJraWQiOiJkZWZhdWx0LWp3dC1rZXktNDg3MGEzZWQzNCIsInR5cCI6IkpXVCIsImppZCI6ICI1ZDNQT0FvQTZMY25EeDJYRkdnYk9nVXR2YWVGUXRwYVNjYjlJSC9LYnpJPSJ9.eyJqdGkiOiJiZTMyMmQyYTllZTk0NzcxODUzZGU4ZmJhZmZjMTY3NSIsImV4dF9hdHRyIjp7ImVuaGFuY2VyIjoiWFNVQUEiLCJzdWJhY2NvdW50aWQiOiJiYTcwNWZhOC04MWRhLTQ3NWQtYjEwMy01YzM3NmZkYTkzM2IiLCJ6ZG4iOiJzYXAtaGFuYS1jbG91ZC1oYy1jYW5hcnktMSJ9LCJzdWIiOiJzYi1oYy1jYW5hcnktYXBpZ2F0ZXdheS1oYW5hLWNsb3VkIWI5MTQ4IiwiYXV0aG9yaXRpZXMiOlsidWFhLnJlc291cmNlIl0sInNjb3BlIjpbInVhYS5yZXNvdXJjZSJdLCJjbGllbnRfaWQiOiJzYi1oYy1jYW5hcnktYXBpZ2F0ZXdheS1oYW5hLWNsb3VkIWI5MTQ4IiwiY2lkIjoic2ItaGMtY2FuYXJ5LWFwaWdhdGV3YXktaGFuYS1jbG91ZCFiOTE0OCIsImF6cCI6InNiLWhjLWNhbmFyeS1hcGlnYXRld2F5LWhhbmEtY2xvdWQhYjkxNDgiLCJncmFudF90eXBlIjoiY2xpZW50X2NyZWRlbnRpYWxzIiwicmV2X3NpZyI6IjM3NzAxZmRlIiwiaWF0IjoxNzI4NTMzMzUxLCJleHAiOjE3Mjg1NzY1NTEsImlzcyI6Imh0dHBzOi8vc2FwLWhhbmEtY2xvdWQtaGMtY2FuYXJ5LTEuYXV0aGVudGljYXRpb24uc2FwLmhhbmEub25kZW1hbmQuY29tL29hdXRoL3Rva2VuIiwiemlkIjoiYmE3MDVmYTgtODFkYS00NzVkLWIxMDMtNWMzNzZmZGE5MzNiIiwiYXVkIjpbInNiLWhjLWNhbmFyeS1hcGlnYXRld2F5LWhhbmEtY2xvdWQhYjkxNDgiLCJ1YWEiXX0.59T6n0Jo86ilq3p0gn0HQAeoaIr_uqtD9mMn-w0Psb0UkzPbArVaAp_LG76ew1A4ZyzzD_JShU1mW-322CoGEdQGcxsQ_H9lzMqYHhcnShqX4WJ5HL2MFywJBJq65NQ71EuQKG2INk3Kzy5Z-P0DRsF36_7J_FM-Xrl8IF9roYcwly307bmymApwKurxYJaz4TJDYqLUIW_OOFKZy03HOJ0MHk60MuPgQ3AtN9ujxv2F6_9At5Ftdy97zifMyaRBpbIPGfb97XcEuTOK67A2EhviJlyS2icM08Gtfg_TFE_JDFkPXcTn2S-bKQK1I3dQ5tkzt1nFQ_zX1RXRl_C09Q"

    # Your RSA public key, can be in PEM format
    public_key = """
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA8+rDuwxDsS/fRb1MBYBI
2et+zJJAOTpkn6ihiFRR2A9Wfplk+uLTJZxIFmP4+XfYWcCUYjnCN6SzDLqYNCGt
QkV514MS6VfFRO5p2NDOlhZgCF0D5i2/lEes7cHHXaIH37kufP7ABd0WsmxfG/Yd
yKzIRag/IJgwszk/Sanv+4aaKyOBdlb8tmrPyXc0JWRtNcu9Gs9OsH++Wf8NuNAk
Ueiey/wLa/6XWS/xiqVHKKAi+8Dn8enDDrcYdjDJpSHxyxH8gNIdH1xISY5SIoKZ
7CRAkuCq+yZySmg00JcO+9jCh2JD2f3tsmTSLkjZ/4ngPUrtQ7vG8qtLisPmlmPr
/QIDAQAB
-----END PUBLIC KEY-----
"""

    # Verify the JWT
    decoded = verify_jwt_rs256(token, public_key)
    if decoded:
        print(f"Decoded JWT: {decoded}")
