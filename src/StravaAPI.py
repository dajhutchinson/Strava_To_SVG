import requests
import pandas as pd

def get_full_activity_list(access_token:str,per_page=50,before=None,after=None) -> [dict]:
    """
    SUMMARY
    fetch data from strava API for all activities completed by user.

    PARAMETERS
	access_token (str): user's access token. See ACQUIRING_ACCESS_TOKEN.md for instructions of how to acquire.
    per_page (int): number of activities fetched with each request. (Has no affect on outcome). (default=50)
    before (int): only fetch activities before this date (in epoch time). Pass `None` for no restriction. (default=None)
    after (int): only fetch activities after this date (in epoch time). Pass `None` for no restriction. (default=None)

    RETURNS
	list(dict): details from fetched activities
    """
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

def activity_fundamentals(activity_details:dict) -> dict:
    """
    SUMMARY
    reduced activity details to only key information.

    PARAMETERS
	activity_details (dict): details activity fetched from strava's api.

    RETURNS
	dict: simplified details ["id","start_date_local","name","distance","elapsed_time","moving_time","total_elevation_gain","type"]
    """
    fundamentals=["id","start_date_local","name","distance","elapsed_time","moving_time","total_elevation_gain","type",]
    fundamental_details={f:activity_details[f] for f in fundamentals if f in activity_details}
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
