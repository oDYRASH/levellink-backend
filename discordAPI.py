import requests, json


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