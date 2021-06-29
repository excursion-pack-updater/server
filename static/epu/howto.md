<style type="text/css">
main
{
    font-family:  sans-serif;
}

ol > li
{
    line-height: 1.75em;
}

ol ul li
{
    line-height: initial;
}

ol img
{
    vertical-align: middle;
}
</style>

## MultiMC Installation
0. Download [MultiMC](https://multimc.org/#Download%20%26%20Install) zip
0. Extract the `MultiMC` folder in the zip somewhere
    * Can be on your Desktop, in Documents, wherever
0. Launch MultiMC.exe in this folder (optionally, make shortcuts)
0. Click *change settings* ![](https://github.com/MultiMC/MultiMC5/raw/develop/application/resources/multimc/22x22/settings.png "Change settings")
0. Select the Java tab
0. Set your minimum, maximum and PermGen memory limits
    * Recommended values are:
        * At least 4096 MB (4 GB) for __maximum allocation__
        * Minimum allocation should match the value for __maximum allocation__
        * PermGen is unused as of Java 8, so you can ignore it
0. Ensure `Java path` is valid
    * Note that MultiMC does not ship with Java, unlike the official Minecraft launcher. [AdoptOpenJDK](https://adoptopenjdk.net/) is recommended
    * Minecraft versions 1.16 and below require **Java 8**. 1.17 and up require **Java 16**.

## Instance Installation
0. Launch MultiMC
0. Click *add instance* ![](https://raw.githubusercontent.com/MultiMC/MultiMC5/develop/application/resources/multimc/22x22/new.png "Add instance")
0. Name the instance accordingly (makes folders) and (optionally) set group
    * Game version does not matter, will be set after extracting instance zip
0. Hit OK, right click the new instance and select Instance Folder
0. Download and extract instance.zip into this folder, overwriting if necessary. Your folder structure should look something like this:
    * `MultiMC/instances/InstanceName`
        * `pack_sync.exe`
        * `instance.cfg`
        * `minecraft/`
            * `pack_sync.ini`
0. Go back to MultiMC and click *refresh* ![](https://raw.githubusercontent.com/MultiMC/MultiMC5/develop/application/resources/multimc/22x22/refresh.png "Refresh") in the lower right
0. (optional, but recommended) Set memory options (See MultiMC Setup below)
0. Double click on the instance to launch it
0. Have a cup of tea while the instance downloads and launches

## Updating Forge or Fabric
0. Right click the instance
0. Select "Edit Instance"
0. Go to the "Version" tab (if it's not selected already)
    * If it's missing, try restarting MultiMC (weird bug)
0. Click "Install Forge" OR "Install Fabric"
    * If you're unsure which the pack is using, look at the list of versions already present. Forge is simply named "Forge", Fabric will be named "Fabric Loader"
0. Select the topmost version with a gold star ![](https://raw.githubusercontent.com/MultiMC/MultiMC5/develop/application/resources/multimc/16x16/star.png "Gold star") next to it
0. The new version of Forge/Fabric will be applied at next launch
