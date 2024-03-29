# godot_SCU
Unity build for Godot engine

## Description
Aimed at Godot engine contributors, this set of scripts allows you to easily modify your Godot folder to perform unity builds (aka single compilation unit, or jumbo builds). It should approximately double the speed of a full rebuild, and speed up incremental rebuilds between 4-6x.

https://en.wikipedia.org/wiki/Single_Compilation_Unit

# Important
Work in progress! Use with care. The script patches (modifies) many of the build files. As such it is essential you try it (at least until it is stable, and you are familiar with how it works) on a temporary version of the godot source and not on your current build. You have been warned! 

## Installation
1) From the parent folder of your godot source code, create a second folder called godot_SCU and clone / download this repository inside.
2) Open a command prompt in the godot_SCU folder and run GO_PatchGodot.py
3) Add the extra switch unity=True to your Scons command line. e.g. Scons p=x11 target=debug unity=True
4) Build as normal

## Usage
1) Add switch unity=True to Scons to use, remove it to use a normal build
2) To revert the patched files, run GO_UnpatchGodot.py. However note that the unpatching is not guaranteed to work, and reverting to the git versions of the patched files may be necessary in some circumstances.
3) The switch standard 'unity' will recreate the SCU files at the start of each build, which will mostly cope with adding or removing source cpp files from the Godot engine as you develop. For an even faster build, you can disable the SCU file recreation by using the flag 'unity_no_refresh' instead (until you need to add or remove source files).

## Notes
To keep the unity build totally separate from the Godot repository (at least for now) the GO_PatchGodot.py script patches SConstruct and many of the SCsub files which tell Scons how to build Godot. It also applies a small patch to make_binders.py.

So take special care if you are making your own edits to the SCsub files (or don't use the unity patched version until you have completed these types of changes), and take care not to submit the patched files as part of a PR.

The unity build can adapt to a certain extent (adding / removing most source files) but major changes will require minor alterations to the scripts. For this reason the master tree is currently building against the Godot master. We can add forks for the other Godot forks as required.

See here for more info:
https://github.com/godotengine/godot/issues/13096

For now, if you update to a newer version of godot_SCU, be sure to revert your build files (SCsub) using git before patching them to the new version.

## Common 'gotchas' working with Unity Builds

1) Techniques that pollute the global namespace can cause problems in a unity build, such as localising a static function in a cpp. It is better to correct such techniques, but where this is not possible files can be excluded from the unity build.

2) Similarly, defines in one file will tend to carryover to later compiled files, something which would not occur in normal builds. For constants, prefer e.g. c++ style class constants, and for macros, it can be good practice to #undef the macro at the end of the source file.

3) The same happens with includes. Typically a programmer knows an include is needed due to an error. In a unity build, an earlier cpp may have already included a needed header, allowing the build to succeed, whereas an error would occur in the normal build. For this reason any work accelerated using unity builds should be subject to a final stage of compiling with a normal build, to resolve these differences.

### Compatibility
Tested on Linux and Android so far, please let me know issues on other platforms.
