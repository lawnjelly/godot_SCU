#!/usr/bin/python
import sys

from subprocess import call

# some globals which decide the operation of the script

# Patch or reverse the patch
g_bReverse = False
# Dont access the files
g_bDryRun = False
# Do the search and replace but dont write files if this is false
g_bDoOutput = True

g_bVerbose = False
g_bSuccess = True

# whether to include specific dependencies, or rely on scons
g_bUseDepends = False

# Some files have extra tabs in the add_source_files section
# This allows us to override this.
g_iNumTabs = 0

#g_szPathToSCU = "#misc/scu/SCU_"
g_szPathToSCU = "#../godot_SCU/SCU_"

###################################################
# Simple search and replace string with string
def replace_in_file(szFile, szSearch, szReplace):
    szFile = "../godot/" + szFile

    # reverse?
    if g_bReverse:
        szTemp = szReplace
        szReplace = szSearch
        szSearch = szTemp
        print ("REVERSING " + szFile)
    else:
        print ("PATCHING " + szFile)
    
    if g_bVerbose:
        print ("________Search\n" + szSearch)
        print ("________Replace\n" + szReplace)

    if g_bDryRun == False:
        # read in the file
        with open(szFile, 'r') as file:
            filedata = file.read()
        
        # replace the target string
        filedata_new = filedata.replace(szSearch, szReplace)

        # error condition
        if filedata == filedata_new:
            if g_bReverse:
                print ("WARNING - Search string not found\n")
            else:
                print ("ERROR - Search string not found:\n")
                print (szSearch)
            global g_bSuccess
            g_bSuccess = False
            return False
            #sys.exit('Patch unsuccessful')
        else:
            if g_bDoOutput == True:
                # write the file out again
                with open(szFile, 'w') as file:
                    file.write(filedata_new)
                    
    return True

###################################################
# Complex search and replace for the most common case of source files
def replace_sources(szFile, szEnv, szSources, szOutput, extra_sources = [], depends_list = []):
    global g_iNumTabs
    
    # some special situations demand extra tabs in the spacing of the whole section
    szTabs = ""
    for i in range (g_iNumTabs):
        szTabs += "    "
        
    # precalculate some strings
    szEnvSources = "env." + szSources
    szAddSourceFiles = szEnv + ".add_source_files(" + szEnvSources + ', "'
    szLongOutput = g_szPathToSCU + szOutput + ".cc"
    
    szSearch = szTabs + szEnv + ".add_source_files(" + szEnvSources + ', "*.cpp")\n'

    
    szReplace = szTabs + "if env['unity']:\n\
    " + szTabs + szAddSourceFiles + szLongOutput + '")\n'
    
    # extra sources
    for i in range (len(extra_sources)):
        szReplace += "    " + szTabs + szAddSourceFiles + extra_sources[i] + '.cpp")\n'

    for i in range (len(depends_list)):
        szReplace += "    " + szTabs + szEnv + '.Depends("' + szLongOutput + '", "' + depends_list[i] + '")\n'
        
    szReplace += szTabs + "else:\n"
    szReplace += "    " + szSearch

    # add a leading return to the search and replace, to prevent double patching
    szSearch = "\n" + szSearch
    szReplace = "\n" + szReplace

    result = replace_in_file(szFile, szSearch, szReplace)
    
    # reset number of tabs after each file
    g_iNumTabs = 0
    
    return result


###################################################
# DoPatch - may be run twice to reverse if failure
def DoPatch():
    global g_iNumTabs

    if g_bReverse:
        print "Reversing Patch"
    else:
        print "Patching Godot for Unity Build"

    if g_bDryRun:
        print "DRY RUN"
        
    print "\n"

    # SConstruct
    szSearch = 'opts.Add(\'system_certs_path\', "Use this path as SSL certificates default for editor (for package maintainers)", \'\')\n'
    szReplace = szSearch + 'opts.Add(BoolVariable(\'unity\', "Single compilation unit (unity) build", False))\n\
opts.Add(BoolVariable(\'unity_no_refresh\', "Single compilation unit (unity) build with no changes to file list", False))\n\n'
    replace_in_file("SConstruct", szSearch + "\n", szReplace)

    szSearch = "env_base.Append(CPPDEFINES=['DEBUG_MEMORY_ALLOC','DISABLE_FORCED_INLINE'])\n"
#    szReplace = szSearch + "\n\
# Unity build\n\
#if (env_base['unity']):\n\
#    env_base.Append(CPPDEFINES=['UNITY_BUILD'])\n\
#"

    szReplace = szSearch + "\n\
# Unity build\n\
from subprocess import call\n\
import os\n\
if (env_base['unity_no_refresh']):\n\
    # unity build also set to active if this flag is set\n\
    env_base['unity'] = True\n\
if (env_base['unity']):\n\
    env_base.Append(CPPDEFINES=['UNITY_BUILD'])\n\
    if (env_base['unity_no_refresh'] == False):\n\
        szCurrWorkingDir = os.getcwd()\n\
        os.chdir('../godot_SCU/')\n\
        call(\"../godot_SCU/GO_Create.py\")\n\
        os.chdir(szCurrWorkingDir)\n\
"
    replace_in_file("SConstruct", szSearch, szReplace)

    # core
    extra_sources = []
    extra_sources.append("variant_call")

    replace_sources("core/SCsub", "env", "core_sources", "core", extra_sources)

    replace_sources("core/io/SCsub", "env", "core_sources", "core_io")
    replace_sources("core/math/SCsub", "env_math", "core_sources", "core_math")
    replace_sources("core/os/SCsub", "env", "core_sources", "core_os")

    # drivers
    replace_sources("drivers/unix/SCsub", "env", "drivers_sources", "drivers_unix")

    # editor
    g_iNumTabs = 1
    extra_sources = []
    depends = []
    if g_bUseDepends:
        depends.append("#core/authors.gen.h")
        depends.append("#core/donors.gen.h")
        depends.append("#core/license.gen.h")
        depends.append("#core/io/certs_compressed.gen.h")
        depends.append("builtin_fonts.gen.h")
        depends.append("doc_data_compressed.gen.h")
        depends.append("translations.gen.h")
        depends.append("editor_icons.gen.h")
    replace_sources("editor/SCsub", "env", "editor_sources", "editor", extra_sources, depends)

    replace_sources("editor/import/SCsub", "env", "editor_sources", "editor_import")

    extra_sources = []
    extra_sources.append("script_text_editor")
    replace_sources("editor/plugins/SCsub", "env", "editor_sources", "editor_plugins", extra_sources)

    # main
    extra_sources = []
    depends = []
    if g_bUseDepends:
        depends.append("#main/app_icon.gen.h")
        depends.append("#main/splash.gen.h")
        depends.append("#main/splash_editor.gen.h")
    replace_sources("main/SCsub", "env", "main_sources", "main", extra_sources, depends)

    replace_sources("main/tests/SCsub", "env", "tests_sources", "main_tests")

    # modules

    # assimp
    szSearch = "\
env_thirdparty.add_source_files(env.modules_sources, Glob('#thirdparty/assimp/code/Common/*.cpp'))\n\
env_thirdparty.add_source_files(env.modules_sources, Glob('#thirdparty/assimp/code/PostProcessing/*.cpp'))\n\
env_thirdparty.add_source_files(env.modules_sources, Glob('#thirdparty/assimp/code/Material/*.cpp'))\n\
env_thirdparty.add_source_files(env.modules_sources, Glob('#thirdparty/assimp/code/FBX/*.cpp'))\n\
env_thirdparty.add_source_files(env.modules_sources, Glob('#thirdparty/assimp/code/MMD/*.cpp'))\n\
env_thirdparty.add_source_files(env.modules_sources, Glob('#thirdparty/assimp/code/glTF/*.cpp'))\n\
env_thirdparty.add_source_files(env.modules_sources, Glob('#thirdparty/assimp/code/glTF2/*.cpp'))\n\
"
    szReplace = "\
if env['unity']:\n\
    env_thirdparty.add_source_files(env.modules_sources, Glob('" + g_szPathToSCU + "thirdparty_assimp.cc'))\n\
    env_thirdparty.add_source_files(env.modules_sources, Glob('#thirdparty/assimp/code/FBX/*.cpp'))\n\
else:\n\
    env_thirdparty.add_source_files(env.modules_sources, Glob('#thirdparty/assimp/code/Common/*.cpp'))\n\
    env_thirdparty.add_source_files(env.modules_sources, Glob('#thirdparty/assimp/code/PostProcessing/*.cpp'))\n\
    env_thirdparty.add_source_files(env.modules_sources, Glob('#thirdparty/assimp/code/Material/*.cpp'))\n\
    env_thirdparty.add_source_files(env.modules_sources, Glob('#thirdparty/assimp/code/FBX/*.cpp'))\n\
    env_thirdparty.add_source_files(env.modules_sources, Glob('#thirdparty/assimp/code/MMD/*.cpp'))\n\
    env_thirdparty.add_source_files(env.modules_sources, Glob('#thirdparty/assimp/code/glTF/*.cpp'))\n\
    env_thirdparty.add_source_files(env.modules_sources, Glob('#thirdparty/assimp/code/glTF2/*.cpp'))\n\
"
    replace_in_file("modules/assimp/SCsub", szSearch, szReplace)

# bullet
    szSearch = '\
    ]\n\
\n\
    thirdparty_sources = [thirdparty_dir + file for file in bullet2_src]\
'
    szReplace = '\
    ]\n\
\n\
    if env[\'unity\']:\n\
        bullet2_src = [\n\
            # BulletCollision\n\
              "btBulletCollisionAll.cpp"\n\
\n\
\n\
            # BulletSoftBody\n\
            , "BulletSoftBody/btSoftBody.cpp"\n\
            , "BulletSoftBody/btSoftBodyConcaveCollisionAlgorithm.cpp"\n\
            , "BulletSoftBody/btSoftBodyHelpers.cpp"\n\
            , "BulletSoftBody/btSoftBodyRigidBodyCollisionConfiguration.cpp"\n\
            , "BulletSoftBody/btSoftRigidCollisionAlgorithm.cpp"\n\
            , "BulletSoftBody/btSoftRigidDynamicsWorld.cpp"\n\
            , "BulletSoftBody/btSoftMultiBodyDynamicsWorld.cpp"\n\
            , "BulletSoftBody/btSoftSoftCollisionAlgorithm.cpp"\n\
            , "BulletSoftBody/btDefaultSoftBodySolver.cpp"\n\
\n\
            , "btBulletDynamicsAll.cpp"\n\
            , "btLinearMathAll.cpp"\n\
        ]\n\
\n\
    thirdparty_sources = [thirdparty_dir + file for file in bullet2_src]\
'
    replace_in_file("modules/bullet/SCsub", szSearch, szReplace)

    # second search and replace in bullet SCsub.. watch for bugs
    replace_sources("modules/bullet/SCsub", "env_bullet", "modules_sources", "modules_bullet")

    # gdnative
    szSearch = '\
env_gdnative.add_source_files(env.modules_sources, "gdnative.cpp")\n\
env_gdnative.add_source_files(env.modules_sources, "register_types.cpp")\n\
env_gdnative.add_source_files(env.modules_sources, "android/*.cpp")\n\
env_gdnative.add_source_files(env.modules_sources, "gdnative/*.cpp")\n\
env_gdnative.add_source_files(env.modules_sources, "nativescript/*.cpp")\n\
env_gdnative.add_source_files(env.modules_sources, "gdnative_library_singleton_editor.cpp")\n\
env_gdnative.add_source_files(env.modules_sources, "gdnative_library_editor_plugin.cpp")\n\
'
    szDepends = ""
    if g_bUseDepends:
        szDepends = '    env.Depends("' + g_szPathToSCU + 'modules_gdnative.cc", "gdnative_api_struct.gen.cpp")\n\
    env.Depends("' + g_szPathToSCU + 'modules_gdnative.cc", "gdnative_api_struct.gen.h")\n'

    szReplace = '\
if env[\'unity\']:\n\
    env_gdnative.add_source_files(env.modules_sources, "' + g_szPathToSCU + 'modules_gdnative.cc")\n\
' + szDepends + '\
else:\n\
    env_gdnative.add_source_files(env.modules_sources, "gdnative.cpp")\n\
    env_gdnative.add_source_files(env.modules_sources, "register_types.cpp")\n\
    env_gdnative.add_source_files(env.modules_sources, "android/*.cpp")\n\
    env_gdnative.add_source_files(env.modules_sources, "gdnative/*.cpp")\n\
    env_gdnative.add_source_files(env.modules_sources, "nativescript/*.cpp")\n\
    env_gdnative.add_source_files(env.modules_sources, "gdnative_library_singleton_editor.cpp")\n\
    env_gdnative.add_source_files(env.modules_sources, "gdnative_library_editor_plugin.cpp")\n\
'
    replace_in_file("modules/gdnative/SCsub", szSearch, szReplace)


    # gdscript
    replace_sources("modules/gdscript/SCsub", "env_gdscript", "modules_sources", "modules_gdscript")

    # scene
    replace_sources("scene/2d/SCsub", "env", "scene_sources", "scene_2d")
    replace_sources("scene/animation/SCsub", "env", "scene_sources", "scene_animation")
    replace_sources("scene/main/SCsub", "env", "scene_sources", "scene_main")
    replace_sources("scene/resources/SCsub", "env", "scene_sources", "scene_resources")

    extra_sources = []
    extra_sources.append("line_edit")
    replace_sources("scene/gui/SCsub", "env", "scene_sources", "scene_gui", extra_sources)


    # scene 3d
    szSearch = 'else:\n\
    env.add_source_files(env.scene_sources, "*.cpp")'
    szReplace = 'else:\n\
    if env[\'unity\']:\n\
        env.add_source_files(env.scene_sources, "' + g_szPathToSCU + 'scene_3d.cc")\n\
    else:\n\
        env.add_source_files(env.scene_sources, "*.cpp")'

    replace_in_file("scene/3d/SCsub", szSearch, szReplace)

    # servers
    replace_sources("servers/SCsub", "env", "servers_sources", "servers")
    replace_sources("servers/audio/SCsub", "env", "servers_sources", "servers_audio")
    replace_sources("servers/audio/effects/SCsub", "env", "servers_sources", "servers_audio_effects")
    replace_sources("servers/physics/SCsub", "env", "servers_sources", "servers_physics")
    replace_sources("servers/physics_2d/SCsub", "env", "servers_sources", "servers_physics_2d")
    replace_sources("servers/visual/SCsub", "env", "servers_sources", "servers_visual")

    # thirdparty

    # make_binders
    szSearch = "\
#ifndef TYPED_METHOD_BIND\n\
$iftempl template<$ $ifret class R$ $ifretargs ,$ $arg, class P@$ $iftempl >$\
"
    szReplace="\
#ifdef UNITY_BUILD\n\
#pragma once\n\
#endif\n" + szSearch
    
    replace_in_file("core/make_binders.py", szSearch, szReplace)

    return g_bSuccess

###################################################
# Main routine

# whether to run the patch forward or reverse
if len(sys.argv) > 1:
    if sys.argv[1] == "-reverse":
        g_bReverse = True

result = DoPatch()

# if we failed, reverse the patch
if (result == False) and (g_bReverse == False):
    g_bReverse = True
    DoPatch()

if g_bSuccess:
    if g_bReverse:
        print "\n\nReversing COMPLETED SUCCESSFULLY.\n"
    else:
        print "\n\nPatching COMPLETED SUCCESSFULLY.\n"
        # create the SCU files for the unity build
        call("./GO_Create.py")
else:
    print "\n\nPatching UNSUCCESSFUL.\n"
