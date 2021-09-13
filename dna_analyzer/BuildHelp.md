# How to Build the Project
## Step 1
 - Login to any DNAC and create directory dna_analyzer
 - Go inside the directory 
 
 ## Step 2 
 Create and Activate virtual env.
 - Install Virtual Env package
    ```
     pip install virtualenv
     virtualenv -p python dna-analyzer-virtual
     source dna-analyzer-virtual/bin/activate
     pip install --upgrade pip
     pip install --upgrade 'setuptools<45.0.0'
    
 ## Step 3
 -  Install pyinstaller and dependent packages
  ```
    pip install pyinstaller==3.6
    pip install requests
  ```

## Step 4
  -  Copy the whole code into dna_analyzer directory using some file transfer
  -  Clean the project
     ````
     find . | grep -E "(pycache|.pyc$)" | xargs rm -rf
  - Build the Project
    ````
     pyinstaller DNA_Analyzer.py --onefile
  - Find the distribution directory contains the Runtime of the script.
   