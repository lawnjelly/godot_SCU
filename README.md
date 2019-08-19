# godot_SCU
Unity build for Godot engine

## Description
Aimed at Godot engine contributors, this set of scripts allows you to easily modify your Godot folder to perform unity builds (aka single compilation unit, or jumbo builds). It should approximately double the speed of a full rebuild, and speed up incremental rebuilds between 4-6x.

https://en.wikipedia.org/wiki/Single_Compilation_Unit

Work in progress! Use with care, and particularly do not test for the first time on your own codebase.

## Installation
1) From the parent folder of your godot source code, create a second folder called godot_SCU and clone / download this repository inside.
2) Open a command prompt in the godot_SCU folder and run GO_PatchGodot.py
3) Add the extra switch -unity to your Scons command line. e.g. Scons p=x11 target=debug -unity
4) Build as normal

## Notes
To keep the unity build totally separate from the Godot repository (at least for now) the GO_PatchGodot.py script patches SConstruct and many of the SCsub files which tell Scons how to build Godot. It also applies a small patch to make_binders.py.

So take special care if you are making your own edits to the SCsub files (or don't use the unity patched version until you have completed these types of changes), and take care not to submit the patched files as part of a PR.

The unity build can adapt to a certain extent (adding / removing most source files) but major changes will require minor alterations to the scripts. For this reason the master tree is currently building against the Godot master. We can add forks for the other Godot forks as required.

See here for more info:
https://github.com/godotengine/godot/issues/13096

## Common 'gotchas' working with Unity Builds

1) Techniques that pollute the global namespace can cause problems in a unity build, such as localising a static function in a cpp. It is better to correct such techniques, but where this is not possible files can be excluded from the unity build.

2) Similarly, defines in one file will tend to carryover to later compiled files, something which would not occur in normal builds. For constants, prefer e.g. c++ style class constants, and for macros, it can be good practice to #undef the macro at the end of the source file.

3) The same happens with includes. Typically a programmer knows an include is needed due to an error. In a unity build, an earlier cpp may have already included a needed header, allowing the build to succeed, whereas an error would occur in the normal build. For this reason any work accelerated using unity builds should be subject to a final stage of compiling with a normal build, to resolve these differences.

### Compatibility
Tested on Linux and Android so far, please let me know issues on other platforms.
