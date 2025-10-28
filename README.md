# Easy_bilboard
A bilboard app to turn a computer into a digital bilboard.  
Made primarily for linux. Other platforms are not tested.

# Running project
## Linux

1. The folowing must be run as administrator to install the dependencies:  
`sudo ./install.sh`
> Currently the install script only supports Debian and Arch linux based systems!
2. Add folowing environment variables to ./.env file:  
`FOLDER_ID=...` ID of your google drive folder to sync from    
`LOCAL_PATH=...` Path that will be used to store the images locally  
`USE_EXT_DISPLAY=...` 1 to use secondary display, 0 to use the primary one  
3. Log into your google cloud console and download the oauth token as credentials.json and put it into the main folder. (On how to do this follow the google's [Instructions](https://developers.google.com/workspace/drive/api/quickstart/python#authorize_credentials_for_a_desktop_application) )  
4. Run the programm for the first time using `run.sh` file and authorize your project to your google drive.
5. Now just put the files you want to show in the google drive folder and run the programm using `run.sh`. The files will update automatically as you add or remove them from the google drive folder - no need to restart the programm.