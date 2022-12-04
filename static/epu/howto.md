<style type="text/css">
main
{
    font-family:  sans-serif;
    background-color: #c3c3c3;
}

li
{
    line-height: 1.75em;
}

/* ol ul li
{
    line-height: initial;
} */

ol img
{
    vertical-align: middle;
}

span.symbol
{
    font-size: 125%;
}
</style>

## MultiMC Installation & Configuration
0. Download the appropriate [MultiMC archive](https://multimc.org/#Download)
0. Extract the archive
    * **Windows**:
        0. Extract the `MultiMC` folder in the zip somewhere
            * Can be on your Desktop, in Documents, wherever
        0. (optional) Make a desktop/taskbar shortcut to MultiMC.exe
        0. Launch MultiMC.exe
    * **Mac**:
        0. Open the .tar.gz, this should open the Downloads folder in Finder
        0. Move the MultiMC app into Applications folder
        0. Open MultiMC (protip: <span class="symbol">&#x2318;</span>+Space) but it will give an error
        0. Go to (Apple icon >) System Preferences > Security & Privacy > General
        0. You should see [a message explaining why](https://support.apple.com/library/content/dam/edam/applecare/images/en_US/macos/Big-Sur/macos-big-sur-system-prefs-security-general-open-anyway.png) MultiMC was blocked, click the Open Anyway button
        0. MultiMC should open, and will launch normally in the future
0. The built-in setup wizard should appear
0. Select your language
0. Ensure that MultiMC has detected a compatible version of Java
    * MultiMC does not ship with Java, unlike the official Minecraft launcher. [AdoptOpenJDK](https://adoptopenjdk.net/) provides easy downloads
    * Minecraft versions 1.16 and below require **Java 8**. 1.17 and up require **Java 16**.
0. Set memory limits
    * Recommended values are:
        * **maximum allocation**: 2048-4096 MB (2-4GB) are sane defaults for small to medium sized packs, larger packs may need more.
            In such cases you may prefer to set this per instance, see note in installation instructions below.
        * **minimum allocation**: same as maximum, setting it lower can make the GC more aggressive, often resulting in lag
0. Disable analytics if desired
0. The main window should now be open
0. Click *Settings* ![](https://github.com/MultiMC/MultiMC5/raw/develop/application/resources/multimc/22x22/settings.png "Settings") > Account
    &mdash; or the grayed out Steve head > Manage Accounts
0. Click Add and enter your Mojang account credentials
0. Close the settings window. Click the cat next to the Patreon button :P
0. You're all set to install some packs!

## Pack Installation
Unfortunately MultiMC's built in import feature mucks up permissions, so packs need to be installed somewhat manually.

0. Download the appropriate pack .zip for your OS (from this site)
0. Open the main MultiMC window
0. Click *Folders* ![](https://raw.githubusercontent.com/MultiMC/MultiMC5/develop/application/resources/multimc/22x22/viewfolder.png "Folders") > View Instance Folder
    (confusingly named, this actually opens the instance<u>s</u> folder)
0. Extract the folder from the zip into this one. Your folder structure should end up looking like this:
    * `<MultiMC root>/instances/<pack name>/`
        * `epu_client(.exe)`
        * `instance.cfg`
        * `.minecraft/`
            * `epu_client.json`
0. Go back to MultiMC and it should automatically refresh, showing the new pack. A restart will fix it otherwise
0. If required for the given pack, set overrides for memory options with (right click or sidebar >) Edit Instance > Settings sidebar tab > Java tab
0. Double click on the instance to launch it
0. Have a cup of tea while the instance downloads and launches

## Updating Forge or Fabric
0. Right click the instance
0. Select "Edit Instance"
0. Go to the "Version" sidebar tab (if it's not selected already)
    * If it's missing, try restarting MultiMC (weird bug)
0. Click "Install Forge" OR "Install Fabric"
    * If you're unsure which the pack is using, look at the list of versions already present. Forge is simply named "Forge", Fabric will be listed as "Fabric Loader"
0. Unless you've been told you should install an exact version, select the topmost version with a gold star ![](https://raw.githubusercontent.com/MultiMC/MultiMC5/develop/application/resources/multimc/16x16/star.png "Gold star") next to it
0. The new version of Forge/Fabric will be applied at next launch
