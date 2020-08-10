"""
    TODO
    Histogram of splits (with animation)
    Styling
    Check scaling
    Animation
    Distance Marker
    Legend?
"""
from GPSReader import GPSReader
from GPSEvaluator import GPSEvaluator
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

    """
    PLOTS
    """
    # generate a path of the route taken
    def generate_route_svg(df,output_name="route"):
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
    def generate_elevation_svg(df,output_name="elevation"):
        BORDER=10
        COLOUR="#214025"

        # check data exists
        if "cumm_distance" in df: elevation=df[["cumm_distance","altitude"]].copy(deep=True) # data to be used
        elif ("position_lat" in df.columns) and ("position_lon" in df.columns):
            df["cumm_distance"]=GPSEvaluator.cumm_distance(df)
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

    def make_histogram(data:pd.Series,output_name="hist"):
        # define bar params
        height=min(int(100/data.size),10)-2
        y_max=2+(data.size*(2+height))

        # calculate bar widths
        min_val=data.min(); max_val=data.max()
        widths=data.copy().apply(lambda x:int((70*(x-min_val))/(max_val-min_val)))

        svg_file=open(output_name+".svg","w+")
        svg_file.write('<svg xmlns="http://www.w3.org/2000/svg" viewbox="0 0 140 {}" width="100%" height="100%" version="1.1">\n'.format(y_max))

        # add axes
        x=2; count=0
        for ind,width in widths.iteritems():
            y=2+count*(2+height)
            svg_file.write('<rect class="hist_bar" x="{}" y="{}" width="{}" height="{}" '.format(x,y,width,height)) # dimensions
            svg_file.write('style="fill:#214025;stroke-width:1;stroke:#547358">') # styling
            svg_file.write('</rect>\n')
            count+=1

            if (width!=0):
                svg_file.write('<text class="hist_text" x="{}" y="{}" dy="{}" style="font-size:{}px">{}</text>\n'.format(width+3,y,height-1,height,ind))

        # add axes
        svg_file.write('<line class="hist_axis" x1="{}" y1="0" x2="{}" y2="{}" stroke-linecap="square" style="stroke:#000;stroke-width:1"></line>\n'.format(x,x,y_max)) # y axis
        svg_file.write("</svg>")

        svg_file.close()

if __name__=="__main__":
    reader=GPSReader()
    data,metadata=reader.read("examples\Run_from_Exam.tcx")
    df=reader.data_to_dataframe(data)

    # SVGMaker.generate_route_svg(df)
    # SVGMaker.generate_elevation_svg(df)

    hist_data=GPSEvaluator.split_histogram_data(df,clean=True)
    SVGMaker.make_histogram(hist_data)
