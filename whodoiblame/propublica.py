import requests

PROPUBLICA_BASE_URL = 'https://api.propublica.org/congress/v1/'


def get_district_data(api_key, state, district):
    senate_resp = requests.get(
        PROPUBLICA_BASE_URL + "members/senate/%s/current.json" % state,
        headers={'X-API-KEY': api_key}
    )

    senators = senate_resp.json()['results']

    house_resp = requests.get(
        PROPUBLICA_BASE_URL + "members/house/%s/%s/current.json" % (state, district),
        headers={'X-API-KEY': api_key}
    )

    reps = house_resp.json()['results']

    members = reps + senators
    detailed_members = []
    for member in members:
        member_resp = requests.get(
            PROPUBLICA_BASE_URL + "members/%s.json" % member['id'],
            headers={'X-API-KEY': api_key}
        )
        member_data = member_resp.json()['results'][0]
        detailed_members.append(member_data)

    return detailed_members
