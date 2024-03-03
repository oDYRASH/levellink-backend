import requests, json
import settings

def getDiscordUser(token):
    
    try:
        if token:
            user_data = requests.get('https://discord.com/api/v6/users/@me', headers={
                'Authorization': f'Bearer {token}'
            }).json()
            user_data['connections'] = [{'type': conn['type'], 'name': conn['name']} for conn in \
                requests.get('https://discord.com/api/users/@me/connections', headers={
                    'Authorization': f'Bearer {token}'
                }).json()]
            return user_data
        else:
            raise ValueError("Access token not found in Discord API response.")
    except (KeyError, json.JSONDecodeError) as e:
        raise ValueError(f"Error processing Discord API response: {e}")
    
def exchange_code(code):
    response = requests.post(
        'https://discord.com/api/oauth2/token',
        data= {
            'client_id': settings.SOCIAL_AUTH_DISCORD_KEY,
            'client_secret': settings.SOCIAL_AUTH_DISCORD_SECRET,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': settings.SOCIAL_AUTH_DISCORD_REDIRECT_URI + '/authUser',
            'scope': 'identify+connections',
        },
        headers= {'Content-Type': 'application/x-www-form-urlencoded'}
    )

    if response.status_code != 200:
        return None
    
    try:
        access_token = response.json().get('access_token')
        if access_token:
            user_data = requests.get('https://discord.com/api/v6/users/@me', headers={
                'Authorization': f'Bearer {access_token}'
            }).json()
            user_data['connections'] = [{'type': conn['type'], 'name': conn['name']} for conn in \
                requests.get('https://discord.com/api/users/@me/connections', headers={
                    'Authorization': f'Bearer {access_token}'
                }).json()]
            return user_data
        else:
            raise ValueError("Access token not found in Discord API response.")
    except (KeyError, json.JSONDecodeError) as e:
        raise ValueError(f"Error processing Discord API response: {e}")
    