"""
This script packages a footprint for each path that exists.
"""
import os
import zipfile
import subprocess
import shutil
import json
import hashlib
import time

PACKAGE_FOLDERS = [
            "resources",
            "symbols",
            "3dmodels"
        ]
PACKAGE_FILES = [
            "metadata.json"
        ]
STATUS_STABLE = "stable"
STATUS_TESTING = "testing"
STATUS_DEVELOPMENT = "development"
STATUS_DEPRECATED = "deprecated"

class packageAddon():
    def __init__(self, currentdir="./", ThirdPartyDirectory="C:/Users/billy/Documents/KICAD/7.0/3rdparty/",ThirdPartyVariable="$\{KICAD7_3RD_PARTY\}"):
        self.THIRD_PARTY = ThirdPartyDirectory
        self.VAR_THIRD_PARTY = ThirdPartyVariable
        self.checkPackageFolders(currentdir)
        self.importPackageInfo()

    def __del__(self):
        print("package object destroyed!")
        self.exportPackageInfo("upload.json")
    def importPackageInfo(self,fileName="metadata.json"):
        f = open(fileName,"r")
        self.metadata = json.load(f)
        f.close()
        #print(self.metadata)
    def exportPackageInfo(self,fileName="metadata.json"):
        f = open(fileName,"w")
        json.dump(self.metadata,f,indent=4)
        f.close()

    def checkPackageFolders(self,currentdir):
        """
        checks currentdir for folders and files to include in the package
        stores the folders , files, and excluded items in the self object.
        """
        current = os.listdir(currentdir)
        self.folders = [i for i in current if i in PACKAGE_FOLDERS]
        self.files = [i for i in current if i in PACKAGE_FILES]
        self.excluded = [i for i in current if i not in PACKAGE_FILES]
        self.excluded = [i for i in self.excluded if i not in PACKAGE_FOLDERS]

    def gitCommit(self,message:str):
        subprocess.run("git commit -m \"{}\"".format(message))
    def gitTag(self,rev:str,message:str):
        subprocess.run("git tag -a {} -m \"{}\"".format(rev,message))
        subprocess.run("git push --tag")
    def copyFolder(self,s:str,d:str):
        shutil.rmtree(d)
        #TODO check if this delets files pointed to by a symlink
        shutil.copy(s,d,follow_symlinks=False)
    def gitPush(self):
        subprocess.run("git push")
    def kicadPush(self):
        pass
    def kicadPull(self):
        pass
    def createArchive(self,outFileName):
        print("creating archive...")
        #update metadata

        #create and submit new git tag for the release.
        # check if folders and files actually exist.


        zf = zipfile.ZipFile(outFileName, "w",compression=zipfile.ZIP_DEFLATED)
        for file in self.files:
            zf.write(file)
        last = 0
        for folder in self.folders:
            print("\r\nProcessing: {}".format(folder))
            for dirname, subdirs, files in os.walk(folder):
                zf.write(dirname)
                print("\r"+" "*last,end="")
                print("\r{}\r".format(dirname),end="")
                last = len(dirname)
                for filename in files:
                    zf.write(os.path.join(dirname, filename),compress_type=zipfile.ZIP_DEFLATED)
        print()
        zf.close()
        zf = zipfile.ZipFile(outFileName, "r",compression=zipfile.ZIP_DEFLATED)
        #size = sum([zinfo.file_size for zinfo in zf.filelist])#zip archive size
        #csize = sum([zinfo.compress_size for zinfo in zf.filelist])#zip compressed size
        zf.extractall("archive")
        zipSize = os.stat(outFileName).st_size
        extract_size = 0
        last =0
        print("finding extracted Size: ")
        for path, dirs, files in os.walk("archive"):
            print("\r"+" "*last,end="")
            print("\rwalking: {}".format(path),end="")
            last = len("walking: {}".format(path))
            for f in files:
                fp = os.path.join(path, f)
                extract_size += os.path.getsize(fp)
        print()
        #estat = os.path.getsize("archive")
        print("folder: {}\r\nzip   : {}\r\nsaved : {}".format(extract_size, zipSize,extract_size-zipSize))
        
        with open(outFileName,"rb") as f:
            h = hashlib.file_digest(f,"sha256")
        self.metadata["versions"][0].update({"download_sha256":h.hexdigest()})
        f.close()
        
        self.metadata["versions"][0].update({
            "download_size": zipSize,
            "install_size": extract_size
            })
        del zf
        print(outFileName)
        time.sleep(1)



if(__name__=="__main__"):
    test = packageAddon()
    test.createArchive("archive.zip")

    del test

