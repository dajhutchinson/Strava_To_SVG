"""
    TODO
    other data sources (cadence etc)
"""
from datetime import datetime
import pandas as pd
import sys

"""
The difference between gpx & tcx data is that tcx includes calculation of distance to point
"""

class GPSReader:

    # read datafiles to dictionaries
    def read(self,path:str) -> (list(dict),dict):
        """
        SUMMARY
        Parse data from gps files.
        Supports .tcx and .gpx files

        PARAMETERS
	    path (str): path to file to read

        RETURNS
	    list(dict): dictionary of data extracted from each reading
        dict: metadata
        """
        extension=path[-4:]
        if (extension==".gpx"): return self.read_gpx(path)
        if (extension==".tcx"): return self.read_tcx(path)
        return -1, -1 # unrecognised file type

    def read_gpx(self,path:str) -> (list(dict),dict):
        """
        SUMMARY
        Parse data from .gpx files.

        PARAMETERS
	    path (str): path to file to read

        RETURNS
	    list(dict): dictionary of data extracted from each reading
                    fields include ["position_lat":float,"position_lon":float,"altitude":float,"time":datetime.datetime,"hr":int]
        dict: metadata
              fields include ["sport":str,"date":datetime.datetime]
        """
        f=open(path,"r")
        it=iter(f) # iterate line by line
        data=[]; metadata={}
        in_metadata=False; datum={}
        type_dict={1:"Cycling",9:"Running"}

        for line in it:
            line=line.strip("\n").strip() # Remove trailing new line and preceeding white spaces

            if "</trkpt>" in line: # end of gpspoint
                data.append(datum)
            elif "<trkpt" in line: # start of gpspoint (lat,lon)
                datum={}
                spl=line.split("\"")
                datum["position_lat"]=float(spl[1])
                datum["position_lon"]=float(spl[3])
            elif "<ele>" in line:
                elevation=line.replace("<ele>",'').replace("</ele>",'')
                datum["altitude"]=float(elevation)
            elif "<time>" in line:
                time=datetime.strptime(line.replace("<time>","").replace("</time>",""),"%Y-%m-%dT%H:%M:%SZ")
                if in_metadata: metadata["date"]=time
                else: datum["time"]=time
            elif "<gpxtpx:hr>" in line:
                hr=line.replace("<gpxtpx:hr>",'').replace("</gpxtpx:hr>",'')
                datum["heart_rate"]=int(hr)
            elif "<type>" in line:
                type=int(line.replace("<type>","").replace("</type>",""))
                if type in type_dict: metadata["sport"]=type_dict[type]
                else: metadata["sport"]=type
            elif "<metadata>" in line:
                in_metadata=True
            elif "</metadata>" in line:
                in_metadata=False

        return data,metadata

    def read_tcx(self, path) -> (list(dict),dict):
        """
        SUMMARY
        Parse data from .tcx files.

        PARAMETERS
	    path (str): path to file to read

        RETURNS
	    list(dict): dictionary of data extracted from each reading
                    fields include ["position_lat":float,"position_lon":float,"altitude":float,"time":datetime.datetime,"distance_to_point":float,"hr":int]
        dict: metadata
              fields include ["sport":str,"date":datetime.datetime]
        """
        f=open(path,"r")
        it=iter(f)

        data=[]; metadata={};
        trackpoints=False

        for line in it:
            line=line.strip("\n").strip() # Remove trailing new line and preceeding white spaces

            # Activity Metadata
            if "<Activity" in line:
                metadata["sport"]=line.strip('<Activity Sport="').rstrip('">"')
            elif "<Id>" in line and "</Id>" in line:
                date_str=line.replace("<Id>","").replace("</Id>","")
                metadata["date"]=datetime.strptime(date_str,"%Y-%m-%dT%H:%M:%SZ")

            # Lap data
            elif "<Track>" in line:
                trackpoints=True
            elif "</Track>" in line:
                trackpoints=False
            elif trackpoints and "<Trackpoint>" in line:
                datum={}
            elif trackpoints and "</Trackpoint>" in line:
                data.append(datum)
            elif trackpoints and "<Time>" in line and "</Time>" in line:
                datum["time"]=datetime.strptime(line.replace("<Time>","").replace("</Time>",""),"%Y-%m-%dT%H:%M:%SZ")
            elif trackpoints and "<Position>" in line:
                line=next(it)
                lat=float(line.strip().replace("<LatitudeDegrees>","").replace("</LatitudeDegrees>",""))
                line=next(it)
                lon=float(line.strip().replace("<LongitudeDegrees>","").replace("</LongitudeDegrees>",""))
                line=next(it)

                datum["position_lat"]=lat
                datum["position_lon"]=lon

            elif trackpoints and "<AltitudeMeters>" in line and "</AltitudeMeters>" in line:
                datum["altitude"]=float(line.replace("<AltitudeMeters>","").replace("</AltitudeMeters>",""))
            elif trackpoints and "<DistanceMeters>" in line and "</DistanceMeters>" in line:
                datum["distance_to_point"]=float(line.replace("<DistanceMeters>","").replace("</DistanceMeters>",""))
            elif trackpoints and "<HeartRateBpm>" in line:
                line=next(it)
                datum["heart_rate"]=int(line.strip().replace("<Value>","").replace("</Value>",""))

        return data,metadata

    def data_to_dataframe(self,data):
        """
        SUMMARY
        Convert data from GPSReader.read, GPSReader.read_gpx or GPSReader.read_tcx to pandas.DataFrame

        PARAMETERS
	    parameter (list(dict)): data from GPSReader.read, GPSReader.read_gpx or GPSReader.read_tcx

        RETURNS
	    pandas.DataFrame: dataframe for passed data
        """
        return pd.DataFrame(data)

if __name__=="__main__":
    reader=GPSReader()
    data,metadata=reader.read("../examples/example_ride.tcx")
    df=reader.data_to_dataframe(data).head()
    print(df.dtypes)
