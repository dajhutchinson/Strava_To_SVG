
from datetime import datetime
import pandas as pd
from math import floor
import sys

from geopy.distance import geodesic
from GPSReader import GPSReader

# Evlauates data generated by GPSReader
class GPSEvaluator:

    """
    HELPERS
    """
    # returns distance covered between pair of (lat,lon) points
    # p=(lat,lon)
    def __distance_lat_lon(p1,p2) -> float:
        return geodesic(p1,p2).meters

    """
    EVALUATE DATA
    """
    # return pd.Series of distance between consequtive lat,lon points
    def distance(df:pd.DataFrame) -> pd.Series:
        if ("position_lat" in df.columns) and ("position_lon" in df.columns):
            lat_lon=df[["position_lat","position_lon"]].copy()
            prev_lat_lon=pd.concat([lat_lon.head(1).copy(),lat_lon.iloc[:-1,:].copy()],ignore_index=True)
            #print(prev_lat_lon["position_lat"])
            lat_lon["prev_lat"]=prev_lat_lon["position_lat"]
            lat_lon["prev_lon"]=prev_lat_lon["position_lon"]

            lat_lon["distance"]=lat_lon.apply(lambda x:GPSEvaluator.__distance_lat_lon((x["position_lat"],x["position_lon"]),(x["prev_lat"],x["prev_lon"])),axis=1)
            return lat_lon["distance"]
        return None

    # calculate cummulative distance from start to point
    def cumm_distance(df:pd.DataFrame) -> pd.Series:

        if ("distance" in df.columns): dists=df["distance"]
        elif ("position_lat" in df.columns) and ("position_lon" in df.columns): dists=GPSEvaluator.distance(df)
        else: return None # not enough data

        return dists.cumsum().apply(lambda x:round(x,2))

    # returns time as number of seconds from start
    def time_to_seconds(df:pd.DataFrame) -> pd.Series:
        if "time" in df:
            times=df["time"]
            start_time=times[0]
            return times.apply(lambda x:(x-start_time).seconds).astype(int)
        else: # not enough data
            return None

    # interpolates time between each dist (chops off any overflow)
    def splits(df:pd.DataFrame,split_dist=1000) -> pd.DataFrame:
        # check data
        if "cumm_distance" not in df.columns:
            cumm_dists=GPSEvaluator.cumm_distance(df)
            if cumm_dists is None: return None # not enough data
            df["cumm_distance"]=cumm_dists
        if "seconds" not in df.columns:
            seconds=GPSEvaluator.time_to_seconds(df)
            if seconds is None: return None
            df["seconds"]=seconds

        data=df[["seconds","cumm_distance"]].copy()
        targ_dist=split_dist
        prev_time=0; splits=pd.DataFrame(columns=["dist","time"])

        for _,row in data.iterrows():
            if row["cumm_distance"]>=targ_dist:
                # record values
                split_time=row["seconds"]-prev_time
                new_row=pd.DataFrame({"dist":[targ_dist],"time":split_time})
                splits=splits.append(new_row,ignore_index=True)

                # set up for next split
                targ_dist+=split_dist
                prev_time=row["seconds"]

        return splits

    # calculate histogram of splits (bin_width:seconds,sampling_dist:metres)
    # clean=runs clean_histogram_data with default values
    def split_histogram_data(df:pd.DataFrame,bin_width=10,sampling_dist=100,clean=False) -> pd.Series:
        # bins=pd.DataFrame(columns=["lower","upper","count"])

        split_data=GPSEvaluator.splits(df,split_dist=sampling_dist)["time"] # generalise data
        split_data=split_data.apply(lambda x:x*(1000/sampling_dist)).astype(int) # extrapolate km splits

        bins={val:0 for val in range(floor(split_data.min()/bin_width)*bin_width,split_data.max()+1,bin_width)}
        for _,val in split_data.iteritems():
            lower_bound=floor(val/bin_width)*bin_width
            bins[lower_bound]+=1

        bins_ser=pd.Series(bins)
        if clean: return GPSEvaluator.__clean_histogram_data(bins_ser)
        return bins_ser

    # keeps densiest cluster whichc contains min_kept% of all values
    def __clean_histogram_data(splits:pd.Series,min_kept=.9) -> pd.Series:
        clusters=[] # lower & upper values of clusters
        cluster_mass={} # count what % of data cluster holds
        total_mass=splits.sum()

        lower=splits.index[0]; in_cluster=True; mass=0; prev=None # prepare to record clusters
        for bound,count in splits.iteritems():
            mass+=count # mass of current cluster
            if (count==0) and (in_cluster): # end of cluster
                clusters.append((lower,prev))
                cluster_mass[(lower,prev)]=mass/total_mass
                mass=0
                in_cluster=False
            elif (count!=0) and (not in_cluster): # start of cluster
                lower=bound
                in_cluster=True
            prev=bound

        if (in_cluster): # if last cluster runs over end of list
            clusters.append((lower,prev))
            cluster_mass[(lower,prev)]=mass/total_mass

        # keep adding largest cluster until min_kept proportion is met
        min_kept=min(1,min_kept)
        new_splits=pd.Series(); stored_mass=0
        while stored_mass<min_kept: # keep adding largest clusters
            biggest_cluster=max(cluster_mass,key=cluster_mass.get)
            new_splits=new_splits.append(splits.loc[biggest_cluster[0]:biggest_cluster[1]])
            stored_mass+=cluster_mass[biggest_cluster]
            del cluster_mass[biggest_cluster] # so cannot be added again

        # fill in gaps
        width=splits.index[1]-splits.index[0]
        for i in range(new_splits.index.min(),new_splits.index.max(),width):
            if (i not in new_splits.index): new_splits=new_splits.append(pd.Series([0],index=[i]))
        new_splits=new_splits.sort_index()

        return new_splits

    # generate histogram data for each km and returns df with kms as columns and splits as rows
    def split_histogram_data_per_km(df:pd.DataFrame,bin_width=10,sampling_dist=100,clean=False) -> pd.DataFrame:
        if (1000%sampling_dist!=0): return None # non-equal samples per km

        split_data=GPSEvaluator.splits(df,split_dist=sampling_dist)["time"] # generalise data
        split_data=split_data.apply(lambda x:x*(1000/sampling_dist)).astype(int) # extrapolate km splits

        samples_per_km=int(1000/sampling_dist)
        num_kms=floor(len(split_data)/samples_per_km)

        bins={val:0 for val in range(floor(split_data.min()/bin_width)*bin_width,split_data.max()+1,bin_width)}
        rows=[]
        for i in range(num_kms+1):
            local_bins=bins.copy()
            slice=split_data.iloc[i*samples_per_km:(i+1)*samples_per_km]
            for _,split in slice.iteritems(): local_bins[split]+=1
            rows.append(local_bins)

        split_df=pd.DataFrame(rows,index=["km_{}".format(i+1) for i in range(num_kms+1)]).transpose() #columns=["km_{}".format(i+1) for i in range(num_kms+1)]

        if clean: return GPSEvaluator.__clean_def_histogram_data_per_km(split_df)
        return split_df

    # keeps densiest cluster whichc contains min_kept% of all values
    def __clean_def_histogram_data_per_km(df:pd.DataFrame,min_kept=.9) -> pd.Series:
        clusters=[]; cluster_mass={}
        total_mass=df.values.sum()

        lower=df.index[0]; in_cluster=True; mass=0; prev=None # prepare to record clusters
        for bound,row in df.iterrows():
            count=row.sum()
            mass+=count # mass of current cluster
            if (count==0) and (in_cluster): # end of cluster
                clusters.append((lower,prev))
                cluster_mass[(lower,prev)]=mass/total_mass
                mass=0
                in_cluster=False
            elif (count!=0) and (not in_cluster): # start of cluster
                lower=bound
                in_cluster=True
            prev=bound

        if (in_cluster): # if last cluster runs over end of list
            clusters.append((lower,prev))
            cluster_mass[(lower,prev)]=mass/total_mass

        # keep adding largest cluster until min_kept proportion is met
        min_kept=min(1,min_kept)
        new_df=pd.DataFrame(); stored_mass=0
        while stored_mass<min_kept: # keep adding largest clusters
            biggest_cluster=max(cluster_mass,key=cluster_mass.get)
            new_df=pd.concat([new_df,df.loc[biggest_cluster[0]:biggest_cluster[1]]])
            stored_mass+=cluster_mass[biggest_cluster]
            del cluster_mass[biggest_cluster] # so cannot be added again

        # fill in gaps
        width=df.index[1]-df.index[0]
        empty_row=[0 for _ in range(df.shape[1])]
        for i in range(new_df.index.min(),new_df.index.max(),width):
            if (i not in new_df.index): new_df=new_df.append(pd.Series(empty_row,name=i,index=new_df.columns))
        new_df=new_df.sort_index()

        return new_df

if __name__=="__main__":
    reader=GPSReader()
    data,metadata=reader.read("examples\Run_from_Exam.tcx")
    df=reader.data_to_dataframe(data)

    # df["seconds"]=GPSEvaluator.time_to_seconds(df)
    # df["distance"]=GPSEvaluator.distance(df)
    # df["cumm_distance"]=GPSEvaluator.cumm_distance(df)

    # hist_data=GPSEvaluator.split_histogram_data(df,clean=True)
    hist_data=GPSEvaluator.split_histogram_data_per_km(df,clean=True)
    print(hist_data)
