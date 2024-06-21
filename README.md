# Koboldcpp_Launcher
Simple wrapper GUI for Koboldcpp (Requires the Koboldcpp executable and gguf models.).

# What does it do?
This is a simple Launcher to make it easier to hot swap GGUF models in Koboldcpp. It simply launches the Koboldcpp executable with the commandline arguments. Just select the model from the dropdown and click launch. It will open a new command window for koboldcpp. Meanwhile the Launcher remains open in the background. When you want to swap models, just close the command window, select a different model in the Launcher and voila, another instance of Koboldcpp without all the hassle.

# Why?
I found it tiresome to have to launch the koboldcpp application and load the settings each time I wanted to swap to a different model. Most of the time, I didn't even need to change the run parameters, just the model. So after wasting many many hours of my precious time, we have this Launcher here that will save you the 10-20 seconds you would otherwise waste trying to reload a new model in Koboldcpp. You're welcome.

There's probably an easier way to do this but well, I couldn't find it. So here you go.

# How to Use
Open the Launcher. You might see a popup saying there's no folder in the selected location. You can ignore that for now. In the 'quick launch' menu, set the root directory where you have the gguf model files and select the Koboldcpp executable file. 
The 'update model list' option will populate the dropdown list with all the gguf files in the root directory and its subfolders.

![image](https://github.com/Daniel-Dan-Espinoza/Koboldcpp_Launcher/assets/92890439/561812c7-d5c8-4f98-b0df-122215af04f5)

The 'favorite model' option will add the selected model as a quick launch shortcut at the bottom of the Launcher.

![image](https://github.com/Daniel-Dan-Espinoza/Koboldcpp_Launcher/assets/92890439/6bb99bff-abe8-4cd9-bc79-aa6719145264)

The 'hardware' menu has some of the common Koboldcpp model configurations. 

![image](https://github.com/Daniel-Dan-Espinoza/Koboldcpp_Launcher/assets/92890439/cac8ce79-ca77-4148-86e9-f34d528318ed)

The 'save config' option saves all the current settings in a json file. This config will be loaded automatically each time the Launcher is opened, or manually using the 'load config' option. The 'launch' option serves the same purpose as the 'load model' option and launches the Koboldcpp executable with the selected configuration. The launch parameters and endpoint are displayed in the 'quick launch' menu.

![image](https://github.com/Daniel-Dan-Espinoza/Just_Another_KoboldCpp_Launcher/assets/92890439/cc0714da-a922-4013-9d60-9b1b91f21272)

