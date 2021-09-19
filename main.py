# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from flask import Flask, render_template, request, jsonify, flash, send_from_directory, current_app
from application_logging.AppLogging import AppLog
from DataSource.LoadFromFile import ReadFileToDataFrame
import pandas as pd
from Training.TrainModel import TrainModel
from sklearn.model_selection import GridSearchCV
from sklearn import metrics
import numpy as np
from pandas_profiling import ProfileReport
from Config_Files.readConfigFile import Read_Config_File
from Training.preprocess import datapreprocess
from Config_Files.Utility import GenericValidation
import os

app = Flask(__name__)

exeType = "Training"
applog = AppLog(exeType)
log = applog.log("sLogger")

objReadFile = ReadFileToDataFrame(exeType)

objReadConfigFile = Read_Config_File(log,"Config_Files//Training_schema.json")
FileStatus, ConfigDict = objReadConfigFile.readData()
print(ConfigDict)
objGenericVal = GenericValidation(log=log)

#exeType = ConfigDict.get("exeType")
classifier = ConfigDict["classifier"]
log.info("classifier : {}".format(classifier))

objTrainModel = TrainModel(exeType=exeType)

RawData = pd.DataFrame()
Status = 0

TrainModelPath = ConfigDict["TrainModelPath"] #"Training//Model//"
log.info("TrainModelPath : {}".format(TrainModelPath))

IndependentCol = ConfigDict["IndependentCol"] #'Summary'
log.info("IndependentCol : {}".format(IndependentCol))
TargetCol = ConfigDict["TargetCol"] #IndependentCol #'Owner_Group'
log.info("TargetCol : {}".format(TargetCol))

ModelVer = ConfigDict["ModelVer"] #"1.0"
log.info("ModelVer : {}".format(ModelVer))

DataDir = ConfigDict["DataDir"] #"DataSource//Data"
log.info("DataDir : {}".format(DataDir))
FileName = ConfigDict["ReadFileName"]
log.info("FileName : {}".format(FileName))

SkipRows = ConfigDict["SkipRows"]
log.info("SkipRows : {}".format(SkipRows))

DatasetColumns = ConfigDict["DatasetColumns"]
log.info("DatasetColumns : {}".format(DatasetColumns))

LogsRegSolver = ConfigDict["LogsRegSolver"]
log.info("Logistic Regression Solver : {}".format(LogsRegSolver))

objPreProcData = datapreprocess(exeType)


if ConfigDict["hyperparam"] == "False":
    hyperparam = False
else:
    hyperparam = True #False
log.info("hyperparam : {}".format(hyperparam))

removecolumn = ConfigDict["removecolumn"] #
log.info("removecolumn : {}".format(removecolumn))

@app.route('/', methods=['GET','POST']) # To render Homepage
def home_page():
    return render_template('index.html')

def PrepareDataset():

    if objGenericVal.IsFileAvailable(DataDir+"//"+FileName) == 1:
        os.remove(DataDir+"//"+FileName)

    objReadFile.NavigateDirectory(dirpath=DataDir, skiprows=SkipRows,IndependentCol=IndependentCol, TargetCol=TargetCol, TargetFileName=FileName, TargetDir=DataDir)
    #RawData = pd.read_csv(DataDir+"//"+FileName,names=DatasetColumns)
    #print(RawData)

def Load_Data(exeType='Training'):
    # Use a breakpoint in the code line below to debug your script.

    objReadCSVFile = ReadFileToDataFrame(exeType=exeType)
    log.info("Load the data from file - {} ".format(FileName))
    Status, RawData = objReadCSVFile.ReadCSVData(DirName=DataDir, FileName=FileName, columns=DatasetColumns)
    columnlst = [col for col in RawData.columns]
    print(columnlst)
    print ("Shape of the data is : {}".format(RawData.shape))
    log.info("Shape of the data is : {}".format(RawData.shape))

    GeneratePrifileReport(exeType,Status,RawData)

    return RawData

def GeneratePrifileReport(exeType='Training',Status=0,RawData=None):

    if Status == 1:
        log.info("Initiate to generate the pandas profile report...")
        print("Initiate to generate the pandas profile report...")
        #profile = ProfileReport(RawData,title="Activity Recognition system based on Multisensor")
        #profile.to_file(output_file="static//css//"+"AReM-Master.html")
        log.info("Pandas profile AI4I_2020_Predictive-Maintenance-Dataset.html generated successfully : {}")
    else:
        log.critical("No data found from the file, please check the log file")

    #PreprocessData(exeType,RawData)
    #if exeType == 'Training':
        #TrainingModel(exeType,RawData['ProcessedText'],RawData[TargetCol])

def PreprocessData(exeType=exeType,df=RawData):

    log.info("Initiate to preprocess the data :")
    print("Initiate to preprocess the data :")
    df_data = objPreProcData.dropcolumn(df,ConfigDict["removecolumn"])
    log.info("Column removed : {}".format(ConfigDict["removecolumn"]))
    print("Column removed : {}".format(ConfigDict["removecolumn"]))

    log.info("Initiate to impute the data :")
    print("Initiate to impute the data :")
    for col in df_data.columns[df_data.dtypes==np.number]:
        df_data = objPreProcData.impute_data(df_data,col,'mean')
    #print(df_data.isnull().sum())


    return df_data

def TrainingModel(exeType=exeType):

    try:
        df = Load_Data()
        df = PreprocessData(exeType=exeType,df=df)

        IndependentData = df[IndependentCol]
        TargetData = df[TargetCol]

        Train_Data, Test_Data, Train_Target, Test_Target = objTrainModel.TrainTestSplit(IndependentData,TargetData)

        #Train_Data = objPreProcData.stdscalling(Train_Data)
        print(Train_Data)

        for solver in LogsRegSolver:
            TrainModel = objTrainModel.TrainSupervisedModel(classifier=classifier,IndLabel=Train_Data
                                                            ,TargetLabel=Train_Target, solver=solver)

            print("Initiate to dump the Training model {} with solver {}".format(classifier,solver))
            log.info("Initiate to dump the Training model {} with solver {}".format(classifier,solver))
            objTrainModel.DumpModel(model=TrainModel, dirpath=TrainModelPath, classifier=classifier
                                    , ver=ModelVer, modelIdent=solver)

            #Test_Data = objPreProcData.stdscalling(Test_Data)
            score = TrainModel.score(Test_Data,Test_Target)
            print("Model score with hyperparameter tuning {}".format(score))
            log.info("Model score with hyperparameter tuning {}".format(score))

    except Exception as e:
        log.critical("Exceptin occured, while training the model : {}".format(e))

@app.route("/TestingModel", methods=['GET','POST'])
def TestingModel():

    try:
        classifier = request.form['classifier']
        print(classifier)
        solver = request.form['solver']
        print(solver)
        param1 = request.form['avg_rss12'] +","+request.form['var_rss12']+","+request.form['avg_rss13']+","+request.form['var_rss13']
        param2 = request.form['avg_rss23'] +","+request.form['var_rss23']
        param = param1+","+param2
        param = np.array([float(itm) for itm in param.split(",")])
        print(param)
        model = objTrainModel.LoadModel(classifier=classifier,dirpath=TrainModelPath,hyperparameter=hyperparam,ver=ModelVer,modelIdent=solver)
        print(model)

        #scalled = objPreProcData.stdscalling(param.reshape(1,-1))
        #print(scalled)
        scalled = param.reshape(1,-1)
        '''
        coef = model.coef_
        print(coef)
        intercept = model.intercept_
        print(intercept)
        '''
        predict = ''.join(model.predict(scalled))
        print(predict)
        #document.getElementById("mytext").value = "My value";

    
    except Exception as e:
        log.critical("Exception occured, while getting model result :{}".format(e))
    return render_template('results.html',rheader=classifier+' Model Prediction',predict=predict)
    #return render_template('../DataSource/Reports/AI4I_2020_Predictive-Maintenance-Dataset.html')

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(debug=True)

    #TrainingModel(exeType)
