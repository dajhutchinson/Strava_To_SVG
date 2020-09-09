# Acquiring Access Token

An access token is required to use certain features of the Strava API. In this project the API is used to get a list of all activities by an athlete.\
*CLIENT_ID* and *CLIENT_SECRET* are found at https://www.strava.com/settings/api.\

### 1. Authorise app
- Paste *https://www.strava.com/oauth/authorize?client_id=CLIENT_ID&redirect_uri=http://localhost&response_type=code&scope=activity:read_all* into a browser (replacing *CLIENT_ID*).
- This will redirect to a page which cannot be reached.
- From the url in the search bar copy the string from the *code* parameter.
- Use this code in place of *CODE* in step 2

### 2. Get access token
- Perform a post request to *https://www.strava.com/oauth/token?client_id=CLIENT_ID&client_secret=CLIENT_SECRET&code=CODE&grant_type=authorization_code* (replacing *CLIENT_ID*, *CLIENT_SECRET* & *CODE*).
- Copy the *access_token* parameter from the returned body.
- Use this code in place of *ACCESS_TOKEN* in *StravaAPI.py*
