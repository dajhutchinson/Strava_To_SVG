from GPSFileReader import GPSFileReader

class SVGMaker:

    def __scale_with_border(v,min_v,max_v,scale=1,border=0):
        range=1000-2*border
        return int(border+range*scale*(v-min_v)/(max_v-min_v))

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
        lat_lon_data["scaled_lon"]=lat_lon_data["position_lon"].apply(SVGMaker.__scale_with_border,min_v=min_lon,max_v=max_lon,scale=lon_diff/max_diff,border=BORDER).astype(int)
        # TODO plot to svg, add border, line width, colour, distance markers, key?
        lat_lon_data["point_str"]=lat_lon_data.apply(lambda row:"{},{}".format(str(int(row["scaled_lon"])),str(int(row["scaled_lat"]))),axis=1)

        # points=[(BORDER+__scale_0_1000(datum["position_lon"],metadata["min_lon"],metadata["max_lon"],lon_diff/max_diff),BORDER+ceil(1000*(lat_diff/max_diff))-__scale_0_1000(datum["position_lat"],metadata["min_lat"],metadata["max_lat"],lat_diff/max_diff)) for datum in data[lap_name]]
        point_str=" ".join(lat_lon_data["point_str"].tolist())
        end_point_str="{} {}".format(lat_lon_data.iloc[0]["point_str"],lat_lon_data.iloc[-1]["point_str"])

        # write to file
        svg_file=open(output_name+".svg","w+")
        svg_file.write('<svg xmlns="http://www.w3.org/2000/svg" viewbox="0 0 {} {}" width="100%" height="100%" version="1.1">\n'.format(lat_lon_data["scaled_lon"].max()+BORDER,lat_lon_data["scaled_lat"].max()+BORDER))

        # content
        svg_file.write('<path class="route" d="M'+point_str+'z" fill="none" stroke-width="5" stroke-linejoin="round" stroke="'+COLOUR+'"></path>\n')
        svg_file.write('<path class="route_end" d="M'+end_point_str+'z" fill="none" stroke-width="5" stroke="#fff" stroke-linecap="butt"></path>\n') # cover extension
        svg_file.write("</svg>")

        svg_file.close()
        return True

# reader=GPSFileReader()
# maker=SVGMaker()
# data,metadata=reader.read("examples\example_ride.tcx")
# df=reader.data_to_dataframe(data)
# maker.generate_route_svg(df)
