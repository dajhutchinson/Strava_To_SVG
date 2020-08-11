"""
    TODO
    Animate hist of splits (show distributioin of split for each km)
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

    def __seconds_to_time_str(seconds):
        secs=seconds%60
        mins=seconds//60
        return "{}:{}".format(mins,"0"+str(secs) if secs<10 else secs)

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

    # makes horizontal histogram using data from GPSEvaluator.split_histogram_data()
    def make_histogram(data:pd.Series,output_name="hist"):
        # define bar params
        height=min(int(100/data.size),10)-2
        y_max=2+(data.size*(2+height))

        # calculate bar widths
        min_val=data.min(); max_val=data.max()
        widths=data.copy().apply(lambda x:int((70*(x))/max_val))

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

    # makes animated horizontal histogram using data from GPSEvaluator.split_histogram_data_per_km()
    # animation_length:seconds
    def make_animated_histogram(df:pd.DataFrame,animation_length=10,output_name="animated_hist",html=False):
        # TODO - add text
        x_axis=10 # x value of axis
        height=min(int(100/df.shape[0]),10)-2
        y_max=2+(df.shape[0]*(2+height))

        min_row_sum=df.sum(axis=1).min()
        max_row_sum=df.sum(axis=1).max()
        max_bar_width=100-x_axis
        widths=df.copy().apply(lambda x:(max_bar_width*x)/max_row_sum).astype(int)

        svg_file=open(output_name+".svg","w+")
        svg_file.write('<svg xmlns="http://www.w3.org/2000/svg" viewbox="0 0 100 {}" width="100%" height="100%" version="1.1">\n'.format(y_max))

        x={val:x_axis for val in widths.index}
        for col in widths.columns:
            column=widths[col]
            count=0
            for split,width in column.iteritems():
                y=2+count*(2+height)
                if (width!=0):
                    svg_file.write('\t<rect class="hist_bar bar_{}" x="{}" y="{}" width="{}" height="{}" '.format(col,x[split],y,width,height)) # dimensions
                    x[split]+=width
                    svg_file.write('style="fill:#214025">') # styling
                    svg_file.write('</rect>\n')
                count+=1

        count=0
        for index,row in widths.iterrows():
            y=2+count*(2+height); count+=1
            label=SVGMaker.__seconds_to_time_str(index)
            if (row.sum()!=0):
                svg_file.write('<text class="hist_text" x={} y={} dy={} text-anchor="end" style="font-size:{}px">{}</text>\n'.format(x_axis-1,y,height-1,height,label))

        svg_file.write('\t<line class="hist_axis" x1="{}" y1="0" x2="{}" y2="{}" stroke-linecap="square" style="stroke:#000;stroke-width:1"></line>\n'.format(x_axis,x_axis,y_max)) # y axis
        svg_file.write("</svg>")

        svg_file.close()

        # extras
        frame_length=round(animation_length/widths.shape[1],1)
        SVGMaker.__generate_css_for_animated_histogram(widths.columns,frame_length=frame_length,output_name=output_name)
        if (html): SVGMaker.__generate_html_for_svg(output_name+".svg",output_name+".css",output_name)

        return True

    # creates csv file which adds animation to histogram
    def __generate_css_for_animated_histogram(col_labels,frame_length=1,output_name="animated_hist"):
        frame_length=max(frame_length,.1)
        css_file=open(output_name+".css","w+")
        css_file.write(".hist_text {\n\tfont-family:Arial\n}\n")
        css_file.write(".hist_bar {\n\topacity: 0;\n}\n\n@keyframes opacity {\n\t0% {opacity: 0}\n\t100% {opacity: 1}\n}\n\n")

        count=0
        for col in col_labels:
            css_file.write(".bar_{} {{\n\tanimation: linear {}s opacity forwards;\n".format(col,frame_length))
            if (count!=0): css_file.write("\tanimation-delay: {}s\n".format(count*frame_length))
            css_file.write("}\n\n")
            count+=1

        css_file.close()
        return True

    # generates html file for checking svg
    def __generate_html_for_svg(svg_file_name,css_file_name=None,output_name="example"):
        html_file=open(output_name+".html","w+")
        html_file.write('<html>\n')
        if css_file_name is not None:
            html_file.write('\t<head>\n\t\t<link rel="stylesheet" type="text/css" href={}>\n\t</head>\n'.format(css_file_name))
        html_file.write('\t<body>\n')

        with open(svg_file_name,"r") as svg_file:
            for line in svg_file:
                html_file.write("\t"+line)

        html_file.write("\t</body>\n</html>")

if __name__=="__main__":
    reader=GPSReader()
    data,metadata=reader.read("examples\example_run.gpx")
    df=reader.data_to_dataframe(data)

    # SVGMaker.generate_route_svg(df)
    # SVGMaker.generate_elevation_svg(df)

    hist_data=GPSEvaluator.split_histogram_data(df,clean=True)
    SVGMaker.make_histogram(hist_data)

    hist_data_per_km=GPSEvaluator.split_histogram_data_per_km(df,clean=True)
    SVGMaker.make_animated_histogram(hist_data_per_km,html=True,animation_length=3)
