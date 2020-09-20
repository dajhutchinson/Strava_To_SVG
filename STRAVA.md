# STRAVA
Here is some guidance for using the files in this repo which interact with [strava](http://www.strava.com).
- `StravaAPI.py` - Provides methods which simplify interacting with (Strava's API)[http://developers.strava.com/].
- `StravaScraper.py` - Interacts directly with Strava to perform actions which the API does not, or makes unnecessarily difficult.

## `StravaAPI.py`

### Access Token
Methods which interact with people's personal account data (including ride data) require an *access token* which is specific to that user. This is different to your API tokens which can be found at  `www.strava.com/settings/api` and needs to be acquired even if         you are accessing your own account.<br/>
See [ACQUIRING_ACCESS_TOKEN.md](https://github.com/dajhutchinson/Strava_To_SVG/ACQUIRING_ACCESS_TOKEN.md) for instructions of how to acquire an *access token*

### Methods
| Method Name | Description | Parameters |
|-------------|-------------|------------|
| `get_full_activity_list` | fetch details about all activities a user has recorded on strava |<ul><li>`access_token (str)`</li><li>`per_page (int)` activities per request (default=`50`)</li><li>`before (int)` only fetch activities before this date (in epoch time).</li><li>`after (int)` only fetch activities after this date (in epoch time).</li></ul> |

## `StravaScraper.py`

### Methods
| Method Name | Description | Parameters |
|-------------|-------------|------------|
| `generate_login_data` | generate dictionary containing details required to log specific session in | <ul><li>`session (requests.Session)` session to be logged in.</li><li>`email (str)` email for Strava account</li><li>`password (str)` password for Strava account</li></ul> |
| `login` | logs in `requests.Session` to Strava | <ul><li>`session (requests.Session)` session to be logged in</li><li>`login_data (dict)` login details returned by `generate_login_data`</li></ul> |
|  |  |  |
| `download_activity_file` | download `.gpx` file for activity with `activity_id` | <ul><li>`session (requests.Session)` a logged in session</li><li>`activity_id (str)` id of activity to download</li><li>`output_name (str)` path & name for file being downloaded</li></ul> |
