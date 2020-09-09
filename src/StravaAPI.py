import requests

def get_full_activity_list(access_token,per_page=50) -> [dict]:
    url='https://www.strava.com/api/v3/athlete/activities'
    payload={"access_token":access_token,"per_page":per_page,"page":1}
    activities=[]

    while True:
        response=requests.get(url,params=payload).json()
        activities.extend(response)
        if (len(response)!=per_page):
            break # all activities collected
        payload["page"]+=1

    return activities

# access token is temporary (6 hours) so follow instructions for acquiring
ACCESS_TOKEN=""
activities=get_full_activity_list(ACCESS_TOKEN,per_page=100)
print(len(activities))
for key,value in activities[0].items():
    print(key,value)
