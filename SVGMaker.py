"""
    TODO
    More Histograms (generalise)
    Multiple routes
    Colour route depending upon elevation
    Text position options (On axis, on tip of bar, in bar)
    Tool tips (title on svg rect)
"""
from GPSReader import GPSReader
from GPSEvaluator import GPSEvaluator
from math import ceil
import pandas as pd
# define style used for histograms
class HistogramStyler:

    """
    OPTIONS for animation_function:
        SVGMaker.histogram_animation_bounce
            An infinite animation where the blocks transition in and out
            var=pause_pct,reset_pct

        SVGMaker.histogram_animation_freeze
            Blocks transition in then hold
    """
    def __init__(self,animation_function,rect_colour="#214025",stroke_width=1,stroke_colour="#547358",space_between_bars=2,
                text=True,font_size=12,text_gap=None,
                font_family="arial",font_colour="#000",font_anchor="start",
                axis=True,axis_x_pos=10,axis_colour="#000",axis_width=1,
                animation_length=10,pause_pct=20,reset_pct=10):

        # rect
        self.stroke_width=stroke_width # border
        self.stroke_colour=stroke_colour
        self.rect_colour=rect_colour # fill colour of rect
        self.space_between_bars=space_between_bars

        # text styling
        self.text=text
        self.text_gap=stroke_width+1 if (text_gap is None) else text_gap # gap between text and end of bar
        self.font_size=font_size
        self.font_colour=font_colour
        self.font_family=font_family
        self.font_anchor=font_anchor

        # x value of vertical axis
        self.axis=axis
        self.axis_x_pos=axis_x_pos
        self.axis_colour=axis_colour
        self.axis_width=axis_width

        # animation
        self.animation_length=animation_length
        self.animation_function=animation_function

        # parameters for __histogram_animation_bounce
        self.pause_pct=pause_pct
        self.reset_pct=reset_pct


    # string used for style tag of rect svg object
    def rect_style_str(self) -> str:
        return "fill:{};stroke-width:{};stroke:{}".format(self.rect_colour,self.stroke_width,self.stroke_colour)

    # string used for style tag of text svg object
    def text_style_str(self) -> str:
        return "font-size:{}px;font-family:{};fill:{}".format(self.font_size,self.font_family,self.font_colour)

    # string used for style tag of axis rect
    def axis_style_str(self) -> str:
        return "stroke:{};stroke-width:{}".format(self.axis_colour,self.axis_width)

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

class ElevationStyler(RouteStyler):

    def __init__(self,plinth_height=30,
        border_width=10,path_colour="#214025",fill_colour="none",path_width=5,path_linejoin="round",
        animated=False,animation_length=10,num_dashes=2,dash_colour="#547358",
        split_dist=None,split_marker_colour="#000",split_marker_width=5,
        start_marker=False,start_marker_colour="green",start_marker_width=5,
        finish_marker=False,finish_marker_colour="red",finish_marker_width=5):
        super().__init__(border_width,path_colour,fill_colour,path_width,path_linejoin,
            animated,animation_length,num_dashes,dash_colour,
            split_dist,split_marker_colour,split_marker_width,
            start_marker,start_marker_colour,start_marker_width,
            finish_marker,finish_marker_colour,finish_marker_width)
        self.plinth_height=plinth_height

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
    def generate_route_svg(df,output_name="test/route",route_styler=None,html=False) -> dict:
        files={"svg":output_name+".svg"}

        if ("position_lat" not in df) or ("position_lon" not in df): return None # insufficient data
        lat_lon_data=df[["position_lat","position_lon"]].copy() # ensure data isn't affected

        if route_styler is None: route_styler=RouteStyler() # ensure a style is applied

        flip_y=lambda x: route_styler.border_width+ceil(1000*(lat_diff/max_diff))-x # flips y co-ord as 0 is top and 1000 is bottom
        scaling={} # store values to help with scaling
        scaling["min_lat"]=lat_lon_data["position_lat"].min(); scaling["max_lat"]=lat_lon_data["position_lat"].max() # determine range of values
        scaling["min_lon"]=lat_lon_data["position_lon"].min(); scaling["max_lon"]=lat_lon_data["position_lon"].max()
        lat_diff=scaling["max_lat"]-scaling["min_lat"]; lon_diff=scaling["max_lon"]-scaling["min_lon"]; max_diff=max(lon_diff,lat_diff)
        scaling["lat_scale"]=lat_diff/max_diff; scaling["lon_scale"]=lon_diff/max_diff # ensure scaling is good

        # path string
        point_str=SVGMaker.__route_svg_path_string(lat_lon_data,route_styler,scaling,flip_y)

        # write svg file
        svg_file=open(output_name+".svg","w+")
        svg_file.write('<svg xmlns="http://www.w3.org/2000/svg" viewbox="0 0 {} {}" width="100%" height="100%" version="1.1">\n'.format(lat_lon_data["scaled_lon"].max()+route_styler.border_width,lat_lon_data["scaled_lat"].max()+route_styler.border_width))
        svg_file.write('<path class="route" {} d="M{}" ></path>\n'.format(route_styler.path_style_str(),point_str)) # base path

        # add animation
        if (route_styler.animated):
            css_file_name,js_file_name=SVGMaker.__add_route_svg_animation(svg_file,"animated_route",route_styler,point_str,output_name)
            files["css"]=css_file_name; files["js"]=js_file_name;
        else: css_file_name=None; js_file_name =None

        # add split markers
        if (route_styler.split_dist is not None): SVGMaker.__add_route_svg_split_markers(svg_file,df,route_styler,scaling,flip_y)

        # add special markers
        if (route_styler.finish_marker): SVGMaker.__add_route_svg_special_markers("finish",route_styler.finish_marker_width,route_styler.finish_marker_colour,route_styler.border_width,svg_file,df,scaling,flip_y)
        if (route_styler.start_marker): SVGMaker.__add_route_svg_special_markers("start",route_styler.start_marker_width,route_styler.start_marker_colour,route_styler.border_width,svg_file,df,scaling,flip_y)

        # end file
        svg_file.write("</svg>")
        svg_file.close()

        # html file for previewing
        if (html):
            html_file_name=SVGMaker.generate_html_for_svg(svg_file_name=output_name+".svg",css_file_name=css_file_name,js_file_name=js_file_name,output_name=output_name)
            files["html"]=html_file_name

        return files

    # generate string for path of route
    def __route_svg_path_string(lat_lon_data,route_styler,scaling,flip_y) -> str:
        # scale gps coords to [0-1000] leaving a border
        lat_lon_data["scaled_lat"]=lat_lon_data["position_lat"].apply(SVGMaker.__scale_with_border,min_v=scaling["min_lat"],max_v=scaling["max_lat"],scale=scaling["lat_scale"],border=route_styler.border_width)
        lat_lon_data["scaled_lat"]=lat_lon_data["scaled_lat"].apply(flip_y) # flip since y increase as it goes down the page
        lat_lon_data["scaled_lon"]=lat_lon_data["position_lon"].apply(SVGMaker.__scale_with_border,min_v=scaling["min_lon"],max_v=scaling["max_lon"],scale=scaling["lon_scale"],border=route_styler.border_width).astype(int)

        # "x,y" string for each point
        lat_lon_data["point_str"]=lat_lon_data.apply(lambda row:"{},{}".format(str(int(row["scaled_lon"])),str(int(row["scaled_lat"]))),axis=1)
        point_str=" ".join(lat_lon_data["point_str"].tolist())

        return point_str

    # add animation to a route svg
    def __add_route_svg_animation(svg_file,class_name:str,route_styler:RouteStyler,point_str:str,output_name:str) -> "str,str":
        svg_file.write('<path class="{}" {} d="M{}" ></path>\n'.format(class_name,route_styler.animated_path_style_str(),point_str)) # path to be animated
        css_file_name=SVGMaker.__generate_css_for_animated_route(class_name,route_styler=route_styler,output_name=output_name) # adds animation
        js_file_name=SVGMaker.__generate_js_for_animated_route(class_name,route_styler=route_styler,output_name=output_name)   # ensures animation is seamless
        return css_file_name,js_file_name

    # add split markers to a route svg
    def __add_route_svg_split_markers(svg_file,df:pd.DataFrame,route_styler:RouteStyler,scaling,flip_y):
        split_coords=GPSEvaluator.split_markers(df,route_styler.split_dist) # get marker lat,lon positions

        # scale to canvas
        split_coords["scaled_lat"]=split_coords["position_lat"].apply(SVGMaker.__scale_with_border,min_v=scaling["min_lat"],max_v=scaling["max_lat"],scale=scaling["lat_scale"],border=route_styler.border_width).astype(int)
        split_coords["scaled_lat"]=split_coords["scaled_lat"].apply(flip_y)
        split_coords["scaled_lon"]=split_coords["position_lon"].apply(SVGMaker.__scale_with_border,min_v=scaling["min_lon"],max_v=scaling["max_lon"],scale=scaling["lon_scale"],border=route_styler.border_width).astype(int)

        for _,row in split_coords.iterrows(): # add markers
            svg_file.write('<circle cx="{}" cy="{}" r="{}" fill="{}" />'.format(row["scaled_lon"],row["scaled_lat"],route_styler.split_marker_width,route_styler.split_marker_colour))

        return svg_file

    def __add_route_svg_special_markers(marker_type:str,marker_width:int,marker_colour:str,image_border,svg_file,df:pd.DataFrame,scaling,flip_y):
        lat,lon=GPSEvaluator.important_points(df,name=marker_type)

        scaled_lat=int(SVGMaker.__scale_with_border(lat,min_v=scaling["min_lat"],max_v=scaling["max_lat"],scale=scaling["lat_scale"],border=image_border))
        scaled_lat=flip_y(scaled_lat)
        scaled_lon=int(SVGMaker.__scale_with_border(lon,min_v=scaling["min_lon"],max_v=scaling["max_lon"],scale=scaling["lon_scale"],border=image_border))

        svg_file.write('<circle cx="{}" cy="{}" r="{}" fill="{}" />'.format(scaled_lon,scaled_lat,marker_width,marker_colour))

    """ELEVATION"""
    # generate an svg path of the elevation against distance
    def generate_elevation_svg(df,output_name="test/elevation",elevation_styler=None,html=False) -> dict:
        files={"svg":output_name+".svg"}

        # check data exists
        if "cumm_distance" in df: elevation_df=df[["cumm_distance","altitude"]].copy(deep=True) # data to be used
        elif ("position_lat" in df.columns) and ("position_lon" in df.columns):
            df["cumm_distance"]=GPSEvaluator.cumm_distance(df)
            elevation_df=df[["cumm_distance","altitude"]].copy(deep=True)
        else: return None # not enough data

        if (elevation_styler is None): elevation_styler=ElevationStyler() # ensure styler exists

        # scale values for plot
        scaling={}
        scaling["min_alt"]=elevation_df["altitude"].min(); scaling["max_alt"]=elevation_df["altitude"].max()
        scaling["min_dist"]=elevation_df["cumm_distance"].min(); scaling["max_dist"]=elevation_df["cumm_distance"].max()

        # path string
        point_str,bottom_of_path=SVGMaker.__elevation_svg_path_string(elevation_df,elevation_styler,scaling)

        # write to file
        svg_file=open(output_name+".svg","w+")
        svg_file.write('<svg xmlns="http://www.w3.org/2000/svg" viewbox="0 0 {} {}" width="100%" height="100%" version="1.1">\n'.format(elevation_df["scaled_distance"].max()+elevation_styler.path_width,bottom_of_path+elevation_styler.path_width))
        svg_file.write('<path class="elevation" {} d="M{}" ></path>\n'.format(elevation_styler.path_style_str(),point_str))

        # add animation
        if (elevation_styler.animated):
            css_file_name,js_file_name=SVGMaker.__add_route_svg_animation(svg_file,"animated_elevation",elevation_styler,point_str,output_name)
            files["css"]=css_file_name; files["js"]=js_file_name
        else: css_file_name=None; js_file_name =None

        # end file
        svg_file.write("</svg>")
        svg_file.close()

        # html for preview
        if (html):
            html_file_name=SVGMaker.generate_html_for_svg(svg_file_name=output_name+".svg",css_file_name=css_file_name,js_file_name=js_file_name,output_name=output_name)
            files["html"]=html_file_name

        return files

    def __elevation_svg_path_string(elevation_df,elevation_styler,scaling):
        elevation_df["scaled_altitude"]=elevation_df["altitude"].apply(lambda x:SVGMaker.__scale_elevation(x,scaling["min_alt"],scaling["max_alt"],border=elevation_styler.path_width))
        elevation_df["scaled_distance"]=elevation_df["cumm_distance"].apply(lambda x:SVGMaker.__scale_with_border(x,scaling["min_dist"],scaling["max_dist"],border=elevation_styler.path_width))

        elevation_df["point_str"]=elevation_df.apply(lambda row:"{},{}".format(str(int(row["scaled_distance"])),str(int(row["scaled_altitude"]))),axis=1)

        # content
        plinth_height=max(0,min(30,elevation_styler.plinth_height)) # min alt above sea or defined height
        bottom_of_path=int(min(1000-elevation_styler.path_width,elevation_df["scaled_altitude"].max()+plinth_height))
        point_str=" ".join(elevation_df["point_str"].tolist())
        point_str="{},{} ".format(elevation_df["scaled_distance"].min(),bottom_of_path)+point_str+" {},{}".format(elevation_df["scaled_distance"].max(),bottom_of_path)+" {},{} ".format(elevation_df["scaled_distance"].min()-elevation_styler.path_width/2,bottom_of_path)

        return point_str, bottom_of_path

    """HISTOGRAM"""
    # makes horizontal histogram using data from GPSEvaluator.split_histogram_data()
    def generate_histogram(data:pd.Series,hist_styler=None,output_name="test/hist",html=False) -> dict:
        files={"svg":output_name+".svg"}
        if hist_styler is None: hist_styler=HistogramStyler()

        # calculate bar heights
        height=min(int(100/data.size),10)-hist_styler.space_between_bars
        y_max=hist_styler.space_between_bars+(data.size*(hist_styler.space_between_bars+height))
        hist_styler.font_size=height

        # calculate bar widths
        min_val=data.min(); max_val=data.max()
        max_bar_width=140-hist_styler.axis_x_pos-hist_styler.axis_width
        if (hist_styler.font_anchor=="start"): max_bar_width-=15
        widths=data.copy().apply(lambda x:int(max_bar_width*(x/max_val)))

        svg_file=open(output_name+".svg","w+")
        svg_file.write('<svg xmlns="http://www.w3.org/2000/svg" viewbox="0 0 140 {}" width="100%" height="100%" version="1.1">\n'.format(y_max))

        # add bars
        x_poss=SVGMaker.__add_histogram_bars(svg_file,widths,hist_styler)

        # add text
        if (hist_styler.text):
            labels=[SVGMaker.__seconds_to_time_str(val) for val in widths.index]
            SVGMaker.__add_histogram_text(svg_file,x_poss,labels,hist_styler)

        # add axis
        if (hist_styler.axis): SVGMaker.__add_histogram_axis(svg_file,hist_styler,y_max)

        # close file
        svg_file.write("</svg>")
        svg_file.close()

        if (html):
            html_file_name=SVGMaker.generate_html_for_svg(output_name+".svg",output_name=output_name)
            files["html"]=html_file_name

        return files

    # add bars to histogram
    def __add_histogram_bars(svg_file,widths:pd.DataFrame,hist_styler:HistogramStyler) -> int:
        height=min(int(100/widths.shape[0]),10)-hist_styler.space_between_bars
        count=0; x_poss=[]
        for ind,width in widths.iteritems():
            y=hist_styler.space_between_bars+count*(hist_styler.space_between_bars+height)
            svg_file.write('<rect class="hist_bar" x="{}" y="{}" width="{}" height="{}" '.format(hist_styler.axis_x_pos,y,width,height)) # dimensions
            x_poss.append(hist_styler.axis_x_pos+width+1)
            svg_file.write('style="{}">'.format(hist_styler.rect_style_str())) # styling
            svg_file.write('</rect>\n')
            count+=1
        return x_poss

    # add labels to histogram bars
    def __add_histogram_text(svg_file,x_poss:[int],labels:[str],hist_styler:HistogramStyler):
        height=min(int(100/len(x_poss)),10)-hist_styler.space_between_bars
        for i in range(len(x_poss)):
            x_pos=x_poss[i]; label=labels[i]
            y=hist_styler.space_between_bars+i*(hist_styler.space_between_bars+height)
            # add text to non-empty bars
            x_pos=x_pos+hist_styler.text_gap if (hist_styler.font_anchor=="start") else x_pos-hist_styler.text_gap
            if (x_pos!=hist_styler.axis_x_pos): svg_file.write('<text class="hist_text" x="{}" y="{}" dy="{}" text-anchor="{}" style="{}">{}</text>\n'.format(x_pos,y,height-1,hist_styler.font_anchor,hist_styler.text_style_str(),label))

    def __add_histogram_axis(svg_file,hist_styler:HistogramStyler,y_max:int):
        svg_file.write('<line class="hist_axis" x1="{}" y1="0" x2="{}" y2="{}" stroke-linecap="square" style="{}"></line>\n'.format(hist_styler.axis_x_pos,hist_styler.axis_x_pos,y_max,hist_styler.axis_style_str())) # y axis

    """ANIMATED HISTOGRAM"""
    # makes animated horizontal histogram using data from GPSEvaluator.split_histogram_data_per_km()
    # animation_length:seconds
    def generate_animated_histogram(df:pd.DataFrame,hist_styler=None,output_name="test/animated_hist",html=False) -> dict:
        files={"svg":output_name+".svg"}
        if (hist_styler is None): hist_styler=HistogramStyler()

        # calculate bar heights
        height=min(int(100/df.shape[0]),10)-2
        y_max=2+(df.shape[0]*(2+height))
        hist_styler.font_size=height

        min_row_sum=df.sum(axis=1).min()
        max_row_sum=df.sum(axis=1).max()
        max_bar_width=100-hist_styler.axis_x_pos
        widths_df=df.copy().apply(lambda x:(max_bar_width*x)/max_row_sum).astype(int)

        svg_file=open(output_name+".svg","w+")
        svg_file.write('<svg xmlns="http://www.w3.org/2000/svg" viewbox="0 0 100 {}" width="100%" height="100%" version="1.1">\n'.format(y_max))

        # add_bars
        SVGMaker.__add_animation_histogram_bars(svg_file,widths_df,hist_styler)

        # add text
        if (hist_styler.text):
            x_poss=[hist_styler.axis_x_pos-1 for _ in range(widths_df.shape[0])]
            labels=[SVGMaker.__seconds_to_time_str(val) for val in widths_df.index]
            SVGMaker.__add_histogram_text(svg_file,x_poss,labels,hist_styler)

        # add axis
        if (hist_styler.axis): html_file_name=svg_file.write('\t<line class="hist_axis" x1="{}" y1="0" x2="{}" y2="{}" stroke-linecap="square" style="{}"></line>\n'.format(hist_styler.axis_x_pos,hist_styler.axis_x_pos,y_max,hist_styler.axis_style_str())) # y axis

        # end file
        svg_file.write("</svg>")
        svg_file.close()

        # css_file_name=SVGMaker.__generate_css_for_animated_histogram(widths_df.columns,hist_styler=hist_styler,output_name=output_name) # add animation
        css_file_name=hist_styler.animation_function(widths_df.columns,hist_styler=hist_styler,output_name=output_name) # add animation
        files["css"]=css_file_name
        if (html):
            html_file_name=SVGMaker.generate_html_for_svg(svg_file_name=output_name+".svg",css_file_name=css_file_name,output_name=output_name) # html for previewing
            files["html"]=html_file_name

        return files

    # add bars for animated histogram (each bar is split up into km intervals)
    def __add_animation_histogram_bars(svg_file,widths_df:pd.DataFrame,hist_styler:HistogramStyler):
        height=min(int(100/widths_df.shape[0]),10)-hist_styler.space_between_bars

        x={val:hist_styler.axis_x_pos for val in widths_df.index}
        for col in widths_df.columns:
            column=widths_df[col]
            count=0
            for split,width in column.iteritems():
                y=hist_styler.space_between_bars+count*(hist_styler.space_between_bars+height)
                if (width!=0):
                    svg_file.write('\t<rect class="animated_hist_bar bar_{}" x="{}" y="{}" width="{}" height="{}" '.format(col,x[split],y,width,height)) # dimensions
                    x[split]+=width
                    svg_file.write('style="{}">'.format(hist_styler.rect_style_str())) # styling
                    svg_file.write('</rect>\n')
                count+=1

    """
    ANIMATION
    """
    # creates csv file which adds animation to histogram
    def histogram_animation_freeze(col_labels,hist_styler,output_name="test/animated_hist") -> str:
        frame_length=max(round(hist_styler.animation_length/len(col_labels),1),.1)
        css_file=open(output_name+".css","w+")
        css_file.write(".animated_hist_bar {\n\ttransition-timing-function: ease;\n\ttransition-duration: .4s;\n\topacity: 0;\n}\n\n")
        css_file.write("@keyframes opacity {\n\t0% {opacity: 0}\n\t100% {opacity: 1}\n}\n\n")

        for count,col in enumerate(col_labels):
            css_file.write(".bar_{} {{\n\tanimation: linear {}s opacity forwards;\n".format(col,frame_length))
            if (count!=0): css_file.write("\tanimation-delay: {}s\n".format(count*frame_length))
            css_file.write("}\n\n")

        css_file.close()
        return output_name+".css"

    def histogram_animation_bounce(col_labels,hist_styler,output_name="test/animated_hist.css") -> str:
        pause_pct=20 # percentage of animation spent frozen on complete
        reset_pct=10 # percentage of animation spend return to origin pos
        frame_pct=int((100-hist_styler.pause_pct-hist_styler.reset_pct)/len(col_labels))

        css_file=open(output_name+".css","w+")
        css_file.write(".animated_hist_bar {\n\ttransition-timing-function: ease;\n\ttransition-duration: .4s;\n\topacity: 0;\n}\n\n")

        for count,col in enumerate(col_labels):
            start_transition=count*frame_pct
            end_transition=(count+1)*frame_pct
            css_file.write(".bar_{} {{\n\tanimation: linear {}s opacity_{} infinite;}}\n".format(col,hist_styler.animation_length,col))
            # individual animations
            css_file.write("@keyframes opacity_{} {{\n\t0% {{opacity: 0;}}\n".format(col))
            if (start_transition!=0): css_file.write("\t{}% {{opacity: 0;}}\n".format(start_transition))
            if (end_transition!=100-hist_styler.pause_pct-hist_styler.reset_pct): css_file.write("\t{}% {{opacity: 1;}}\n".format(end_transition))
            css_file.write("\t{}% {{opacity: 1;}}\n".format(100-hist_styler.reset_pct-hist_styler.pause_pct))
            css_file.write("\t{}% {{opacity: 1;}}\n".format(100-hist_styler.reset_pct))
            css_file.write("\t100% {opacity: 0;}\n}\n\n")

        return output_name+".css"

    def hello(greet): print(greet)

    # creates csv file which adds css to make a dash follow the path in an infintie loop
    def __generate_css_for_animated_route(class_name,route_styler=None,output_name="test/animated_route"):
        if (route_styler is None): route_styler=RouteStyler()
        css_file=open(output_name+".css","w+")

        css_file.write(".{} {{\n\tstroke-dasharray:1000;\n\tstroke-dashoffset:1000;\n\tanimation: draw {}s linear infinite;\n}}\n\n".format(class_name,route_styler.animation_length))
        css_file.write("@keyframes draw {\n\t0%{\n\t\tstroke-dashoffset:0;\n\t}\n}")

        css_file.close()

        return output_name+".css"

    # creates js file which updates the dash offset & length so that the loop is seemless
    def __generate_js_for_animated_route(class_name,route_styler=None,output_name="test/animated_route"):
        if (route_styler is None): route_styler=RouteStyler()
        js_file=open(output_name+".js","w+")

        js_file.write("document.addEventListener('DOMContentLoaded', function() {{\n\tupdate_stroke_dash({},'.{}');\n}});\n\n".format(route_styler.num_dashes,class_name))
        js_file.write("function update_stroke_dash(num_dashs,class_name) {{\n\tvar path=document.querySelector(class_name);\n\tvar length=path.getTotalLength();\n\tvar dash_length=length/num_dashs;\n\tpath.style.strokeDasharray=dash_length;\n\tpath.style.strokeDashoffset=-(dash_length*2);\n}}".format())

        js_file.close()
        return output_name+".js"

    """
    HELPERS
    """
    # generates html file for visulasing svg
    def generate_html_for_svg(svg_file_name,css_file_name=None,js_file_name=None,output_name="test/example",path_to_remove="test/") -> str:
        html_file=open(output_name+".html","w+")
        html_file.write('<html>\n\t<head>\n')

        if css_file_name is not None: html_file.write('\t\t<link rel="stylesheet" type="text/css" href={}>\n'.format(css_file_name.replace(path_to_remove,"")))
        if js_file_name is not None: html_file.write('\t\t<script src="{}"></script>\n'.format(js_file_name.replace(path_to_remove,"")))

        html_file.write('\t</head>\n\t<body>\n')

        with open(svg_file_name,"r") as svg_file:
            for line in svg_file:
                html_file.write("\t"+line)

        html_file.write("\t</body>\n</html>")
        return output_name+".html"

    # html file with multiple plots on
    def generate_html_for_many_svg(files:"[{'svg':str,'css':str,'js':str}]",per_row=2,output_name="test/many_examples",path_to_remove="test/"):
        svg_files=[dic["svg"] for dic in files if "svg" in dic]
        css_files=[dic["css"] for dic in files if "css" in dic]
        js_files= [dic["js"]  for dic in files if "js" in dic]

        html_file=open(output_name+".html","w+")
        html_file.write("<html>")

        if (len(css_files)+len(js_files)>0):
            html_file.write("\t<head>\n")
            html_file.write("\t\t<style>::-webkit-scrollbar {display: none;}</style>\n")
            for js_file in js_files: html_file.write('\t\t<script src="{}"></script>\n'.format(js_file.replace(path_to_remove,"")))
            for css_file in css_files: html_file.write('\t\t<link rel="stylesheet" type="text/css" href={}>\n'.format(css_file.replace(path_to_remove,"")))
            html_file.write("\t</head>\n")

        if (len(svg_files)>0):
            dim=int(99/per_row)
            html_file.write("\t<body>\n")
            for svg_file in svg_files:
                html_file.write("\t\t<div class='container' style='display:inline-flex;width:{}vw;height:{}vw'>\n".format(dim,dim))
                html_file.write("\t\t\t<div style='display:block;width:100%;height:100%'>\n")
                html_file.write("<h1 style='margin:0;height:10%;font-size:{}vw;text-align:center'>{}</h1>\n".format(dim/10,svg_file))
                with open(svg_file,"r") as f:
                    for line in f: html_file.write("\t\t\t\t"+line.replace('height="100%"','height="90%"')) # hard add svg file
                html_file.write("\t\t</div>\n")
                html_file.write("\t\t</div>\n")

            html_file.write("\t</body>\n")

        html_file.write("</html>")

        return output_name+".html"

class DefaultStylers:
    # colour listed light to dark
    # ffcad4,ffacc5,ffacc5
    hot_pink_route=RouteStyler(path_colour="#ff87ab",dash_colour="#ffacc5",animated=True,num_dashes=12)
    hot_pink_elevation=ElevationStyler(path_colour="#ff87ab",dash_colour="#ffacc5",fill_colour="#ffcad4",animated=True,num_dashes=12)
    hot_pink_hist=HistogramStyler(None,stroke_colour="#ff87ab",rect_colour="#ffcad4",font_anchor="end",space_between_bars=0,font_colour="#ff87ab",axis_x_pos=0)
    hot_pink_animated_hist=HistogramStyler(SVGMaker.histogram_animation_bounce,rect_colour="#ff87ab",font_anchor="end",space_between_bars=0,font_colour="#ff87ab",stroke_width=0,text_gap=0)
    hot_pink={"route":hot_pink_route,"elevation":hot_pink_elevation,"hist":hot_pink_hist,"animated_hist":hot_pink_animated_hist}

    # 9db8a1,547358,214025
    after_eights_route=RouteStyler(path_colour="#214025",dash_colour="#547358",animated=True,num_dashes=12,start_marker=True,finish_marker=True,split_dist=1000,split_marker_colour="#000")
    after_eights_elevation=ElevationStyler(path_colour="#214025",dash_colour="#547358",fill_colour="#9db8a1",animated=True,num_dashes=12)
    after_eights_hist=HistogramStyler(None,stroke_colour="#547358",rect_colour="#214025",font_anchor="end",space_between_bars=0,font_colour="#9db8a1",axis_x_pos=0)
    after_eights_animated_hist=HistogramStyler(SVGMaker.histogram_animation_bounce,rect_colour="#214025",font_anchor="end",space_between_bars=0,font_colour="#9db8a1",stroke_width=0,text_gap=0)
    after_eights={"route":after_eights_route,"elevation":after_eights_elevation,"hist":after_eights_hist,"animated_hist":after_eights_animated_hist}

    # dc2f02,d00000,9d0208
    fire_route=RouteStyler(path_colour="#dc2f02",dash_colour="#d00000",animated=True,animation_length=1,num_dashes=12,start_marker=True,finish_marker=True,split_dist=1000,split_marker_colour="#000")
    fire_elevation=ElevationStyler(path_colour="#dc2f02",dash_colour="#d00000",fill_colour="#9d0208",animated=True,animation_length=1,num_dashes=12)
    fire_hist=HistogramStyler(None,stroke_colour="#dc2f02",rect_colour="#9d0208",font_anchor="end",space_between_bars=0,font_colour="#d00000",axis_x_pos=0)
    fire_animated_hist=HistogramStyler(SVGMaker.histogram_animation_bounce,rect_colour="#9d0208",font_anchor="end",space_between_bars=0,font_colour="#d00000",stroke_width=0,text_gap=0)
    fire={"route":fire_route,"elevation":fire_elevation,"hist":fire_hist,"animated_hist":fire_animated_hist}

    # 02c39a,00a896,028090
    agua_route=RouteStyler(path_colour="#00a896",dash_colour="#028090",animated=True,num_dashes=12,start_marker=True,finish_marker=True,split_dist=1000,split_marker_colour="#000")
    agua_elevation=ElevationStyler(path_colour="#00a896",dash_colour="#028090",fill_colour="#02c39a",animated=True,num_dashes=12)
    agua_hist=HistogramStyler(None,stroke_colour="#00a896",rect_colour="#028090",font_anchor="end",space_between_bars=0,font_colour="#00a896",axis_x_pos=0)
    agua_animated_hist=HistogramStyler(SVGMaker.histogram_animation_bounce,rect_colour="#028090",font_anchor="end",space_between_bars=0,font_colour="#00a896",stroke_width=0,text_gap=0)
    agua={"route":agua_route,"elevation":agua_elevation,"hist":agua_hist,"animated_hist":agua_animated_hist}


def plot_all(file_path,to_plot={"route":None,"elevation":None,"histogram":None,"animated_histogram":None}) -> str:

    reader=GPSReader()
    data,metadata=reader.read(file_path)
    df=reader.data_to_dataframe(data)

    files=[]
    if "route" in to_plot:
        styler=RouteStyler() if (to_plot["route"] is None) else to_plot["route"]
        new_files=SVGMaker.generate_route_svg(df,route_styler=styler)
        files.append(new_files)

    if "elevation" in to_plot:
        styler=ElevationStyler() if (to_plot["elevation"] is None) else to_plot["elevation"]
        new_files=SVGMaker.generate_elevation_svg(df,elevation_styler=styler)
        files.append(new_files)

    if "histogram" in to_plot:
        styler=HistogramStyler() if (to_plot["histogram"] is None) else to_plot["histogram"]
        hist_data=GPSEvaluator.split_histogram_data(df,clean=True)
        new_files=new_files=SVGMaker.generate_histogram(hist_data,hist_styler=styler,output_name="test/hist")
        files.append(new_files)

    if "animated_histogram" in to_plot:
        styler=HistogramStyler() if (to_plot["animated_histogram"] is None) else to_plot["animated_histogram"]
        hist_data_per_km=GPSEvaluator.split_histogram_data_per_km(df,clean=True)
        new_files=SVGMaker.generate_animated_histogram(hist_data_per_km,hist_styler=styler)
        files.append(new_files)

    return SVGMaker.generate_html_for_many_svg(files,per_row=2)

if __name__=="__main__":
    stylers=DefaultStylers.after_eights
    plots={
        # "route":RouteStyler(animated=True,animation_length=5,num_dashes=12,split_dist=1000,start_marker=True,finish_marker=True,split_marker_colour="purple"),
        # "elevation":ElevationStyler(animated=True,animation_length=5,num_dashes=12,plinth_height=30),
        # "histogram":HistogramStyler(font_anchor="end",space_between_bars=0,font_colour="#fff"),
        # "animated_histogram":HistogramStyler(font_anchor="end",animation_length=3,space_between_bars=0,text_gap=0)
        "route":stylers["route"],
        "elevation":stylers["elevation"],
        "histogram":stylers["hist"],
        "animated_histogram":stylers["animated_hist"]
    }
    print(plot_all("examples/example_ride.tcx",to_plot=plots))
