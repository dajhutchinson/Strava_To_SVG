"""
    TODO
    Distance Markers
    More Histograms (generalise)
"""
from GPSReader import GPSReader
from GPSEvaluator import GPSEvaluator
from math import ceil
import pandas as pd

# define style used for histograms
class HistogramStyler:

    def __init__(self,rect_colour="#214025",stroke_width=1,stroke_colour="#547358",font_size=12,font_family="arial"):
        self.rect_colour=rect_colour # fill colour of rect

        # rect border
        self.stroke_width=stroke_width
        self.stroke_colour=stroke_colour

        # text styling
        self.font_size=font_size
        self.font_family=font_family

    # string used for style tag of rect svg object
    def rect_style_str(self) -> str:
        return "fill:{};stroke-width:{};stroke:{}".format(self.rect_colour,self.stroke_width,self.stroke_colour)

    # string used for style tag of text svg object
    def text_style_str(self) -> str:
        return "font-size:{}px;font-family:{}".format(self.font_size,self.font_family)

class RouteStyler:

    def __init__(self,border_width=10,path_colour="#214025",fill_colour="none",path_width=5,path_linejoin="round",
        animated=False,animation_length=10,num_dashes=2,dash_colour="#547358",
        split_dist=None,split_marker_colour="#000",split_marker_width=5,
        start_marker=False,start_marker_colour="green",start_marker_width=5,
        finish_marker=False,finish_marker_colour="red",finish_marker_width=5):
        # image styling
        self.border_width=border_width

        self.fill_colour=fill_colour

        # path
        self.path_colour=path_colour
        self.path_width=path_width
        self.path_linejoin=path_linejoin

        # animation
        self.animated=animated
        self.animation_length=animation_length
        self.num_dashes=num_dashes
        self.dash_colour=dash_colour

        # split markers (ie mile markers)
        self.split_dist=split_dist # set to None for no markers
        self.split_marker_colour=split_marker_colour
        self.split_marker_width=split_marker_width

        # start & end markers
        self.start_marker=start_marker
        self.start_marker_colour=start_marker_colour
        self.start_marker_width=start_marker_width
        self.finish_marker=finish_marker
        self.finish_marker_colour=finish_marker_colour
        self.finish_marker_width=finish_marker_width

    def path_style_str(self) -> str:
        return 'fill="{}" stroke-width="{}" stroke-linejoin="{}" stroke="{}"'.format(self.fill_colour,self.path_width,self.path_linejoin,self.path_colour)

    def animated_path_style_str(self) -> str:
        return 'fill="{}" stroke-width="{}" stroke-linejoin="{}" stroke="{}"'.format("none",self.path_width,self.path_linejoin,self.dash_colour)

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
    """ROUTE"""
    # generate a path of the route taken
    def generate_route_svg(df,output_name="route",route_styler=None,html=False) -> str:
        if route_styler is None: route_styler=RouteStyler()

        lat_lon_data=df[["position_lat","position_lon"]].copy()

        min_lat=lat_lon_data["position_lat"].min(); max_lat=lat_lon_data["position_lat"].max()
        min_lon=lat_lon_data["position_lon"].min(); max_lon=lat_lon_data["position_lon"].max()

        lat_diff=max_lat-min_lat
        lon_diff=max_lon-min_lon
        max_diff=max(lon_diff,lat_diff)

        lat_lon_data["scaled_lat"]=lat_lon_data["position_lat"].apply(SVGMaker.__scale_with_border,min_v=min_lat,max_v=max_lat,scale=lat_diff/max_diff,border=route_styler.border_width)
        lat_lon_data["scaled_lat"]=lat_lon_data["scaled_lat"].apply(lambda x: route_styler.border_width+ceil(1000*(lat_diff/max_diff))-x)
        lat_lon_data["scaled_lon"]=lat_lon_data["position_lon"].apply(SVGMaker.__scale_with_border,min_v=min_lon,max_v=max_lon,scale=lon_diff/max_diff,border=route_styler.border_width).astype(int)

        lat_lon_data["point_str"]=lat_lon_data.apply(lambda row:"{},{}".format(str(int(row["scaled_lon"])),str(int(row["scaled_lat"]))),axis=1)

        point_str=" ".join(lat_lon_data["point_str"].tolist())

        # content
        svg_file=open(output_name+".svg","w+")
        svg_file.write('<svg xmlns="http://www.w3.org/2000/svg" viewbox="0 0 {} {}" width="100%" height="100%" version="1.1">\n'.format(lat_lon_data["scaled_lon"].max()+route_styler.border_width,lat_lon_data["scaled_lat"].max()+route_styler.border_width))
        svg_file.write('<path class="route" {} d="M{}" ></path>\n'.format(route_styler.path_style_str(),point_str))

        # add animation
        if (route_styler.animated):
            svg_file.write('<path class="animated_route" {} d="M{}" ></path>\n'.format(route_styler.animated_path_style_str(),point_str)) # path to be animated
            css_file_name=SVGMaker.__generate_css_for_animated_route(route_styler=route_styler,output_name=output_name)
            js_file_name=SVGMaker.__generate_js_for_animated_route(route_styler=route_styler,output_name=output_name)
        else:
            css_file_name=None
            js_file_name =None

        if (route_styler.split_dist is not None):
            split_coords=GPSEvaluator.split_markers(df,route_styler.split_dist)

            # scale to canvas
            split_coords["scaled_lat"]=split_coords["position_lat"].apply(SVGMaker.__scale_with_border,min_v=min_lat,max_v=max_lat,scale=lat_diff/max_diff,border=route_styler.border_width)
            split_coords["scaled_lat"]=split_coords["scaled_lat"].apply(lambda x: route_styler.border_width+ceil(1000*(lat_diff/max_diff))-x)
            split_coords["scaled_lon"]=split_coords["position_lon"].apply(SVGMaker.__scale_with_border,min_v=min_lon,max_v=max_lon,scale=lon_diff/max_diff,border=route_styler.border_width).astype(int)

            for _,row in split_coords.iterrows():
                svg_file.write('<circle cx="{}" cy="{}" r="{}" fill="{}" />'.format(row["scaled_lon"],row["scaled_lat"],route_styler.split_marker_width,route_styler.split_marker_colour))


        # add special markers
        range=1000-2*route_styler.border_width
        scale=lambda x,min_v,max_v,scale_factor:int(route_styler.border_width+range*scale_factor*(x-min_v)/(max_v-min_v)) # scale individual points

        if (route_styler.finish_marker):
            lat,lon=GPSEvaluator.important_points(df,name="finish")

            scaled_lat=scale(lat,min_lat,max_lat,lat_diff/max_diff)
            scaled_lat=route_styler.border_width+ceil(1000*(lat_diff/max_diff))-scaled_lat
            scaled_lon=scale(lon,min_lon,max_lon,lon_diff/max_diff)

            svg_file.write('<circle cx="{}" cy="{}" r="{}" fill="{}" />'.format(scaled_lon,scaled_lat,route_styler.finish_marker_width,route_styler.finish_marker_colour))

        if (route_styler.start_marker):
            lat,lon=GPSEvaluator.important_points(df,name="start")

            scaled_lat=scale(lat,min_lat,max_lat,lat_diff/max_diff)
            scaled_lat=route_styler.border_width+ceil(1000*(lat_diff/max_diff))-scaled_lat
            scaled_lon=scale(lon,min_lon,max_lon,lon_diff/max_diff)

            svg_file.write('<circle cx="{}" cy="{}" r="{}" fill="{}" />'.format(scaled_lon,scaled_lat,route_styler.start_marker_width,route_styler.start_marker_colour))

        svg_file.write("</svg>")
        svg_file.close()

        if (html): SVGMaker.generate_html_for_svg(svg_file_name=output_name+".svg",css_file_name=css_file_name,js_file_name=js_file_name,output_name=output_name)

        return output_name+".svg"

    """ELEVATION"""
    # generate an svg path of the elevation against distance
    def generate_elevation_svg(df,output_name="elevation",route_styler=None,html=False) -> str:
        if (route_styler is None): route_styler=RouteStyler()
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

        elevation["scaled_altitude"]=elevation["altitude"].apply(lambda x:SVGMaker.__scale_elevation(x,min_alt,max_alt,border=route_styler.path_width))
        elevation["scaled_distance"]=elevation["cumm_distance"].apply(lambda x:SVGMaker.__scale_with_border(x,min_dist,max_dist,border=route_styler.path_width))

        elevation["point_str"]=elevation.apply(lambda row:"{},{}".format(str(int(row["scaled_distance"])),str(int(row["scaled_altitude"]))),axis=1)

        # content
        PLINTH=min(30,min_alt) # PLINTH is min alt above sea or 30m
        bottom_of_path=int(min(1000-route_styler.path_width,elevation["scaled_altitude"].max()+PLINTH))
        point_str=" ".join(elevation["point_str"].tolist())
        point_str="{},{} ".format(elevation["scaled_distance"].min(),bottom_of_path)+point_str+" {},{}".format(elevation["scaled_distance"].max(),bottom_of_path)+" {},{} ".format(elevation["scaled_distance"].min()-route_styler.path_width/2,bottom_of_path)

        # write to file
        svg_file=open(output_name+".svg","w+")
        svg_file.write('<svg xmlns="http://www.w3.org/2000/svg" viewbox="0 0 {} {}" width="100%" height="100%" version="1.1">\n'.format(elevation["scaled_distance"].max()+route_styler.path_width,bottom_of_path+route_styler.path_width))
        svg_file.write('<path class="route" {} d="M{}" ></path>\n'.format(route_styler.path_style_str(),point_str))

        if (route_styler.animated):
            svg_file.write('<path class="animated_route" {} d="M{}" ></path>\n'.format(route_styler.animated_path_style_str(),point_str))
            css_file_name=SVGMaker.__generate_css_for_animated_route(route_styler=route_styler,output_name=output_name)
            js_file_name=SVGMaker.__generate_js_for_animated_route(route_styler=route_styler,output_name=output_name)
        else:
            css_file_name=None
            js_file_name =None

        svg_file.write("</svg>")
        svg_file.close()

        if (html): SVGMaker.generate_html_for_svg(svg_file_name=output_name+".svg",css_file_name=css_file_name,js_file_name=js_file_name,output_name=output_name)

        return output_name+".svg"

    """HISTOGRAM"""
    # makes horizontal histogram using data from GPSEvaluator.split_histogram_data()
    def generate_histogram(data:pd.Series,output_name="hist",hist_styler=None,html=False) -> str:
        if hist_styler is None: hist_styler=HistogramStyler()
        # define bar params
        height=min(int(100/data.size),10)-2
        y_max=2+(data.size*(2+height))

        hist_styler.font_size=height

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
            svg_file.write('style="{}">'.format(hist_styler.rect_style_str())) # styling
            svg_file.write('</rect>\n')
            count+=1

            if (width!=0):
                svg_file.write('<text class="hist_text" x="{}" y="{}" dy="{}" style="{}">{}</text>\n'.format(width+3,y,height-1,hist_styler.text_style_str(),ind))

        # add axes
        svg_file.write('<line class="hist_axis" x1="{}" y1="0" x2="{}" y2="{}" stroke-linecap="square" style="stroke:#000;stroke-width:1"></line>\n'.format(x,x,y_max)) # y axis
        svg_file.write("</svg>")

        svg_file.close()

        if (html): SVGMaker.generate_html_for_svg(output_name+".svg",output_name=output_name)

        return output_name+".svg"

    # makes animated horizontal histogram using data from GPSEvaluator.split_histogram_data_per_km()
    # animation_length:seconds
    def generate_animated_histogram(df:pd.DataFrame,animation_length=10,output_name="animated_hist",html=False) -> str:
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
        SVGMaker.__generate_css_for_animated_histogram(widths.columns,animation_length=animation_length,output_name=output_name)
        if (html): SVGMaker.generate_html_for_svg(output_name+".svg",output_name+".css",output_name)

        return output_name+".svg"

    """
    ANIMATION
    """
    # creates csv file which adds animation to histogram
    def __generate_css_for_animated_histogram(col_labels,animation_length=10,output_name="animated_hist"):
        frame_length=max(round(animation_length/len(col_labels),1),.1)
        css_file=open(output_name+".css","w+")
        css_file.write(".hist_bar {\n\ttransition-timing-function: ease;\n\ttransition-duration: .4s;\n\topacity: 0;\n}\n\n")
        css_file.write(".hist_bar:hover {\n\ttransition-timing-function: ease;\n\ttransition-duration: .4s;\n\tfill: #547358!important\n}\n\n")
        css_file.write("@keyframes opacity {\n\t0% {opacity: 0}\n\t100% {opacity: 1}\n}\n\n")

        count=0
        for col in col_labels:
            css_file.write(".bar_{} {{\n\tanimation: linear {}s opacity forwards;\n".format(col,frame_length))
            if (count!=0): css_file.write("\tanimation-delay: {}s\n".format(count*frame_length))
            css_file.write("}\n\n")
            count+=1

        css_file.close()
        return output_name+".css"

    # creates csv file which adds css to make a dash follow the path in an infintie loop
    def __generate_css_for_animated_route(route_styler=None,output_name="animated_route"):
        if (route_styler is None): route_styler=RouteStyler()
        css_file=open(output_name+".css","w+")

        css_file.write(".animated_route {{\n\tstroke-dasharray:1000;\n\tstroke-dashoffset:1000;\n\tanimation: draw {}s linear infinite;\n}}\n\n".format(route_styler.animation_length))
        css_file.write("@keyframes draw {\n\t0%{\n\t\tstroke-dashoffset:0;\n\t}\n}")

        css_file.close()

        return output_name+".css"

    # creates js file which updates the dash offset & length so that the loop is seemless
    def __generate_js_for_animated_route(route_styler=None,output_name="animated_route"):
        if (route_styler is None): route_styler=RouteStyler()
        js_file=open(output_name+".js","w+")

        js_file.write("document.addEventListener('DOMContentLoaded', function() {{\n\tupdate_stroke_dash({});\n}});\n\n".format(route_styler.num_dashes))
        js_file.write("function update_stroke_dash(num_dashs) {\n\tvar path=document.querySelector('.animated_route');\n\tvar length=path.getTotalLength();\n\tvar dash_length=length/num_dashs;\n\tpath.style.strokeDasharray=dash_length;\n\tpath.style.strokeDashoffset=-(dash_length*2);\n}")

        js_file.close()
        return output_name+".js"

    """
    HELPERS
    """
    # generates html file for visulasing svg
    def generate_html_for_svg(svg_file_name,css_file_name=None,js_file_name=None,output_name="example"):
        html_file=open(output_name+".html","w+")
        html_file.write('<html>\n\t<head>\n')
        if css_file_name is not None:
            html_file.write('\t\t<link rel="stylesheet" type="text/css" href={}>\n'.format(css_file_name))
            html_file.write('\t\t<script src="{}"></script>\n'.format(js_file_name))
        html_file.write('\t</head>\n\t<body>\n')

        with open(svg_file_name,"r") as svg_file:
            for line in svg_file:
                html_file.write("\t"+line)

        html_file.write("\t</body>\n</html>")
        return output_name+".html"

if __name__=="__main__":
    reader=GPSReader()
    data,metadata=reader.read("examples\Liverpool_HM_1_35_01_PB_.gpx")
    df=reader.data_to_dataframe(data)

    # SVGMaker.generate_route_svg(df,html=True)
    styler=RouteStyler(animated=True,animation_length=5,num_dashes=12,split_dist=1000,start_marker=True,finish_marker=True)
    SVGMaker.generate_route_svg(df,html=True,route_styler=styler)

    # styler=RouteStyler(animated=True,animation_length=5,num_dashes=12,fill_colour="black")
    # SVGMaker.generate_elevation_svg(df,html=True,route_styler=styler)
    # SVGMaker.generate_elevation_svg(df,html=True,route_styler=styler)

    # hist_data=GPSEvaluator.split_histogram_data(df,clean=True)
    # SVGMaker.generate_histogram(hist_data)

    # hist_data_per_km=GPSEvaluator.split_histogram_data_per_km(df,clean=True)
    # SVGMaker.generate_animated_histogram(hist_data_per_km,html=True,animation_length=3)
