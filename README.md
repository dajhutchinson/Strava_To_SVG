# GPS to SVG
Generate svg images of plots from data stored in *GPX* and *TCX* files.

RapidTables have a useful tool for visualising svg plots [Link](https://www.rapidtables.com/web/tools/svg-viewer-editor.html)

# Contents
 * [Results](#Results)
  * [Route Plot](#Route)
  * [Elevation Profile Plot](#Elevation Profile)
  * [Animated Histogram](#Animated Histogram)
 * [Usage Guide](#Usage Guide)
  * [Installation](#Installation)
  * [Getting Data](#Getting Data)
    * [GPS Data to DataFrame](#GPS Data to DataFrame)
    * [GPSEvaluator](#GPSEvaluator)
  * [Making Plots](#Making Plots)
    * [Route Plot](# Route SVG)
    * [Elevation Profile Plot](# Elevation Profile SVG)
    * [Histogram SVG (Not Animated)](#Histogram SVG (Not Animated))
    * [Histogram SVG (Animated)](#Histogram SVG (Animated))
 * [Reference](#Reference)
  * [GPX Files](#GPX file)
  * [TCX Files](#TCX file)
  * [Metadata](#Metadata)

# Results

## Route
Plot of the route using GPS data.
![Route](route.gif)

## Elevation Profile
Plot of the elevation along the route using GPS data.
![Elevation](elevation.gif)

## Animated Histogram
Animated histogram of split times. In this example splits are added 1km at a time.
![Animated Hist](animated_hist.gif)

# Usage Guide

## Installation
Install requirements using
`pip install -r requirements.txt`

## Getting Data

### GPS Data to DataFrame
1. Pass path for gps file to `GPSReader.read()`
2. This returns two objects:
  - `list(dict)`, the parsed gps data.
  - `dict`, the parsed metadata.
3. Pass the `list(dict)` to `GPSReader.data_to_dataframe()` to convert it to a `pd.DataFrame`.

### GPSEvaluator
`GPSEvaluator` offers several methods for elevating the data parsed by `GPSReader`. Each method takes the dataframe generated [above](#GPS Data to DataFrame) as a parameter, along with certain specifiers.
| Method Name | Description | Other Parameters |
|-------------|-------------|------------------|
| `time_to_seconds` | Calculates the number of seconds since the first reading, for all readings |  |
| `distance` | Calculates the euclidean distance between consecutive pairs of readings |  |
| `cumm_distance` | Calculates the distance covered by route up to each reading |  |
| `splits` | Calculates the time, in seconds, to complete each `split_dist` | `split_dist (int)` (default=`1000`) |
| `split_markers` | Returns the gps co-ordinates of each time `split_dist` is completed | `split_dist (int)` (default=`1000`) |
| `important_points` | Returns the gps co-ordinates for specified notable positions on route | `name (str)` taking `"start"` or `"finish"` |
| `split_histogram_data` | Counts the number of readings in given split speed intervals | `bin_width (int)` (default=`10`); `sampling_dist (int)` (default=`100`); `clean (bool)` (default=`False`) |
| `split_histogram_data_per_km` | Counts the number of readings, per km, in given split speed intervals | `bin_width (int)` (default=`10`); `sampling_dist (int)` (default=`100`); `clean (bool)` (default=`False`) |

## Making Plots

### Route SVG
1. Parse `pd.DataFrame` of gps file you want to plot.
2. Pass dataframe to `SVGMaker.generate_route_svg` with **optional** parameters:
  - `output_name` (`str`), name and relative path to where to output resulting file. (don't include extension!)
  - `route_styler` (`SVGMaker.RouteStyler`) styler for plot.
  - `html` (`bool`) whether to generate a html file which includes the generated plot. (This will be saved at `_output_name_.html`)
3. A `dict` will be returned which specifies which files where created.
  - `None` is returned if the dataframe included insufficient data.

### Elevation Profile SVG
1. Parse `pd.DataFrame` of gps file you want to plot.
2. Pass dataframe to `SVGMaker.generate_elevation_svg` with **optional** parameters:
  - `output_name` (`str`), name and relative path to where to output resulting file. (don't include extension!)
  - `elevation_styler` (`SVGMaker.ElevationStyler`) styler for plot.
  - `html` (`bool`) whether to generate a html file which includes the generated plot. (This will be saved at `_output_name_.html`)
3. A `dict` will be returned which specifies which files where created.
  - `None` is returned if the dataframe included insufficient data.

### Histogram SVG (Not Animated)
1. Parse `pd.DataFrame` of gps file you want to plot.
2. Pass dataframe to `SVGMaker.generate_histogram` with **optional** parameters:
  - `output_name` (`str`), name and relative path to where to output resulting file. (don't include extension!)
  - `hist_styler` (`SVGMaker.HistogramStyler`) styler for plot.
  - `html` (`bool`) whether to generate a html file which includes the generated plot. (This will be saved at `_output_name_.html`)
3. A `dict` will be returned which specifies which files where created.
  - `None` is returned if the dataframe included insufficient data.

### Histogram SVG (Animated)
1. Parse `pd.DataFrame` of gps file you want to plot.
2. Pass dataframe to `SVGMaker.generate_animated_histogram` with **optional** parameters:
  - `output_name` (`str`), name and relative path to where to output resulting file. (don't include extension!)
  - `hist_styler` (`SVGMaker.HistogramStyler`) styler for plot.
  - `html` (`bool`) whether to generate a html file which includes the generated plot. (This will be saved at `_output_name_.html`)
3. A `dict` will be returned which specifies which files where created.
  - `None` is returned if the dataframe included insufficient data.

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
