"""
    TODO
    Elevation Plot
    Styling
    Check scaling
    Animation
    Distance Marker
    Legend?
"""
from geopy.distance import geodesic
from GPSFileReader import GPSFileReader
from math import ceil
import pandas as pd

class SVGMaker:

    """
    MANIPULATE DATA
    """
    def __scale_with_border(v,min_v,max_v,scale=1,border=0):
        range=1000-2*border
        return int(border+range*scale*(v-min_v)/(max_v-min_v))

    def __scale_elevation(v,min_v,max_v,border=0):
        scale_range=min(1000,4*(max_v-min_v))
        return border+scale_range-int(scale_range*(v-min_v)/(max_v-min_v))

    # returns distance covered between pair of (lat,lon) points
    # p=(lat,lon)
    def __distance_lat_lon(self,p1,p2) -> float:
        return geodesic(p1,p2).meters

    # return pd.Series of distance between consequtive lat,lon points
    def distance(self,df:pd.DataFrame) -> pd.Series:
        if ("position_lat" in df.columns) and ("position_lon" in df.columns):
            lat_lon=df[["position_lat","position_lon"]].copy()
            prev_lat_lon=pd.concat([lat_lon.head(1).copy(),lat_lon.iloc[:-1,:].copy()],ignore_index=True)
            #print(prev_lat_lon["position_lat"])
            lat_lon["prev_lat"]=prev_lat_lon["position_lat"]
            lat_lon["prev_lon"]=prev_lat_lon["position_lon"]

            lat_lon["distance"]=lat_lon.apply(lambda x:self.__distance_lat_lon((x["position_lat"],x["position_lon"]),(x["prev_lat"],x["prev_lon"])),axis=1)
            return lat_lon["distance"]
        return None

    # calculate cummulative distance from start to point
    def cumm_distance(self,df:pd.DataFrame) -> pd.Series:

        if ("distance" in df.columns): dists=df["distance"]
        elif ("position_lat" in df.columns) and ("position_lon" in df.columns): dists=self.distance(df)
        else: return None # not enough data

        return dists.cumsum().apply(lambda x:round(x,2))

    # returns time as number of seconds from start
    def time_to_seconds(self,df:pd.DataFrame) -> pd.Series:
        if "time" in df:
            times=df["time"]
            start_time=times[0]
            return times.apply(lambda x:(x-start_time).seconds).astype(int)
        else: # not enough data
            return None

    """
    PLOTS
    """
    # generate a path of the route taken
    def generate_route_svg(self,df,output_name="route"):
        BORDER=10
        COLOUR="#214025"
        lat_lon_data=df[["position_lat","position_lon"]].copy()

        min_lat=lat_lon_data["position_lat"].min(); max_lat=lat_lon_data["position_lat"].max()
        min_lon=lat_lon_data["position_lon"].min(); max_lon=lat_lon_data["position_lon"].max()

        lat_diff=max_lat-min_lat
        lon_diff=max_lon-min_lon
        max_diff=max(lon_diff,lat_diff)

        lat_lon_data["scaled_lat"]=lat_lon_data["position_lat"].apply(SVGMaker.__scale_with_border,min_v=min_lat,max_v=max_lat,scale=lat_diff/max_diff,border=BORDER)
        lat_lon_data["scaled_lat"]=lat_lon_data["scaled_lat"].apply(lambda x: BORDER+ceil(1000*(lat_diff/max_diff))-x)
        lat_lon_data["scaled_lon"]=lat_lon_data["position_lon"].apply(SVGMaker.__scale_with_border,min_v=min_lon,max_v=max_lon,scale=lon_diff/max_diff,border=BORDER).astype(int)

        lat_lon_data["point_str"]=lat_lon_data.apply(lambda row:"{},{}".format(str(int(row["scaled_lon"])),str(int(row["scaled_lat"]))),axis=1)

        # points=[(BORDER+__scale_0_1000(datum["position_lon"],metadata["min_lon"],metadata["max_lon"],lon_diff/max_diff),BORDER+ceil(1000*(lat_diff/max_diff))-__scale_0_1000(datum["position_lat"],metadata["min_lat"],metadata["max_lat"],lat_diff/max_diff)) for datum in data[lap_name]]
        point_str=" ".join(lat_lon_data["point_str"].tolist())

        # write to file
        style_str='fill="none" stroke-width="5" stroke-linejoin="round" stroke="'+COLOUR+'"'

        # content
        svg_file=open(output_name+".svg","w+")
        svg_file.write('<svg xmlns="http://www.w3.org/2000/svg" viewbox="0 0 {} {}" width="100%" height="100%" version="1.1">\n'.format(lat_lon_data["scaled_lon"].max()+BORDER,lat_lon_data["scaled_lat"].max()+BORDER))
        svg_file.write('<path class="route" {} d="M{}" ></path>\n'.format(style_str,point_str))
        svg_file.write("</svg>")

        svg_file.close()
        return True

    # generate an svg path of the elevation against distance
    def generate_elevation_svg(self,df,output_name="elevation"):
        BORDER=10
        COLOUR="#214025"

        # check data exists
        if "cumm_distance" in df: elevation=df[["cumm_distance","altitude"]].copy(deep=True) # data to be used
        elif ("position_lat" in df.columns) and ("position_lon" in df.columns):
            df["cumm_distance"]=self.distance(df)
            elevation=df[["cumm_distance","altitude"]].copy(deep=True)
        else: return None # not enough data

        # scale values for plot
        min_alt=elevation["altitude"].min(); max_alt=elevation["altitude"].max()
        min_dist=elevation["cumm_distance"].min(); max_dist=elevation["cumm_distance"].max()

        elevation["scaled_altitude"]=elevation["altitude"].apply(lambda x:SVGMaker.__scale_elevation(x,min_alt,max_alt,border=BORDER))
        elevation["scaled_distance"]=elevation["cumm_distance"].apply(lambda x:SVGMaker.__scale_with_border(x,min_dist,max_dist,border=BORDER))

        elevation["point_str"]=elevation.apply(lambda row:"{},{}".format(str(int(row["scaled_distance"])),str(int(row["scaled_altitude"]))),axis=1)

        # content
        PLINTH=min(30,min_alt) # PLINTH is min alt above sea or 30m
        bottom_of_path=int(min(1000-BORDER,elevation["scaled_altitude"].max()+PLINTH))
        point_str=" ".join(elevation["point_str"].tolist())
        point_str="{},{} ".format(elevation["scaled_distance"].min(),bottom_of_path)+point_str+" {},{}".format(elevation["scaled_distance"].max(),bottom_of_path)
        style_str='fill="none" stroke-width="5" stroke-linejoin="round" stroke="'+COLOUR+'"'

        # write to file
        svg_file=open(output_name+".svg","w+")
        svg_file.write('<svg xmlns="http://www.w3.org/2000/svg" viewbox="0 0 {} {}" width="100%" height="100%" version="1.1">\n'.format(elevation["scaled_distance"].max()+BORDER,bottom_of_path+BORDER))
        svg_file.write('<path class="route" {} d="M{}z" ></path>\n'.format(style_str,point_str))
        svg_file.write("</svg>")
        svg_file.close()

        return True
