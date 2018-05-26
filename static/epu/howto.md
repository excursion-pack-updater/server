# EPU
## Downloads
* [MultiMC](https://multimc.org/#Download%20%26%20Install)

## Instructions
### Installation
0. Download and install MultiMC
0. Download the instance zip
0. Launch MultiMC
0. Click ![Open instance folder](https://raw.githubusercontent.com/MultiMC/MultiMC5/develop/application/resources/multimc/22x22/viewfolder.png "Open instance folder")
0. Extract instance.zip here
0. Go back to MultiMC and click ![Refresh](https://raw.githubusercontent.com/MultiMC/MultiMC5/develop/application/resources/multimc/22x22/refresh.png "Refresh")
0. Click ![Change settings](https://github.com/MultiMC/MultiMC5/raw/develop/application/resources/multimc/22x22/settings.png "Change settings")
0. Select the Java tab
0. Set your minimum, maximum and PermGen memory limits
    * Recommended values are:
        * At least 1024 MB (1 GB) for minimum allocation
        * At least 4096 MB (4 GB) for maximum allocation
        * 512 MB for PermGen
            * If you're running Java 8 or newer, this does not matter
    * Ensure `Java path` is valid
0. Double click the ender pearl to launch the pack
    * The first launch will take unusually long, as the updater will download the entire pack

### Updating Forge
You should do this every so often, just to be safe.

0. Right click the instance
0. Select "Edit Instance"
0. Go to the "Version" tab (if it's not selected already)
    * If it's missing, try restarting MultiMC (weird bug)
0. Click "Install Forge"
0. Select the topmost version with a ![Gold star](https://raw.githubusercontent.com/MultiMC/MultiMC5/develop/application/resources/multimc/16x16/star.png "Gold star") next to it
0. The new version of Forge will be applied at next launch
