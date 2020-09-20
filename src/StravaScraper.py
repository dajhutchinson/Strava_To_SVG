"""
e.g.
https://www.strava.com/activities/4030142544/export_gpx
https://www.strava.com/activities/4030142544/export_tcx
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_authentication(session:requests.Session) -> (str,str):
    """
    SUMMARY
    get utf8 and authentication token to enable login

    PARAMETERS
	session (requests.Session): session you want to log in

    RETURNS
	str: utf8 encoding value
    str: authentication token for session
    """
    response=session.get("https://www.strava.com/login",verify=None,allow_redirects=True)

    # parse utf8 and token
    soup=BeautifulSoup(response.content,'lxml')
    utf8=soup.find_all('input',{'name':'utf8'})[0].get('value').encode('utf-8')
    token=soup.find_all('input',{'name':'authenticity_token'})[0].get('value')

    return utf8,token

def generate_login_data(session:requests.Session,email:str,password:str,utf8=None,token=None) -> dict:
    """
    SUMMARY
    generate a dictionary with details to login

    PARAMETERS
	session (requests.Session): session you want to log in
    email (str): account's email
    password (str): account's password
    utf8 (str): utf8 value for login session. If `None` is passed then the value will be fetched. (default=None)
    token (str): authentication token value for login session. If `None` is passed then the value will be fetched. (default=None)

    RETURNS
	dict: details to use for StravaScraper.login
    """
    if (utf8 is None) or (token is None):utf8,token=get_authentication(session)
    login_data={'utf8':utf8,'authenticity_token':token,'plan':"",'email':email,'password':password}
    return login_data

def login(session:requests.Session,login_data:dict) -> bool:
    """
    SUMMARY
    log session into strava

    PARAMETERS
	session (requests.Session): session to log in
    login_data (dict): details to log in. Generated by StravaScraper.generate_login_data

    RETURNS
	type: description
    """
    response=session.post("https://www.strava.com/session",data=login_data)
    if (response.status_code==302) and (response.headers['Location']=="https://www.strava.com/login"):return False
    else:return True

def download_activity_file(session:requests.Session,activity_id:str,output_name="downloaded_file",output_path="",file_type="gpx") -> int:
    """
    SUMMARY
    download gps file for activity (gpx or tcx).
    NOTE session must already be logged in.

    PARAMETERS
	session (requests.Session): logged in session.
    activity_id (str): id of strava activity to download
    output_name (str): name for downloaded file. (default=`downloaded_file`)
    output_path (str): path to directory for downloaded file. (default=``)
    file_type (str): type of file to download "gpx" or "tcx". (default=`gpx`)

    RETURNS
	int: stratus code of request
    """
    if file_type not in ["gpx","tcx"]:return -1
    response=session.get("https://www.strava.com/activities/{}/export_{}".format(activity_id,file_type),verify=None,allow_redirects=False)

    if (output_name[-4]!="."+file_type): output_name+="."+file_type
    open("{}{}".format(output_path,output_name),"wb").write(response.content)
    return response.status_code

if __name__=="__main__":
    email=""
    password=""

    session=requests.Session()
    login_data=generate_login_data(session,email,password)
    login(session,login_data)
    print("Logged In")
    # download_activity_file(session,"4030142544")
