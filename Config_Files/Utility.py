
import os

class GenericValidation:

    def __init__(self,log):
        self.log = log

    def IsDirectoryAvailable(self, dir=None):

        try:
            DirectoryAvailable = 1
            #print("Checking the available directory path : {}".format(dir))
            if dir == None:
                self.log.info("Directory path is missing as Input argument :")
                DirectoryAvailable = 0
            else:
                if not os.path.exists(dir):
                    self.log.info("Directory is not available in given path : {}".format(dir))

                    DirectoryAvailable = 0

        except Exception as e:
            self.log.critical('Exception occured, while validating the file directory availability : '.format(e))

        return DirectoryAvailable

    def IsFileAvailable(self, filename=None):

        try:
            FileAvailable = 1
            if filename == None:
                self.log.info("File Name is missing as Input argument :")
                FileAvailable = 0
            else:
                if not os.path.isfile(filename):
                    self.log.info("File Name is not available in given path :")
                    FileAvailable = 0

        except Exception as e:
            self.log.critical('Exception occured, while validating the file availability : {}'.format(e))

        return FileAvailable

    def MakeDir(self,dirpath):

        try:

            #dpath = os.path.split(dirpath)
            #print(dirpath)
            dirpath = dirpath.replace("\\","/").replace("//","/")
            dirpath = [x for x in dirpath.split("/") if x]

            #print(dirpath)
            status = 0
            varpath=""
            for dirph in dirpath:
                varpath = varpath+dirph + "//"
                if self.IsDirectoryAvailable(varpath) == 0:
                    os.mkdir(varpath)
                    status = 1

        except Exception as e:
            self.log.critical('Exception occured, while creating the directory : {}'.format(e))

        return status
