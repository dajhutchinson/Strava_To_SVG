# strava_to_svg
Uses the gps data from GPX or TCX files to generate svg images of the route and profile.

RapidTables have a useful tool for visualising svg plots [Link](https://www.rapidtables.com/web/tools/svg-viewer-editor.html)

# Results

## Animated Histogram
Animated histogram of split times. In this example splits are added 1km at a time.
![Animated Hist](animated_hist.gif)

## Route
Plot of the route using GPS data.
![Route](route.gif)

## Elevation
Plot of the elevation along the route using GPS data.
![Elevation](elevation.gif)

## Installation
Install requirements using
`pip install -r requirements.txt`

# Reference

## GPX file
The following fields are available from a `.gpx` file after it is parsed by `GPSReader.read()`.
| field name | type | description |
|------------|------|-------------|
| `position_lat` | `float` | latitude position |
| `position_lon` | `float` | longitude position |
| `altitude` | `float` | altitude in metres |
| `time` | `datetime.datetime` | time and date of reading |
| `hr` | `int` | heart rate (not in all file) |

## TCX file
The following fields are available from a `.tcx` file after it is parsed by `GPSReader.read()`.
| field name | type | description |
|------------|------|-------------|
| `position_lat` | `float` | latitude position |
| `position_lon` | `float` | longitude position |
| `altitude` | `float` | altitude in metres |
| `time` | `datetime.datetime` | time and date of reading |
| `distance_to_point` | `float` | distance covered on route up to this reading (in metres) |
| `hr` | `int` | heart rate (not in all file) |

## Metadata
The following metadata is available from both `.tcx` and `.gpx` files parsed by `GPSReader.read()`.
| field name | type | description |
|------------|------|-------------|
| `sport` | `str` | name of sport activity represents |
| `date` | `datetime.datetime` | date on which activity occurred |
