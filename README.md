# Multi Seed World Preloader for Minecraft
Purpose of this script is to find nice seeds for your Minecraft server.

Features:
* create lists with wast amount of seeds based on e.g. your name
* automatically setup Minecraft servers for each seed
* automatically preload Chunks in configurable region for each server
* CPU load throtteling -> preload adapts to CPU load of your PC
* progress storage in case Java crashes -> easy restart and continue
* no modifications to world files, no extra mod or datapack
  -> your world is clean and ready to use afterwards
* Python based -> should run on every OS that support Minecraft servers

Under normal circumstances you would use [Amidst](https://github.com/toolbox4minecraft/amidst) for this task, but for early development releases or after bigger changes to Minecraft code, no working Amidst release may be available. This approach is a million times slower, but should work with any Minecraft version, even modded ones.

You can use [Minutor](https://github.com/mrkite/minutor) to create Biome colored maps.


## Usage
First steps are to prepare the `template` folder. This folder has to contain everything to start a Minecraft server.
* download the version of `minecraft_server.jar` you intend to use
* change `eula.txt`. Attention, you accept the EULA from Mojang with this step!

In case you plan to use modded server, place any datapack, mods or folder structures directly into the template folder. It will be copied completely to the new work destination.

Next is to prepare a list of seeds. They have to be in `seeds.txt`.
Simple Example for Ann and Bob who try to find a nice seed based on their names:
```
> seed_generators\SeedFromNameParts_FuLlCasE.py Ann Bob > seeds.txt
```
Now start the world generation process. This will take a very long time. (Linux example)
```
> nohup python3 SeedPreloader.py &
```
Restart with the same command in case Java crashes.

Finaly you can use Minutor to render images from your world. (Windows example)
```
> cd work
> create_images.bat
```


## License
* You are free to use this software for private purpose.
* I guarantee for nothing: functionality, physical damage, injury or harm you may take.
* In case you want to use this software in commercial environment, contact me.
* Redistribution of code is not permitted.
