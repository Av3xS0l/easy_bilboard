# Easy_bilboard
A bilboard app to turn a computer into a digital bilboard.  
Made primarily for linux.

# Running project
## Linux
1. The folowing must be run as root/admin to install the dependencies:  
```sudo ./install.sh```  
2. Set all of the environment variables in `.env` file in project's directory.  
    ```
    FOLDER_ID={google drive folder id}
    LOCAL_PATH={replace with absolute path to folder to store local files
    USE_EXT_DISPLAY={1 to use secondary display; 0 to use the main display}  
    ```
    OPTIONAL:  
    ```
    LAST_INCIDENT={date of the last incident or other counter}  
    ```
3. Run the programm using `./run.sh`
> [!NOTE]  
> In order to start a timer run `./reset.sh`
