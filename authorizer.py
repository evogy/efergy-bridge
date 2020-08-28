from modules.tools import logger
import json
from models.user import UserTable

_LOGGER = logger("efergy")


def generatePolicy(principalId, effect, resource):
    authResponse = {
        'principalId': principalId
    }
    if effect and resource:
        policyDocument = {
            'Version':'2012-10-17',
            'Statement':[
                {
                    'Action':'execute-api:Invoke',
                    'Effect':effect,
                    'Resource':resource
                }
            ]
        }
        authResponse['policyDocument'] = policyDocument
        return authResponse


def handler(event, context):
    
    if 'authorizationToken' not in event:
        _LOGGER.info("No auth token")
        return generatePolicy('efergyUser', 'Deny', "*")
    
    split = event['authorizationToken'].split('Bearer')
    if len(split) != 2:
        _LOGGER.info("No token in Bearer")
        return generatePolicy('efergyUser', 'Deny', "*")
    
    token = split[1].strip()
    valid_tokens = get_auth_tokens()
    if token.lower() not in valid_tokens:
        return generatePolicy('efergyUser', 'Deny', "*")
    else:
        return generatePolicy('efergyUser', 'Allow', "*")

def get_auth_tokens():

    users = UserTable()
    users = users.list()

    tokens = [t['id'] for t in users]
    return tokens

