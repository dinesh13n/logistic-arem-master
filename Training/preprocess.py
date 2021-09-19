from application_logging.AppLogging import AppLog
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

class datapreprocess:

    def __init__(self,exeType='Training'):
        self.exeType = exeType

        self.applog = AppLog(self.exeType)
        self.log = self.applog.log("sLogger")

    def dropcolumn(self, df, columnname):

        try:
            self.log.info("Initiate to drop {} column from the dataset".format(columnname))
            df.drop(columns=columnname,axis=0,inplace=True)
            self.log.info("Successfully drop the {} column from the dataset".format(columnname))
        except Exception as e:
            self.log.critical("Exception occoured, while droping the {} column from dataset : {}".format(columnname,e))
        return df


    def stdscalling(self,df):

        try:
            print(df)
            # define standard scaler
            scaler = StandardScaler()
            # transform data
            scaled = scaler.fit_transform(df)

        except Exception as e:
            self.log.critical("Exception occoured, while scalling the dataframe dataset : {}".format(e))

        return scaled

    def impute_data(self,df,variable,imp_type):

        try:

            if imp_type == 'mean':
                df[variable] = df[variable].fillna(df[variable].mean())
            elif imp_type == 'median':
                df[variable] = df[variable].fillna(df[variable].median())
            elif imp_type == 'mod':
                df[variable] = df[variable].fillna(df[variable].mod(1,fill_value=0))
            elif imp_type == 'constant':
                df[variable] = df[variable].copy()
                data_imputer = SimpleImputer(strategy=imp_type)
                df[variable] = data_imputer.fit_transform(df[variable])
            else:
                self.log.info('Selected method {} is wrong'.format(imp_type))

        except Exception as e:
            self.log.info("Exception occured, while impute the data".format(e))

        return df