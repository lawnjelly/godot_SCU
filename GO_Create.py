#!/usr/bin/python
import os

from os import listdir
from os.path import isfile, join, isdir

g_bVerbose = False
g_bUseMacros = False

def process_folder(depth, szBaseDir, szSubDir, szExtension, bRecursive, files, IgnoreList):

    szFullPath = os.path.abspath("../godot/" + szBaseDir + szSubDir)
    if g_bVerbose:
        print ("FullPath : " + szFullPath)

    # all files and directorys in directory
    filenames_orig = sorted(listdir(szFullPath))
    
    # remove those on ignore list
    filenames = []
    for filename in filenames_orig:
        bOK = True
        for ignore in IgnoreList:
            #print ("is " + ignore + " in " + filename)
            if (filename.startswith(ignore)):
            #if ignore in filename:
                bOK = False
                break
        
        if bOK:
            filenames.append(filename)
    
    # only those files we are interested in
    filenames_ext = [ filename for filename in filenames if filename.endswith("." + szExtension) ]
    
    # add them to the file list
    for filename in filenames_ext:
        files.append(os.path.join(szSubDir, filename))
        sz = ""
        for t in range (depth+1):
            sz += "\t"
        if g_bVerbose:
            print (sz + filename)
        
    # if recursive, go through sub directorys
    if bRecursive:
        for filename in filenames:
            sub_path = os.path.join(szFullPath, filename)
            
            if isdir(sub_path):
                process_folder(depth + 1, szBaseDir, os.path.join(szSubDir, filename), szExtension, bRecursive, files, IgnoreList)
            

def process(szDir, szExtension, szOutput, IgnoreList = [], bRecursive = False):
    szOutput = "SCU_" + szOutput
    print ("\tProcess " + szDir + ", " + szExtension + " > " + szOutput)
    
    files = []
    
    process_folder(0, szDir, "", szExtension, bRecursive, files, IgnoreList)
    
    write_files(szDir, files, szOutput)
    #print (files)
    
def write_files(szDir, files, szOutput):
    f = open(szOutput, "w+")


    f.write("// Single Compilation Unit\n")
    
    if g_bUseMacros:
        f.write("#define SCU_IDENT(x) x\n")
        f.write("#define SCU_XSTR(x) #x\n")
        f.write("#define SCU_STR(x) SCU_XSTR(x)\n")

        f.write("#define SCU_PATH(x,y) SCU_STR(SCU_IDENT(x)SCU_IDENT(y))\n")
        f.write("#define SCU_DIR " + szDir + "\n\n")
        
        for fi in files:
            f.write("#include SCU_PATH(SCU_DIR," + fi + ")\n")
    else:
        for fi in files:
            f.write('#include "' + szDir + fi + '"\n')
        
        
    f.close()

# if you need to ignore more than 1 file / folder in a section, then manually
# create an ignore_list and pass it to process()
def process_ignore(szDir, szExtension, szOutput, szIgnore, bRecursive = False):
    ignore_list = []
    ignore_list.append(szIgnore)
    process(szDir, szExtension, szOutput, ignore_list, bRecursive)

print ("Creating Unity Build SCU files")

# fire off creation of the unity build files
process_ignore("main/", "cpp", "main.cc", "default_controller_mappings")
process("main/tests/", "cpp", "main_tests.cc")

process_ignore("core/", "cpp", "core.cc", "variant_call.cpp")
process("core/math/", "cpp", "core_math.cc")
process("core/os/", "cpp", "core_os.cc")
process("core/io/", "cpp", "core_io.cc")

process("drivers/unix/", "cpp", "drivers_unix.cc")
#process("drivers/gles2/", "cpp", "drivers_gles2.cc")


process("editor/", "cpp", "editor.cc")
#process("editor/doc/", "cpp", "editor_doc.cc")
#process("editor/fileserver/", "cpp", "editor_fileserver.cc")
process("editor/import/", "cpp", "editor_import.cc")
process_ignore("editor/plugins/", "cpp", "editor_plugins.cc", "script_text_editor.cpp")



process("servers/", "cpp", "servers.cc")
process("servers/audio/", "cpp", "servers_audio.cc")
process("servers/audio/effects/", "cpp", "servers_audio_effects.cc")
process("servers/physics/", "cpp", "servers_physics.cc")
process("servers/physics_2d/", "cpp", "servers_physics_2d.cc")
process("servers/visual/", "cpp", "servers_visual.cc")

process("scene/2d/", "cpp", "scene_2d.cc")
process("scene/3d/", "cpp", "scene_3d.cc")
process("scene/animation/", "cpp", "scene_animation.cc")
process_ignore("scene/gui/", "cpp", "scene_gui.cc", "line_edit.cpp")
process("scene/main/", "cpp", "scene_main.cc")
process("scene/resources/", "cpp", "scene_resources.cc")


# Modules
process("modules/bullet/", "cpp", "modules_bullet.cc")
process("modules/gdscript/", "cpp", "modules_gdscript.cc")

gdnative_ignore = []
gdnative_ignore.append("gdnative_api_struct.gen")
gdnative_ignore.append("arvr")
gdnative_ignore.append("doc_classes")
gdnative_ignore.append("icons")
gdnative_ignore.append("include")
gdnative_ignore.append("net")
gdnative_ignore.append("pluginscript")
gdnative_ignore.append("videodecoder")
process("modules/gdnative/", "cpp", "modules_gdnative.cc", gdnative_ignore, True)

# Third party
process_ignore("thirdparty/assimp/code/", "cpp", "thirdparty_assimp.cc", "FBX", True)
#process_ignore("thirdparty/squish/", "cpp", "thirdparty_squish.cc", "colourblock.cpp")

print ("\nUnity Build SCU files created OK\n")
