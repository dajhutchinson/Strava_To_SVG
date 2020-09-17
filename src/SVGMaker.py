"""
    TODO
    More Histograms (generalise)
    Multiple routes
    Colour route depending upon elevation
    Text position options (On axis, on tip of bar, in bar)
    Tool tips (title on svg rect)
"""
from src.GPSReader import GPSReader
from src.GPSEvaluator import GPSEvaluator
from math import ceil
import pandas as pd
import re
# define style used for histograms
class HistogramStyler:

    @staticmethod
    def __ensure_hex(hex_val:str) -> str:
        """
        SUMMARY
        ensure correct formatting for a hex colour code. Checks that first character is '#' and rest is 3 or 6 digits

        PARAMETERS
        hex_val (str/int): code to format

        RETURNS
        str: encoded hex string. (returns None if cannot create correct format)
        """
        hex_str=str(hex_val)
        if bool(re.search("#[0-9a-f]{3}",hex_str)): return hex_str
        if bool(re.search("[0-9a-f]{3}",hex_str)):  return "#"+hex_str
        if bool(re.search("#[0-9a-f]{6}",hex_str)): return hex_str
        if bool(re.search("[0-9a-f]{6}",hex_str)):  return "#"+hex_str
        return None

    def __init__(self,animation_function,rect_colour="#214025",stroke_width=1,stroke_colour="#547358",space_between_bars=2,
                text=True,font_size=12,text_gap=None,
                font_family="arial",font_colour="#000",font_anchor="start",
                axis=True,axis_x_pos=10,axis_colour="#000",axis_width=1,
                animation_length=10,pause_pct=20,reset_pct=10):
        """
        SUMMARY
        specify style guide and features for a histogram.
        used in SVGMaker.generate_histogram, SVGMaker.generate_animated_histogram

        PARAMETERS
        rect_colour (str): hexcode colour of bars (default="#214025")
        stroke_width (int): width of border in px (default=1)
        stroke_colour (str): hexcode colour of border (default="#547358")
        space_between_bars (int): vertical space between bars (default=2)

        text (bool): whether to include text (default=True)
        font_size (int): size of text in px (default=12)
        text_gap (int): horizontal gap between text and end of bar (default=None)
        font_family (str): font family (default="arial")
        font_colour (str): colour of text (defaukt="#000")
        font_anchor (str): how text is aligned to given position. ["start","middle","end"] (default="start")

        axis (bool): whether to include an axis(default=True)
        axis_x_pos (int): horizontal position of vertical axis (default=10)
        axis_colour (str): colour of axis (default="#000")
        axis_width (int): with of axis in px(default=1)

        animation_function (str): type of animation
                                  `SVGMaker.histogram_animation_freeze`. Animates in then freezes in final state.
                                    OPTIONS: None
                                  `SVGMaker.histogram_animation_bounce`. Animates in, holds, animates back out in an infinite loop.
                                    OPTIONS: pause_pct,reset_pct
        animation_length (int): length of animation in seconds (default=10)
        pause_pct (int): Proportion of time for which final state is held. option for SVGMaker.histogram_animation_bounce.(default=20)
        reset_pct (int): Proportion of time to animate out. option for SVGMaker.histogram_animation_bounce(default=10)
        """

        # rect
        self.stroke_width=stroke_width # border
        self.stroke_colour=HistogramStyler.__ensure_hex(stroke_colour)
        self.rect_colour=HistogramStyler.__ensure_hex(rect_colour) # fill colour of rect
        self.space_between_bars=max(0,space_between_bars)

        # text styling
        self.text=text
        self.text_gap=stroke_width+1 if (text_gap is None) else text_gap
        self.font_size=font_size
        self.font_colour=HistogramStyler.__ensure_hex(font_colour)
        self.font_family=font_family
        self.font_anchor=font_anchor

        # x value of vertical axis
        self.axis=axis
        self.axis_x_pos=axis_x_pos
        self.axis_colour=HistogramStyler.__ensure_hex(axis_colour)
        self.axis_width=axis_width

        # animation
        self.animation_length=animation_length
        self.animation_function=animation_function

        # parameters for __histogram_animation_bounce
        self.pause_pct=pause_pct
        self.reset_pct=reset_pct

    def bar_style_str(self) -> str:
        """
        SUMMARY
        string for style tag of svg rect object which represents a bar

        PARAMETERS
	    None

        RETURNS
	    str: style string
        """
        return "fill:{};stroke-width:{}px;stroke:{}".format(self.rect_colour,self.stroke_width,self.stroke_colour)

    def text_style_str(self) -> str:
        """
        SUMMARY
        string for style tag of svg text object

        PARAMETERS
        None

        RETURNS
	    str: style string
        """
        return "font-size:{}px;font-family:{};fill:{}".format(self.font_size,self.font_family,self.font_colour)

    def axis_style_str(self) -> str:
        """
        SUMMARY
        string for style tag of svg rect object which represents the axis

        PARAMETERS
	    None

        RETURNS
	    str: style string
        """
        return "stroke:{};stroke-width:{}px".format(self.axis_colour,self.axis_width)

class RouteStyler:

    @staticmethod
    def __ensure_hex(hex_val:str) -> str:
        """
        SUMMARY
        ensure correct formatting for a hex colour code. Checks that first character is '#' and rest is 3 or 6 digits

        PARAMETERS
        hex_val (str/int): code to format

        RETURNS
        str: encoded hex string. (returns None if cannot create correct format)
        """
        hex_str=str(hex_val)
        if bool(re.search("#[0-9a-f]{3}",hex_str)): return hex_str
        if bool(re.search("[0-9a-f]{3}",hex_str)):  return "#"+hex_str
        if bool(re.search("#[0-9a-f]{6}",hex_str)): return hex_str
        if bool(re.search("[0-9a-f]{6}",hex_str)):  return "#"+hex_str
        return None

    def __init__(self,border_width=10,path_colour="#214025",fill_colour=None,path_width=5,path_linejoin="round",
        animated=False,animation_length=10,num_dashes=2,dash_colour="#547358",
        split_dist=None,split_marker_colour="#000",split_marker_width=5,
        start_marker=False,start_marker_colour="#00ff00",start_marker_width=5,
        finish_marker=False,finish_marker_colour="#ff0000",finish_marker_width=5):
        """
        SUMMARY
        specify style guide and features for a histogram.
        used in SVGMaker.generate_route_svg

        PARAMETERS
	    border_width (int): amount of empty space around path in svg (default=10)

        fill_colour (str): hexcode colour for fill of path. pass `None` for no fill (default=`None`)
        path_colour (str): hexcode colour for path. (default="#214025")
        path_width (int): width of route path in px (default=5)
        path_linejoin (str): how path looks at point where two lines. see svg 'stroke-linejoin' property. (default="round")

        animated (bool): whether path is animated (default=False)
        animation_length (int): length of animation in seconds (default=10)
        num_dashes (int): number of dashes moving in animation (default=2)
        dash_colour (str): hexcode colour of animated dashs (default="#547358")

        split_dist (int): at what distance to add markers. pass `None` if you want no markers. (default=None)
        split_marker_colour (str): hexcode colour for split markers. (default="#000")
        split_marker_width (int): radius of markers. Note that markers are circles. (default=5)

        start_marker (bool): whether to include a marker for the start location. (default=False)
        start_marker_colour (str): hexcode colour for marker. (default="#00ff00")
        start_marker_width (int): radius of marker. Note that marker is a circle. (default=5)

        finish_marker (bool): whether to include a marker for the end location. (default=False)
        finish_marker_colour (str): hexcode colour for marker. (default="#ff0000")
        finish_marker_width (int): radius of marker. Note that marker is a circle. (default=5)
        """
        # image styling
        self.border_width=border_width

        self.fill_colour="none" if (fill_colour is None) else RouteStyler.__ensure_hex(fill_colour)

        # path
        self.path_colour=RouteStyler.__ensure_hex(path_colour)
        self.path_width=path_width
        self.path_linejoin=path_linejoin

        # animation
        self.animated=animated
        self.animation_length=animation_length
        self.num_dashes=num_dashes
        self.dash_colour=RouteStyler.__ensure_hex(dash_colour)

        # split markers (ie mile markers)
        self.split_dist=split_dist # set to None for no markers
        self.split_marker_colour=RouteStyler.__ensure_hex(split_marker_colour)
        self.split_marker_width=split_marker_width

        # start & end markers
        self.start_marker=start_marker
        self.start_marker_colour=RouteStyler.__ensure_hex(start_marker_colour)
        self.start_marker_width=start_marker_width

        self.finish_marker=finish_marker
        self.finish_marker_colour=finish_marker_colour
        self.finish_marker_width=RouteStyler.__ensure_hex(finish_marker_width)

    def path_style_str(self) -> str:
        """
        SUMMARY
        string for style tag of svg path object representing route (without animation)

        PARAMETERS
        None

        RETURNS
	    str: style string
        """
        return 'fill="{}" stroke-width="{}px" stroke-linejoin="{}" stroke="{}"'.format(self.fill_colour,self.path_width,self.path_linejoin,self.path_colour)

    def animated_path_style_str(self) -> str:
        """
        SUMMARY
        string for style tag of svg text object representing route (with animation)

        PARAMETERS
        None

        RETURNS
	    str: style string
        """
        return 'fill="{}" stroke-width="{}px" stroke-linejoin="{}" stroke="{}"'.format("none",self.path_width,self.path_linejoin,self.dash_colour)

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

        """
        SUMMARY
        specify style guide and features for an evelation plot. An extension of RouteStyler
        used in SVGMaker.generate_elevation_svg

        PARAMETERS
        see RouteStyler
        plinth_height (int): heigh of plinth. gap between lowest point and bottom of plot. (default=30)
        """

        self.plinth_height=plinth_height # set to None for no plinth

class SVGMaker:

    """
    MANIPULATE DATA
    """
    def __scale_with_border(v:float,min_v:float,max_v:float,scale=1,border=0) -> int:
        """
        SUMMARY
        linearly scale value in [0,1000] with border accounted for.
        effectively scales in [border,1000-border]. used for SVGMaker.generate_route_svg

        PARAMETERS
	    v (float): value to scale
        v_min (float): min possible value
        v_max (float): max possible value
        scale (float): scale factor. used when scaling wrt another set of value and wishing to maintain aspect ratio (default=1)
        border (int): width of border (default=0)

        RETURNS
	    int: scaled value
        """
        range=1000-2*border
        return int(border+range*scale*(v-min_v)/(max_v-min_v))

    def __scale_elevation(v:float,min_v:float,max_v:float,border=0) -> int:
        """
        SUMMARY
        linearly scale value in [0,1000] with border accounted for.
        different to SVGMaker.__scale_with_border as it ensures the elevation gradients are not over-exaggerated

        PARAMETERS
	    v (float): value to scale
        v_min (float): min possible value
        v_max (float): max possible value
        border (int): width of border (default=0)

        RETURNS
	    int: scaled value
        """
        scale_range=min(1000,4*(max_v-min_v))
        return border+scale_range-int(scale_range*(v-min_v)/(max_v-min_v))

    def __seconds_to_time_str(seconds:int) -> str:
        """
        SUMMARY
        converts a count of seconds into a string of form "mm:ss".
        used for labels for split histogram.

        PARAMETERS
	    seconds (int): number of seconds

        RETURNS
	    str: time string of form "mm:ss"
        """
        secs=seconds%60
        mins=seconds//60
        return "{}:{}".format(mins,"0"+str(secs) if secs<10 else secs)

    """
    PLOTS
    """

    """ROUTE"""
    def generate_route_svg(df:pd.DataFrame,output_name="test/route",route_styler=None,html=False) -> dict:
        """
        SUMMARY
        generates an svg which includes a path representing the route defined by gps data

        PARAMETERS
	    df (pandas.DataFrame): dataframe of data produced by GPSReader.read()
                               requires "position_lat" & "position_lon" column. Assumes rows are in chronological order
        output_name (str): name & relative path of file to output. (default="test/route")
        route_styler (RouteStyler): styler for plot. pass `None` for RouteStyler with default values. (default=None).
        html (bool): whether to generate a html file which includes generated plot. (default=False)
                     NOTE will be named `output_name`.html

        RETURNS
	    dict: files generated [file_type:path]
              (returns `None` if insufficient data in `df`)
        """
        if output_name[-4:]==".svg": output_name=output_name[:-4] # remove extension
        files={"svg":output_name+".svg"}

        if ("position_lat" not in df) or ("position_lon" not in df): return None # insufficient data
        lat_lon_data=df[["position_lat","position_lon"]].copy() # ensure data isn't affected

        if route_styler is None: route_styler=RouteStyler() # ensure a style is applied

        scaling={} # store values to help with scaling
        scaling["min_lat"]=lat_lon_data["position_lat"].min(); scaling["max_lat"]=lat_lon_data["position_lat"].max() # determine range of values
        scaling["min_lon"]=lat_lon_data["position_lon"].min(); scaling["max_lon"]=lat_lon_data["position_lon"].max()
        lat_diff=scaling["max_lat"]-scaling["min_lat"]; lon_diff=scaling["max_lon"]-scaling["min_lon"]; max_diff=max(lon_diff,lat_diff)
        scaling["lat_scale"]=lat_diff/max_diff; scaling["lon_scale"]=lon_diff/max_diff # ensure scaling is good

        # path string
        point_str=SVGMaker.__route_svg_path_string(lat_lon_data,route_styler,scaling)

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
        if (route_styler.split_dist is not None): SVGMaker.__add_route_svg_split_markers(svg_file,df,route_styler,scaling)

        # add special markers
        if (route_styler.finish_marker): SVGMaker.__add_route_svg_special_markers("finish",route_styler.finish_marker_width,route_styler.finish_marker_colour,route_styler.border_width,svg_file,df,scaling,route_styler)
        if (route_styler.start_marker): SVGMaker.__add_route_svg_special_markers("start",route_styler.start_marker_width,route_styler.start_marker_colour,route_styler.border_width,svg_file,df,scaling,route_styler)

        # end file
        svg_file.write("</svg>")
        svg_file.close()

        # html file for previewing
        if (html):
            html_file_name=SVGMaker.generate_html_for_svg(svg_file_name=output_name+".svg",css_file_name=css_file_name,js_file_name=js_file_name,output_name=output_name)
            files["html"]=html_file_name

        return files

    def __route_svg_path_string(lat_lon_data:pd.DataFrame,route_styler:RouteStyler,scaling:dict) -> str:
        """
        SUMMARY
        generate string for points in path of route.
        used by SVGMaker.generate_route_svg

        PARAMETERS
	    lat_lon_data (pandas.DataFrame): dataframe of data produced by GPSReader.read() to plot from.
                                         requires "position_lat" and "position_lon" columns
        route_styler (RouteStyler): styler
        scaling (dict): contains details of range of lat&lon values to help scaling. requires ["min_lat","max_lat","lat_scale","min_lon","max_lon","lon_scale"]

        RETURNS
	    str: string of points
        """
        lon_diff=scaling["max_lon"]-scaling["min_lon"]
        lat_diff=scaling["max_lat"]-scaling["min_lat"]
        max_diff=max(lon_diff,lat_diff)
        flip_y=lambda x: route_styler.border_width+ceil(1000*(lat_diff/max_diff))-x # function to flip y since it increases as it goes down the image

        # scale gps coords to [0-1000] leaving a border
        lat_lon_data["scaled_lat"]=lat_lon_data["position_lat"].apply(SVGMaker.__scale_with_border,min_v=scaling["min_lat"],max_v=scaling["max_lat"],scale=scaling["lat_scale"],border=route_styler.border_width)
        lat_lon_data["scaled_lat"]=lat_lon_data["scaled_lat"].apply(flip_y)
        lat_lon_data["scaled_lon"]=lat_lon_data["position_lon"].apply(SVGMaker.__scale_with_border,min_v=scaling["min_lon"],max_v=scaling["max_lon"],scale=scaling["lon_scale"],border=route_styler.border_width).astype(int)

        # "x,y" string for each point
        lat_lon_data["point_str"]=lat_lon_data.apply(lambda row:"{},{}".format(str(int(row["scaled_lon"])),str(int(row["scaled_lat"]))),axis=1)
        point_str=" ".join(lat_lon_data["point_str"].tolist())

        return point_str

    def __add_route_svg_animation(svg_file,class_name:str,route_styler:RouteStyler,point_str:str,output_name:str) -> (str,str):
        """
        SUMMARY
        add animation to a route svg.
        used by SVGMaker.generate_route_svg

        PARAMETERS
	    svg_file (file): file to add animation to. ensure file isn't already closed (ie no `</svg>` tag)
        class_name (str): name of css class for animation
        route_styler (RouteStyler): styler
        point_str (str): string of points in route path
        output_name (str): name & relative path to output files. used to name css & js files which add animation

        RETURNS
	    str: path to css file
        str: path to js file
        """
        svg_file.write('<path class="{}" {} d="M{}" ></path>\n'.format(class_name,route_styler.animated_path_style_str(),point_str)) # path to be animated
        css_file_name=SVGMaker.__generate_css_for_animated_route(class_name,route_styler=route_styler,output_name=output_name) # adds animation
        js_file_name=SVGMaker.__generate_js_for_animated_route(class_name,route_styler=route_styler,output_name=output_name)   # ensures animation is seamless
        return css_file_name,js_file_name

    def __add_route_svg_split_markers(svg_file,df:pd.DataFrame,route_styler:RouteStyler,scaling:dict) -> str:
        """
        SUMMARY
        add split markers to a route svg.
        used by SVGMaker.generate_route_svg

        PARAMETERS
	    svg_file (file): file to add animation to. ensure file isn't already closed (ie no `</svg>` tag)
        df (pandas.DataFrame): dataframe of data produced by GPSReader.read() to plot from.
                               requires "position_lat" and "position_lon" columns
        route_styler(RouteStyler): styler
        scaling (dict): contains details of range of lat&lon values to help scaling. requires ["min_lat","max_lat","lat_scale","min_lon","max_lon","lon_scale"]

        RETURNS
	    file: svg file (same as parameter `svg_file`)
        """
        lon_diff=scaling["max_lon"]-scaling["min_lon"]
        lat_diff=scaling["max_lat"]-scaling["min_lat"]
        max_diff=max(lon_diff,lat_diff)
        flip_y=lambda x: route_styler.border_width+ceil(1000*(lat_diff/max_diff))-x # function to flip y since it increases as it goes down the image
        split_coords=GPSEvaluator.split_markers(df,route_styler.split_dist) # get marker lat,lon positions

        # scale to canvas
        split_coords["scaled_lat"]=split_coords["position_lat"].apply(SVGMaker.__scale_with_border,min_v=scaling["min_lat"],max_v=scaling["max_lat"],scale=scaling["lat_scale"],border=route_styler.border_width).astype(int)
        split_coords["scaled_lat"]=split_coords["scaled_lat"].apply(flip_y)
        split_coords["scaled_lon"]=split_coords["position_lon"].apply(SVGMaker.__scale_with_border,min_v=scaling["min_lon"],max_v=scaling["max_lon"],scale=scaling["lon_scale"],border=route_styler.border_width).astype(int)

        for _,row in split_coords.iterrows(): # add markers
            svg_file.write('<circle cx="{}" cy="{}" r="{}" fill="{}" />'.format(row["scaled_lon"],row["scaled_lat"],route_styler.split_marker_width,route_styler.split_marker_colour))

        return svg_file

    def __add_route_svg_special_markers(marker_type:str,marker_width:int,marker_colour:str,image_border:int,svg_file,df:pd.DataFrame,scaling:dict,route_styler:RouteStyler) -> str:
        """
        SUMMARY
        add markers for special locations on a route svg.
        used by SVGMaker.generate_route_svg

        PARAMETERS
        marker_type (str): name of marker to add. one of ["start","finish"] (see GPSEvaluator.important_points)
        marker_width (int): radius of marker. (RouteStyler.start_marker_width or RouteStyler.finish_marker_width)
        marker_colour (str): hexcode for marker colour. (RouteStyler.start_marker_colour or RouteStyler.finish_marker_colour)
        image_border (int): clear space around plot. (RouteStyler.border_width)
	    svg_file (file): file to add animation to. ensure file isn't already closed (ie no `</svg>` tag)
        df (pandas.DataFrame): dataframe of data produced by GPSReader.read() to plot from.
                               requires "position_lat" and "position_lon" columns
        route_styler(RouteStyler): styler
        scaling (dict): contains details of range of lat&lon values to help scaling. requires ["min_lat","max_lat","lat_scale","min_lon","max_lon","lon_scale"]

        RETURNS
	    file: svg file (same as parameter `svg_file`)
        """
        lon_diff=scaling["max_lon"]-scaling["min_lon"]
        lat_diff=scaling["max_lat"]-scaling["min_lat"]
        max_diff=max(lon_diff,lat_diff)
        flip_y=lambda x: route_styler.border_width+ceil(1000*(lat_diff/max_diff))-x # function to flip y since it increases as it goes down the image
        lat,lon=GPSEvaluator.important_points(df,name=marker_type)

        scaled_lat=int(SVGMaker.__scale_with_border(lat,min_v=scaling["min_lat"],max_v=scaling["max_lat"],scale=scaling["lat_scale"],border=image_border))
        scaled_lat=flip_y(scaled_lat)
        scaled_lon=int(SVGMaker.__scale_with_border(lon,min_v=scaling["min_lon"],max_v=scaling["max_lon"],scale=scaling["lon_scale"],border=image_border))

        svg_file.write('<circle cx="{}" cy="{}" r="{}" fill="{}" />'.format(scaled_lon,scaled_lat,marker_width,marker_colour))
        return svg_file

    """ELEVATION"""
    def generate_elevation_svg(df:pd.DataFrame,output_name="test/elevation",elevation_styler=None,html=False) -> dict:
        """
        SUMMARY
        generates an svg which includes a path representing the elevation on the route defined by gps data

        PARAMETERS
	    df (pandas.DataFrame): dataframe of data produced by GPSReader.read()
                               requires "cumm_distance" ("position_lat" & "position_lon" are required)
                               AND "altitude" columns.
                               Assumes rows are in chronological order
        output_name (str): name & relative path of file to output. (default="test/elevation")
        elevation_styler (ElevationStyler): styler for plot. pass `None` for ElevationStyler with default values. (default=None).
        html (bool): whether to generate a html file which includes generated plot. (default=False)
                     NOTE will be named `output_name`.html

        RETURNS
	    dict: files generated [file_type:path]
              (returns `None` if insufficient data in `df`)
        """
        if output_name[-4:]==".svg": output_name=output_name[:-4] # remove extension
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

    def __elevation_svg_path_string(elevation_df:pd.DataFrame,elevation_styler:ElevationStyler,scaling:dict) -> (str,int):
        """
        SUMMARY
        generate string for points in path of route.
        used by SVGMaker.generate_elevation_svg

        PARAMETERS
	    elevation_df (pandas.DataFrame): dataframe of data produced by GPSReader.read()
                                         requires "cumm_distance" ("position_lat" & "position_lon" are required)
                                         AND "altitude" columns.
                                         Assumes rows are in chronological order
        elevation_styler (ElevationStyler): styler
        scaling (dict): contains details of range of distance & altitude values to help scaling. requires ["min_dist","max_dist","min_alt","max_alt"]

        RETURNS
	    str: string of points
        int: y-value of bottom of path
        """
        elevation_df["scaled_altitude"]=elevation_df["altitude"].apply(lambda x:SVGMaker.__scale_elevation(x,scaling["min_alt"],scaling["max_alt"],border=elevation_styler.path_width))
        elevation_df["scaled_distance"]=elevation_df["cumm_distance"].apply(lambda x:SVGMaker.__scale_with_border(x,scaling["min_dist"],scaling["max_dist"],border=elevation_styler.path_width))

        elevation_df["point_str"]=elevation_df.apply(lambda row:"{},{}".format(str(int(row["scaled_distance"])),str(int(row["scaled_altitude"]))),axis=1)

        # content
        point_str=" ".join(elevation_df["point_str"].tolist())
        if elevation_styler.plinth_height is not None:
            plinth_height=max(0,min(30,elevation_styler.plinth_height)) # min alt above sea or defined height
            bottom_of_path=int(min(1000-elevation_styler.path_width,elevation_df["scaled_altitude"].max()+plinth_height))
            point_str="{},{} ".format(elevation_df["scaled_distance"].min(),bottom_of_path)+point_str+" {},{}".format(elevation_df["scaled_distance"].max(),bottom_of_path)+" {},{} ".format(elevation_df["scaled_distance"].min()-elevation_styler.path_width/2,bottom_of_path)
        else:
            bottom_of_path=int(min(1000-elevation_styler.path_width,elevation_df["scaled_altitude"].max()))

        return point_str, bottom_of_path

    """HISTOGRAM"""
    def generate_histogram(data:pd.Series,output_name="test/hist",hist_styler=None,html=False) -> dict:
        """
        SUMMARY
        produce an svg representing a horizontal histogram using data from GPSEvaluator.split_histogram_data.
        NOTE for an animated histogram see SVGMaker.generate_animated_histogram

        PARAMETERS
        data (pd.Series): data generated by GPSEvaluator.split_histogram_data
        output_name (str): name & relative path of file to output. (default="test/hist")
        hist_styler (HistogramStyler): styler for plot. pass `None` for HistogramStyler with default values. (default=None).
        html (bool): whether to generate a html file which includes generated plot. (default=False)
                     NOTE will be named `output_name`.html

        RETURNS
	    dict: files generated [file_type:path]
              (returns `None` if insufficient data in `df`)
        """
        if output_name[-4:]==".svg": output_name=output_name[:-4] # remove extension
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

    def __add_histogram_bars(svg_file,widths:pd.Series,hist_styler:HistogramStyler) -> [int]:
        """
        SUMMARY
        add histogram bars to svg file.
        used by SVGMaker.generate_histogram

        PARAMETERS
	    svg_file (file): file to add bars to. ensure file isn't already closed (ie no `</svg>` tag)
        widths (pd.Series): widths of bars to add. GPSEvaluator.split_histogram_data
        hist_styler (HistogramStyler): styler

        RETURNS
	    list(int): list of x-values of end of bars
        """
        height=min(int(100/widths.shape[0]),10)-hist_styler.space_between_bars
        count=0; x_poss=[]
        for _,width in widths.iteritems():
            y=hist_styler.space_between_bars+count*(hist_styler.space_between_bars+height)
            svg_file.write('<rect class="hist_bar" x="{}" y="{}" width="{}" height="{}" '.format(hist_styler.axis_x_pos,y,width,height)) # dimensions
            x_poss.append(hist_styler.axis_x_pos+width+1)
            svg_file.write('style="{}">'.format(hist_styler.bar_style_str())) # styling
            svg_file.write('</rect>\n')
            count+=1
        return x_poss

    def __add_histogram_text(svg_file,x_poss:[int],labels:[str],hist_styler:HistogramStyler) -> str:
        """
        SUMMARY
        add labels to end of bars in svg_file.
        used by SVGMaker.generate_histogram & SVGMaker.generate_animated_histogram

        PARAMETERS
	    svg_file (file): file to add bars to. ensure file isn't already closed (ie no `</svg>` tag)
        x_poss (list(int)): x_value for text for each bar. One value per bar.
        labels (list(str)): label for each bar. One value per bar.
        hist_styler (HistogramStyler): styler

        RETURNS
	    file: svg file (same as parameter `svg_file`)
        """
        height=min(int(100/len(x_poss)),10)-hist_styler.space_between_bars
        for i in range(len(x_poss)):
            x_pos=x_poss[i]; label=labels[i]
            y=hist_styler.space_between_bars+i*(hist_styler.space_between_bars+height)
            # add text to non-empty bars
            x_pos=x_pos+hist_styler.text_gap if (hist_styler.font_anchor=="start") else x_pos-hist_styler.text_gap
            if (x_pos!=hist_styler.axis_x_pos): svg_file.write('<text class="hist_text" x="{}" y="{}" dy="{}" text-anchor="{}" style="{}">{}</text>\n'.format(x_pos,y,height-1,hist_styler.font_anchor,hist_styler.text_style_str(),label))

        return svg_file

    def __add_histogram_axis(svg_file,hist_styler:HistogramStyler,y_max:int) -> str:
        """
        SUMMARY
        add vertical axis to histogram.
        used by SVGMaker.generate_histogram & SVGMaker.generate_animated_histogram

        PARAMETERS
	    svg_file (file): file to add axis to
        hist_styler (HistogramStyler): styler
        y_max (int): y-value for bottom of bar

        RETURNS
	    file: svg file (same as parameter `svg_file`)
        """
        svg_file.write('<line class="hist_axis" x1="{}" y1="0" x2="{}" y2="{}" stroke-linecap="square" style="{}"></line>\n'.format(hist_styler.axis_x_pos,hist_styler.axis_x_pos,y_max,hist_styler.axis_style_str())) # y axis

        return svg_file

    """ANIMATED HISTOGRAM"""
    def generate_animated_histogram(df:pd.DataFrame,output_name="test/animated_hist",hist_styler=None,html=False) -> dict:
        """
        SUMMARY
        produce an svg representing a horizontal histogram using data from GPSEvaluator.split_histogram_data_per_km
        NOTE for a non-animated histogram see SVGMaker.generate_histogram

        PARAMETERS
        df (pd.DataFrame): data generated by GPSEvaluator.split_histogram_data_per_km
        output_name (str): name & relative path of file to output. (default="test/animated_hist")
        hist_styler (HistogramStyler): styler for plot. pass `None` for HistogramStyler with default values and bounce animation. (default=None).
        html (bool): whether to generate a html file which includes generated plot. (default=False)
                     NOTE will be named `output_name`.html

        RETURNS
	    dict: files generated [file_type:path]
              (returns `None` if insufficient data in `df`)
        """
        if output_name[-4:]==".svg": output_name=output_name[:-4] # remove extension
        files={"svg":output_name+".svg"}
        if (hist_styler is None): hist_styler=HistogramStyler(animation_function=SVGMaker.histogram_animation_bounce)

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

    def __add_animation_histogram_bars(svg_file,widths_df:pd.DataFrame,hist_styler:HistogramStyler) -> str:
        """
        SUMMARY
        add bars to histogram svg file, such that animation is possible.
        used by SVGMaker.generate_animated_histogram

        PARAMETERS
	    svg_file (file): file to add bars to. ensure file isn't already closed (ie no `</svg>` tag)
        widths_df (pd.DataFrame): widths of bars to add for each km. data generated by GPSEvaluator.split_histogram_data_per_km
        hist_styler (HistogramStyler): styler

        RETURNS
	    file: svg file (same as parameter `svg_file`)
        """
        height=min(int(100/widths_df.shape[0]),10)-hist_styler.space_between_bars

        x={val:hist_styler.axis_x_pos for val in widths_df.index}
        for col in widths_df.columns: # add columns
            column=widths_df[col]
            count=0
            for split,width in column.iteritems(): # add each block for column
                y=hist_styler.space_between_bars+count*(hist_styler.space_between_bars+height)
                if (width!=0):
                    svg_file.write('\t<rect class="animated_hist_bar bar_{}" x="{}" y="{}" width="{}" height="{}" '.format(col,x[split],y,width,height)) # dimensions
                    x[split]+=width
                    svg_file.write('style="{}">'.format(hist_styler.bar_style_str())) # styling
                    svg_file.write('</rect>\n')
                count+=1
        return svg_file

    """
    ANIMATION
    """
    def histogram_animation_freeze(col_labels:[str],hist_styler:HistogramStyler,output_name="test/animated_hist") -> str:
        """
        SUMMARY
        creates css file which defines the *freeze* animation for a histogram.
        freeze animation animates the bars in (km at a time) and holds the final state.
        definable as `animation_function` property of `HistogramStyler`.

        PARAMETERS
	    col_labels (list(str)): name for each column (widths_df.columns). used to define css classes as `bar_{}`
        hist_styler (HistogramStyler): styler
        output_name (str): relative path and name for outputted css file. (default="test/animated_hist")

        RETURNS
	    str: path to created css file
        """
        if output_name[-4:]==".css": output_name=output_name[:-4] # remove extension
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

    def histogram_animation_bounce(col_labels:[str],hist_styler:HistogramStyler,output_name="test/animated_hist") -> str:
        """
        SUMMARY
        creates css file which defines the *bounce* animation for a histogram.
        bounce animation animates the bars in (km at a time); holds; then transitions back to initial state. This runs in an infite loop
        definable as `animation_function` property of `HistogramStyler`.

        PARAMETERS
	    col_labels (list(str)): name for each column (widths_df.columns). used to define css classes as `bar_{}`
        hist_styler (HistogramStyler): styler
        output_name (str): relative path and name for outputted css file. (default="test/animated_hist")

        RETURNS
	    str: path to created css file
        """
        if output_name[-4:]==".css": output_name=output_name[:-4] # remove extension
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

    def __generate_css_for_animated_route(class_name:str,route_styler=None,output_name="test/animated_route") -> str:
        """
        SUMMARY
        generate css file which defines the animation of dashes moving around the path in an infinite loop.
        NOTE requires SVGMaker.__generate_js_for_animated_route for clean animation
        used by SVGMaker.__add_route_svg_animation <= SVGMaker.generate_route_svg

        PARAMETERS
	    class_name (str): name of css class to defined animation for.
        route_styler (RouteStyler): styler. pass `None` for RouteStyler with default values. (default=None)
        output_name (str): relative path and name for outputted css file. (default="test/animated_route")

        RETURNS
	    str: path to generated css file
        """
        if output_name[-4:]==".css": output_name=output_name[:-4] # remove extension
        if (route_styler is None): route_styler=RouteStyler()
        css_file=open(output_name+".css","w+")

        css_file.write(".{} {{\n\tstroke-dasharray:1000;\n\tstroke-dashoffset:1000;\n\tanimation: draw {}s linear infinite;\n}}\n\n".format(class_name,route_styler.animation_length))
        css_file.write("@keyframes draw {\n\t0%{\n\t\tstroke-dashoffset:0;\n\t}\n}")

        css_file.close()

        return output_name+".css"

    def __generate_js_for_animated_route(class_name:str,route_styler=None,output_name="test/animated_route"):
        """
        SUMMARY
        generate js file which ensure the path animation runs as a **smooth** infinite loop
        NOTE relies of css file generate by SVGMaker.__generate_css_for_animated_route
        used by SVGMaker.__add_route_svg_animation <= SVGMaker.generate_route_svg

        PARAMETERS
	    class_name (str): name of css class to defined animation for.
        route_styler (RouteStyler): styler. pass `None` for RouteStyler with default values. (default=None)
        output_name (str): relative path and name for outputted css file. (default="test/animated_route")

        RETURNS
	    str: path to generated js file
        """
        if output_name[-3:]==".js": output_name=output_name[:-3] # remove extension
        if (route_styler is None): route_styler=RouteStyler()
        js_file=open(output_name+".js","w+")

        js_file.write("document.addEventListener('DOMContentLoaded', function() {{\n\tupdate_stroke_dash({},'.{}');\n}});\n\n".format(route_styler.num_dashes,class_name))
        js_file.write("function update_stroke_dash(num_dashs,class_name) {{\n\tvar path=document.querySelector(class_name);\n\tvar length=path.getTotalLength();\n\tvar dash_length=length/num_dashs;\n\tpath.style.strokeDasharray=dash_length;\n\tpath.style.strokeDashoffset=-(dash_length*2);\n}}".format())

        js_file.close()
        return output_name+".js"

    """
    HELPERS
    """
    def generate_html_for_svg(svg_file_name:str,css_file_name=None,js_file_name=None,output_name="test/example",path_to_remove="test/") -> str:
        """
        SUMMARY
        generates html file for previewing a *single* svg file. Ideal for those with animation
        NOTE for *multiple* svg files see SVGMaker.generate_html_for_many_svg

        PARAMETERS
	    svg_file_name (str): name of svg file to feature in page.
        css_file_name (str): name of css file to feature in page. pass `None` if no css file required. (default=None)
        js_file_name (str): name of js file to feature in page. pass `None` if no js file required. (default=None)
        output_name (str): relative name & path to where to output file. (default=`test/example`)
        path_to_remove (str): string to remove start of `svg_file_name`, `css_file_name` & `js_file_name` to ensure they are correctly defined relative to html file being generated. (default="test/")

        RETURNS
	    str: path & name of generated file (`output_name`+".html")
        """
        if (output_name[-5:]==".html"): output_name=output_name[:-5]
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

    def generate_html_for_many_svg(files:"[{'svg':str,'css':str,'js':str}]",per_row=2,output_name="test/many_examples",path_to_remove="test/") -> str:
        """
        SUMMARY
        generates html file for previewing a *multiple* svg files. Ideal for those with animation
        NOTE for *single* svg files see SVGMaker.generate_html_for_many_svg

        PARAMETERS
	    files (list(dict)): list of dictionaries defining the files associated to each svg image. dicts contain keys ["svg","css","js"]
        per_row (int): number of images per row (default=2).
        output_name (str): relative name & path to where to output file. (default=`test/many_examples`)
        path_to_remove (str): string to remove start of file names in `files` to ensure they are correctly defined relative to html file being generated. (default="test/")

        RETURNS
	    str: path & name of generated file (`output_name`+".html")
        """
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
    """
    SUMMARY
    a selection of predefined stylers (RouteStyler,ElevationStyler,HistogramStyler).

    STYLES
    hot_pink: [#ffcad4,#ffacc5,#ffacc5]
    after_eights: dark greens [#9db8a1,#547358,#214025]
    fire: reds & orange [#dc2f02,#d00000,#9d0208]
    agua: marine colours (blue & turquoises) [#02c39a,#00a896,#028090]

    USAGE
    for each of the choices above stylers are defined as `style_name`+"_"+`styler_type` where `styler_type` in ["route","elevation","hist","animated_hist"].
    there is a dictionary for each styler containing all the stylers.

    OTHER STYLERS
    `simple_elevation` is an `ElevationStyler` showcasing the elvation plot with no plinth
    """
    # #ffcad4,#ffacc5,#ffacc5
    hot_pink_route=RouteStyler(path_colour="#ff87ab",dash_colour="#ffacc5",animated=True,num_dashes=12)
    hot_pink_elevation=ElevationStyler(path_colour="#ff87ab",dash_colour="#ffacc5",fill_colour="#ffcad4",animated=True,num_dashes=12)
    hot_pink_hist=HistogramStyler(None,stroke_colour="#ff87ab",rect_colour="#ffcad4",font_anchor="end",space_between_bars=0,font_colour="#ff87ab",axis_x_pos=0)
    hot_pink_animated_hist=HistogramStyler(SVGMaker.histogram_animation_bounce,rect_colour="#ff87ab",font_anchor="end",space_between_bars=0,font_colour="#ff87ab",stroke_width=0,text_gap=0)
    hot_pink={"route":hot_pink_route,"elevation":hot_pink_elevation,"hist":hot_pink_hist,"animated_hist":hot_pink_animated_hist}

    # #9db8a1,#547358,#214025
    after_eights_route=RouteStyler(path_colour="#214025",dash_colour="#547358",animated=True,num_dashes=12,start_marker=True,finish_marker=True,split_dist=1000,split_marker_colour="#000")
    after_eights_elevation=ElevationStyler(path_colour="#214025",dash_colour="#547358",fill_colour="#9db8a1",animated=True,num_dashes=12)
    after_eights_hist=HistogramStyler(None,stroke_colour="#547358",rect_colour="#214025",font_anchor="end",space_between_bars=0,font_colour="#9db8a1",axis_x_pos=0)
    after_eights_animated_hist=HistogramStyler(SVGMaker.histogram_animation_bounce,rect_colour="#214025",font_anchor="end",space_between_bars=0,font_colour="#9db8a1",stroke_width=0,text_gap=0)
    after_eights={"route":after_eights_route,"elevation":after_eights_elevation,"hist":after_eights_hist,"animated_hist":after_eights_animated_hist}

    # #dc2f02,#d00000,#9d0208
    fire_route=RouteStyler(path_colour="#dc2f02",dash_colour="#d00000",animated=True,animation_length=1,num_dashes=12,start_marker=True,finish_marker=True,split_dist=1000,split_marker_colour="#000")
    fire_elevation=ElevationStyler(path_colour="#dc2f02",dash_colour="#d00000",fill_colour="#9d0208",animated=True,animation_length=1,num_dashes=12)
    fire_hist=HistogramStyler(None,stroke_colour="#dc2f02",rect_colour="#9d0208",font_anchor="end",space_between_bars=0,font_colour="#d00000",axis_x_pos=0)
    fire_animated_hist=HistogramStyler(SVGMaker.histogram_animation_bounce,rect_colour="#9d0208",font_anchor="end",space_between_bars=0,font_colour="#d00000",stroke_width=0,text_gap=0)
    fire={"route":fire_route,"elevation":fire_elevation,"hist":fire_hist,"animated_hist":fire_animated_hist}

    # #02c39a,#00a896,#028090
    agua_route=RouteStyler(path_colour="#00a896",dash_colour="#028090",animated=True,num_dashes=12,start_marker=True,finish_marker=True,split_dist=1000,split_marker_colour="#000")
    agua_elevation=ElevationStyler(path_colour="#00a896",dash_colour="#028090",fill_colour="#02c39a",animated=True,num_dashes=12)
    agua_hist=HistogramStyler(None,stroke_colour="#00a896",rect_colour="#028090",font_anchor="end",space_between_bars=0,font_colour="#00a896",axis_x_pos=0)
    agua_animated_hist=HistogramStyler(SVGMaker.histogram_animation_bounce,rect_colour="#028090",font_anchor="end",space_between_bars=0,font_colour="#00a896",stroke_width=0,text_gap=0)
    agua={"route":agua_route,"elevation":agua_elevation,"hist":agua_hist,"animated_hist":agua_animated_hist}

    simple_elevation=ElevationStyler(plinth_height=None,fill_colour=None,animated=False)

# to_plot pass a tuple containing (styler,output_name)
def plot_all(file_path:str,plot_html=True,html_output_name="test/many_examples",to_plot={"route":(None,"test/route"),"elevation":(None,"test/elevation"),"histogram":(None,"test/hist"),"animated_histogram":(None,"test/animated_hist")},path_to_remove="test/") -> str:
    """
    SUMMARY
    parses a gps file and generates specified svgs for it

    PARAMETERS
	file_path (str): path to gps file to plot for
    plot_html (bool): whether to generate a html file showcasing all the generated svgs (default=True)
    output_name (str): path & name for generated html file (default="test/many_examples")
    to_plot (dict(str:(Styler,Path))): defines which svg to generate for, the styler to use & path to use.
                                       use options from ["route","elevation","histogram","animated_histogram"] as key to define what svgs to generate.
                                       for values define a tuple (Styler,output_name of generated files). Pass `None` for Styler to use default.
                                       (default={"route":(None,"test/route"),"elevation":(None,"test/elevation"),"histogram":(None,"test/hist"),"animated_histogram":(None,"test/animated_hist")})
   path_to_remove (str): string to remove start of file names in `to_plot` to ensure they are correctly defined relative to html file being generated. (default="test/")

    RETURNS
	str: IF (plot_html): relative path to generated html file
    list(dict): IF (not plot_html): list of dicts specifying files generated for each svg
    """
    reader=GPSReader()
    data,metadata=reader.read(file_path)
    df=reader.data_to_dataframe(data)

    files=[]
    if "route" in to_plot:
        plot_details=to_plot["route"]
        styler=RouteStyler() if (plot_details[0] is None) else plot_details[0]
        new_files=SVGMaker.generate_route_svg(df,route_styler=styler,output_name=plot_details[1])
        files.append(new_files)

    if "elevation" in to_plot:
        plot_details=to_plot["elevation"]
        styler=ElevationStyler() if (plot_details[0] is None) else plot_details[0]
        new_files=SVGMaker.generate_elevation_svg(df,elevation_styler=styler,output_name=plot_details[1])
        files.append(new_files)

    if "histogram" in to_plot:
        plot_details=to_plot["histogram"]
        styler=HistogramStyler() if (plot_details[0] is None) else plot_details[0]
        hist_data=GPSEvaluator.split_histogram_data(df,clean=True)
        new_files=new_files=SVGMaker.generate_histogram(hist_data,hist_styler=styler,output_name=plot_details[1])
        files.append(new_files)

    if "animated_histogram" in to_plot:
        plot_details=to_plot["animated_histogram"]
        styler=HistogramStyler() if (plot_details[0] is None) else plot_details[0]
        hist_data_per_km=GPSEvaluator.split_histogram_data_per_km(df,clean=True)
        new_files=SVGMaker.generate_animated_histogram(hist_data_per_km,hist_styler=styler,output_name=plot_details[1])
        files.append(new_files)

    if plot_html:
        return SVGMaker.generate_html_for_many_svg(files,per_row=2,output_name=html_output_name,path_to_remove=path_to_remove)
    else:
        return files

if __name__=="__main__":
    stylers=DefaultStylers.after_eights
    plots={
        "route":(stylers["route"],"test/route"),
        "elevation":(stylers["elevation"],"test/elevation"),
        "histogram":(stylers["hist"],"test/hist"),
        "animated_histogram":(stylers["animated_hist"],"test/animated_hist")
    }
    print(plot_all("../examples/example_ride.tcx",html_output_name="test/plotted",to_plot=plots,path_to_remove="test/"))
