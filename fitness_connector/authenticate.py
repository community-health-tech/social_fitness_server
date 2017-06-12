from fitbit.api import Fitbit
from fitness_connector.models import Account
from fitness_connector import settings as fitbit_settings
from oauthlib.oauth2.rfc6749.errors import MismatchingStateError,\
    MissingTokenError, InvalidGrantError
    
STRING_ERR_UNKNOWN = "Unknown error while authenticating"
STRING_ERR_MISSING_TOKEN = "Missing access token parameter. Please check that\
    you are using the correct client_secret"
STRING_ERR_MISMATCHED_STATE = "CSRF Warning! Mismatching state"
STRING_ERR_INVALID_GRANT = "Invalid grant"

def get_auth_url ():
    fitbit = Fitbit (
        fitbit_settings.CLIENT_ID,
        fitbit_settings.CLIENT_SECRET,
        redirect_uri = fitbit_settings.REDIRECT_URI,
        timeout = fitbit_settings.TIMEOUT,
    )
    url, _ = fitbit.client.authorize_token_url()
    return(url)
    
    
def authenticate (code):
    fitbit = Fitbit (
        fitbit_settings.CLIENT_ID,
        fitbit_settings.CLIENT_SECRET,
        redirect_uri = fitbit_settings.REDIRECT_URI,
        timeout = fitbit_settings.TIMEOUT,
    )

    response_text = None
    if code:
        try:
            fitbit.client.fetch_access_token(code)
            profile = fitbit.user_profile_get()
            credential = fitbit.client.session.token
            response_text = __create_fitbit_account(profile, credential)
        except MissingTokenError:
            response_text = STRING_ERR_MISSING_TOKEN
        except MismatchingStateError:
            response_text = STRING_ERR_MISMATCHED_STATE
        except InvalidGrantError:
            response_text = STRING_ERR_INVALID_GRANT
    else:
        response_text = STRING_ERR_UNKNOWN
        
    return response_text
    
def __create_fitbit_account (profile, credential):
    """
        Given a Profile and a credential Token, create a new Fitbit Account object
        INVARIANT: The new object does not exist in the database
    """
    if __does_user_id_exists(credential):
        return "Fitbit account has existed"
    else:
        fitbit_account = Account.objects.create(
            fullname = profile['user']['fullName'],
            user_id = credential["user_id"],
            access_token = credential["access_token"],
            refresh_token = credential["refresh_token"]
        )
        fitbit_account.set_expires_at_in_unix(credential["expires_at"])
        fitbit_account.save()
        return "Fitbit account has been created"

def __does_user_id_exists (credential):
    return Account.objects.filter(user_id = credential["user_id"]).exists()