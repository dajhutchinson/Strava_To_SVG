import requests
import pandas as pd

def get_full_activity_list(access_token,per_page=50,before=None,after=None) -> [dict]:
    url='https://www.strava.com/api/v3/athlete/activities'

    payload={"access_token":access_token,"per_page":per_page,"page":1}
    if before is not None: payload["before"]=before
    if after is not None: payload["after"]=after

    # fetch activities
    activities=[]
    while True:
        response=requests.get(url,params=payload).json()
        activities.extend(response)
        if (len(response)!=per_page):
            break # all activities collected
        payload["page"]+=1

    return activities

# extract the fundamental details from the full set of details returned from API request
def activity_fundamentals(activity_details) -> dict:
    fundamentals=["id","start_date_local","name","distance","elapsed_time","moving_time","total_elevation_gain","type",]
    fundamental_details={f:activity_details[f] for f in fundamentals}
    return fundamental_details

if __name__=="__main__":
    # access token is temporary (6 hours) so follow instructions for acquiring
    ACCESS_TOKEN=""

    activities=get_full_activity_list(ACCESS_TOKEN,per_page=100)
    activity_fundamentals=[activity_fundamentals(row) for row in activities]

    activities_df=pd.DataFrame(activities)
    activity_fundamentals_df=pd.DataFrame(activity_fundamentals)

    activities_df.to_csv("activities.csv")
    activity_fundamentals_df.to_csv("activity_fundamentals.csv")
