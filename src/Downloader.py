"""
e.g.
https://www.strava.com/activities/4030142544/export_gpx
https://www.strava.com/activities/4030142544/export_tcx
"""

import requests
from bs4 import BeautifulSoup

# returns utf8 and authentication token for session
def get_authentication(session) -> (str,str):
    response=session.get("https://www.strava.com/login",verify=None, allow_redirects=True)
    soup=BeautifulSoup(response.content, 'lxml')
    utf8=soup.find_all('input',{'name': 'utf8'})[0].get('value').encode('utf-8')
    token=soup.find_all('input',{'name': 'authenticity_token'})[0].get('value')
    return utf8,token

# generate data to login to strava
def generate_login_data(session,email,password,utf8=None,token=None) -> dict:
    if (utf8 is None) or (token is None): utf8,token=get_authentication(session)
    login_data={'utf8': utf8,'authenticity_token': token,'plan': "",'email':email,'password':password}
    return login_data

# log session into strava
def login(session,login_data) -> bool:
    response=session.post("https://www.strava.com/session",data=login_data)
    if (response.status_code==302) and (response.headers['Location']=="https://www.strava.com/login"): return False
    else: return True

# download activity file (either gpx  or tcv)
def download_activity_file(session,activity_id,output_name="downloaded_file",output_path="",file_type="gpx") -> int:
    if file_type not in ["gpx","tcx"]: return -1
    response=session.get("https://www.strava.com/activities/{}/export_{}".format(activity_id,file_type),verify=None, allow_redirects=False)
    open("{}{}.{}".format(output_path,output_name,file_type),"wb").write(response.content)
    return response.status_code

email=""
password=""

session=requests.Session()
login_data=generate_login_data(session,email,password)
login(session,login_data)
download_activity_file(session,"4030142544")
