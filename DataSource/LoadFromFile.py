
import os
from application_logging.AppLogging import AppLog
import pandas as pd
from Config_Files.Utility import GenericValidation


class ReadFileToDataFrame:

    def __init__(self, exeType='Training'):

        self.exeType = exeType

        self.applog = AppLog(self.exeType)
        self.log = self.applog.log("sLogger")

        self.GenValidation = GenericValidation(self.log)

    def ReadCSVData(self,DirName=None,FileName=None, Separator=',', skiprows=0, columns=None):

        try:
            Data = 'No Data'
            Status = 0
            if FileName != None:
                if self.GenValidation.IsDirectoryAvailable(DirName) == 1:

                    filepath = DirName + '\\'+ FileName
                    self.log.info('File path to read file : {}'.format(filepath))

                    if self.GenValidation.IsFileAvailable(filepath) == 1:
                        if columns == None:
                            Data = pd.read_csv(filepath,sep=Separator, skiprows=skiprows)
                        else:
                            Data = pd.read_csv(filepath,sep=Separator, skiprows=skiprows, names=columns)

                        Status = 1
        except Exception as e:
            self.log.critical("Exception occured, while reading the data from file : ".format(e))

        return Status, Data

    def NavigateDirectory(self, dirpath, skiprows,IndependentCol, TargetCol, TargetFileName, TargetDir):

        try:

            self.log.info("Initiate navigating folder path - {}".format(dirpath))
            print("Initiate navigating folder path - {}".format(dirpath))
            print(os.listdir(dirpath))
            #dirpath = dirpath
            for dirname in os.listdir(dirpath):
                if os.path.isdir(dirpath+"//"+dirname):
                    self.log.info("Find the {} folder inside the directory path {} ".format(dirname,dirpath))
                    print("Find the {} folder inside the directory path {} ".format(dirname,dirpath))
                    self.NavigateDirectory(dirpath=dirpath+"//"+dirname, skiprows=skiprows,IndependentCol=IndependentCol, TargetCol=TargetCol, TargetFileName=TargetFileName, TargetDir=TargetDir)

                elif os.path.isfile(dirpath+"//"+dirname):
                    if dirname.lower().endswith('.csv'):
                        self.log.info("Find the {} file inside the directory path {} ".format(dirname,dirpath))
                        print("Find the {} file inside the directory path {} ".format(dirname,dirpath))

                        self.log.info("Path to create on target directory is {} ".format(TargetDir+"//"+TargetFileName))
                        print("Path to create on target directory is {} ".format(TargetDir+"//"+TargetFileName))

                        #if self.GenValidation.IsFileAvailable(TargetDir+"//"+TargetFileName)==1:
                        status, df_data = self.ReadCSVData(DirName=dirpath, FileName=dirname, skiprows=skiprows, columns=None)
                        #else:
                        #    status, df_data = self.ReadCSVData(DirName=dirpath, FileName=dirname, skiprows=skiprows, columns=IndependentCol)

                        self.log.info("Initiate to write {} filename ".format(dirname))
                        print("Initiate to write {} filename ".format(dirname))
                        #print(os.path.normpath(dirpath).split(os.sep)[-1])
                        df_data.insert(len(IndependentCol), TargetCol, os.path.normpath(dirpath).split(os.sep)[-1])
                        df_data.insert(len(IndependentCol)+1, "FileName", dirname)

                        self.WriteCSVFile(df=df_data, dirpath=TargetDir, FileName=TargetFileName)

        except Exception as e:
            self.log.critical("Exception occured, while navigating directory - {}".format(e))

        #return df_data

    def WriteCSVFile(self, df,dirpath, FileName=None):

        try:
            if FileName != None:
                with open(dirpath+"//"+FileName, 'a') as fp:
                    dfToCSV = df.to_csv(header=False,index=False,line_terminator='\n',)
                    fp.write(dfToCSV)

        except Exception as e:
            self.log.critical("Exception occured to write the file {}".format(e))