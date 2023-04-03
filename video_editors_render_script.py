########################### BEGIN GPL LICENSE BLOCK ###########################
#
#     THE VIDEO EDITOR'S RENDER SCRIPT FOR BLENDER (Universal Script)
#     Copyright (C) 2017 Mike Meyers 
#     Copyright (C) 2023 b1f6c1c4
#
#     This program is free software; you can redistribute it and/or
#     modify it under the terms of the GNU General Public License as 
#     published by the Free Software Foundation; either version 3 
#     of the License, or (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#     
#     You should have received a copy of the GNU General Public License
#     along with this program; if not, write to the Free Software Foundation,
#     Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
############################ END GPL LICENSE BLOCK ############################

#____________________________<[ SUPPORT \ CONTACT ]>___________________________
#
#                Originally Programmed by Mike "Mikeycal" Meyers
#                            Improved by b1f6c1c4
#                 Website: http://www.mikeycal.com
# Blender Video Editing Tutorials: https://www.youtube.com/user/MikeycalDOTcom
# Support Email [Paypal Donations Email] : mikeycaldotcom@yahoo.com
#______________________________________________________________________________

#_____________________________<[ SPECIAL THANKS ]>_____________________________
#
# [ Multiple background Blender instances ]
#  Thanks to Isti115's info on "How to make vse render faster"
#  https://goo.gl/mt7IUY
#
# [ Animated GIF ]
#  Thanks to ubitux's info on how to generate animated GIFS with ffmpeg
#  https://goo.gl/bs5Nk1
#
# [ Viewers like You ]
#  Thanks to viewers like you that have watched my series, given me good
#  advice, and brightened my day with your kind words and donations
#______________________________________________________________________________

#______________________________<[ INSTRUCTIONS ]>______________________________
#
# (1) SET THE PATH TO THE BLENDER AND FFMPEG PROGRAMS:
#
#  Set full paths for Blender and FFMPEG in the section starting on line 94
#
# RECOMMENDED PATHS FOR PROGRAMS (Set By Default):
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#       Windows: "C:\Program Files\Blender Foundation\Blender\blender.exe"
#                 C:\ffmpeg\bin\ffmpeg.exe
#
#           Mac: /Applications/Blender/blender.app/Contents/MacOS/blender
#                /Applications/ffmpeg
#
#     GNU/Linux: /usr/bin/blender
#                /usr/bin/ffmpeg
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# (2) PUT SCRIPT IN A FOLDER AND "SAVE AS..." 1.blend FILE TO SAME FOLDER
#
# (3) RUN THIS SCRIPT FROM THE FOLDER USING CMD.EXE OR TERMINAL:
#              (use the quotation marks for paths with spaces)
#        "Path \ To \ blender" -b 1.blend -P my_render_script.py
#
#  Link to Detailed Instructions:
#
#  GitHub Project Link:
#  https://github.com/b1f6c1c4/the-video-editors-render-script-for-blender
#
#  Link to Video Tutorial:
#
#  http: https://www.youtube.com/watch?v=rgwP5L1bICk                               ___________________________________________________________________________
#______________________________________________________________________________#  |__________________________________NOTES MARGIN_____________________________|

#----[ IMPORT PYTHON MODULES ]                                                 #  | This script should work on any Operating System that supports
import platform                                                                #  | Bash Shell, Blender and FFmpeg. You can add your own "elif:"
import bpy                                                                     #  | for your platform or simply edit the "else:" section.
import os
import time
import shutil
import tempfile
import multiprocessing
import math
import subprocess
import re

#----[ DETECT OPERATING SYSTEM ]
my_platform = platform.system()

#______________________________________________________________________________
#
#>> > > ENTER FULL PATH TO BLENDER AND FFMPEG FOR YOUR OPERATING SYSTEM  < < <<#  |  OS Specific Shortcuts like ~ (tilde) don't work - enter full path.
#______________________________________________________________________________

if True:

    if my_platform == "Windows": #SET MICROSOFT WINDOWS PATHS BELOW
        blender_path = r"C:\Program Files\Blender Foundation\Blender\blender.exe"  #  | (leave "r" prefix) python doesn't like \ slashes
        ffmpeg_path = r"C:\ffmpeg\bin\ffmpeg.exe"                               #  | (leave "r" prefix) python doesn't like \ slashes

    elif my_platform == "Darwin": # APPLE OSX PATHS BELOW
        blender_path = "/Applications/Blender/blender.app/Contents/MacOS/blender"
        ffmpeg_path = "/Applications/ffmpeg"

    else: # OTHER OPERATING SYSTEMS PATHS BELOW
        blender_path = "blender"
        ffmpeg_path = "ffmpeg"

#______________________________________________________________________________
#
#                            USER PREFERRED SETTINGS
#______________________________________________________________________________

#----[ OUTPUT FILES ]
full_root_filepath = os.path.dirname(bpy.data.filepath)
stem_name = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
output_audio_file = os.path.join(full_root_filepath, f"{stem_name}-audio")
output_video_file = os.path.join(full_root_filepath, f"{stem_name}-video")
output_gif_file = os.path.join(full_root_filepath, f"{stem_name}-output.gif")
output_seq_dir = os.path.join(full_root_filepath, f"{stem_name}-seq")

#--------------------------------------------------------------------#
#----------------------[ SCRIPT SETTINGS BANNER ]--------------------#---------
#--------------------------------------------------------------------#

display_script_settings_banner = True #(Default: True) [True or False]
banner_wait_time = 5 # seconds (Default: 5)                                    #  | Number of seconds the script will display render settings before rendering starts.
show_cpu_core_lowram_notice = False # (Default: False) [True or False]         #  | Display that we need 1.6GB to 3GB per CPU core available
show_render_status = True # (Default: True) [True or False]                    #  | Display frame count (It is off by default because it may be slower.)

#--------------------------------------------------------------------#
#---------------------------[ CPU SETTINGS ]-------------------------#---------
#--------------------------------------------------------------------#

#----[ NUMBER OF LOGICAL CPU CORES RESERVED TO RUN OPERATING SYSTEM ]          #  | [0 = use all cores] (Each used core creates 1 additional instance of blender. 1.6GB to 3GB RAM/Core is required)
reserved_cpu_logical_cores = 0 # (Default: 0) [1 = safe mode]                  #  | "reserved_cpu_logical_cores" setting subtracts cores from the total available.
                                                                               #  | e.g. reserved_cpu_logical_cores = 3 (on a 8 core CPU) will limit the script to use only 5 of 8 cores.
#----[ FORCE 1 BLENDER INSTANCE ] (!DISABLES MULTICORE FUNCTIONALITY!)         #  | When True, this disables multicore rendering, but it lets you use external
force_one_instance_render = False # (Default: False) [True or False]           #  | FFmpeg with any of your blender projects. Including keyframed 3D Scenes
                                                                               #  | Basically, this let you render any .blend file without the interface.
#----[ SHOULD WE BYPASS WARNINGS WHEN ONLY 1 CPU CORE IS ENABLED? ]
bypass_low_cpu_warnings = False # (Default: False) [True or False]             #  | True will hide warning prompts and auto-select script recommended settings.

#--------------------------------------------------------------------#
#--------------------------[ FILE SETTINGS ]-------------------------#---------
#--------------------------------------------------------------------#

#----[ SHOULD WE AUTO-DELETE GENERATED TEMP FOLDERS AND TEMP FILES? ]
auto_delete_temp_files = True #(Default: True) [True or False]

#----[ SHOULD WE ALLOW AUTOMATIC OVERWRITING OF MEDIA FILES? ]                 #  | When this is False, it will stop the script and ask to overwrite when necessary.
auto_overwrite_files = True #(Default: True) [True or False]

#--------------------------------------------------------------------#
#----------------------[ AUDIO/VIDEO SETTINGS ]----------------------#---------
#--------------------------------------------------------------------#

separate_audio_video = False #(Default: False) [True or False]
force_lossless_audio = True #(Default: True) [True or False]

#----[ FFMPEG COMMAND LINE ARGUMENTS USED TO MUX FINAL VIDEO ]                 #  | e.g.: ffmpeg -i video.mp4 -i FullAudio.m4a [arg1] FinishedVideo.mp4 [arg2]
post_full_audio = "-c:v copy -c:a copy -map 0:v:0 -map 1:a:0"                  #  | Essential arguments used to Mux Final Audio/Video (! DON'T CHANGE !)
post_full_audio += " -movflags faststart" # [arg1]                             #  | Makes the video streamable for services like YouTube
post_full_audio_arg2 = "-async 1" # [arg2]                                     #  | add trailing args here

#----[ BLENDER AUDIO PCM MIXDOWN SETTINGS ]                                    #  | Note: Audio is exported separate from the video, using following settings.
export_audio_accuracy = 1024 # (Default: 1024)                                 #  | Sample Accuracy - lower it is, the more accurate. (?)
export_audio_format = "" # (Default: "") ["U8","S16","S24","S32","F32","F64"]  #  | Sample Format: 's16' works on all platforms but try 'S24' or 'S32'
force_audio_mixrate = "" # (Default: "") ["44100","48000","96000","192000"]    #  | Mixrate (Audio Sample Rate) - 48kHz seems to be default for most recording devices.
                                                                               #  | Leave the force_audio_mixrate = "" to use the Blender's default setting.
#----[ SHOULD WE USE FFMPEG'S RANGE OF BITRATES? ]
use_ffmpeg_audio_bitrates = False # (Default: False) [True or False]           #  | True allows audio bitrates from 8kb/s to 640kb/s (Depending on codec limit)

#----[ WHAT FFMPEG AUDIO BITRATE SHOULD WE TRY TO USE? ]                       #  | Blender locks bitrate from 32kb/s-384kb/s. We are using external ffmpeg, so
custom_audio_bitrate = 512 # kb/s  [8 - 640]                                   #  | we can override blender's limit. FFmpeg uses closest compatible bitrate.

#----[ DO YOU WANT TO USE LIBFDK_AAC INSTEAD OF STANDARD ACC ]                 #  | If you built FFMPEG with libfdk_acc, you can use it by setting to True. This feature only works
use_libfdk_acc = False # (Default: False) [True or False]                      #  | if you have compiled in support for libfdk. It will crash if you set to True and it isn't present.

#--------------------------------------------------------------------#
#---------------------------[ GIF FEATURES ]-------------------------#---------
#--------------------------------------------------------------------#

#----[ SHOULD WE CONVERT VIDEO TO AN ANIMATED GIF? ]                           #  | You must render a Movie format (e.g. mp4,avi,...) to create animated GIFs
render_gif = False #(Default: False) [True or False]
gif_framerate = "15" #(Default: "15") [use quotation marks(String)]            #  | If you use "" (empty), it will default to blender's FPS render setting
stats_mode = "full" #(Default: full) [full, diff]
custom_gif_scale_x_value = "" # (Default: "") [eg "640", "800", "1024"]        #  | If you set this to "" (empty), it will default to blender's render settings resolution
dither_options = "none" # (Default: "none")                                    #  | Dither Options: "none", "bayer:bayer_scale=1", "bayer:bayer_scale=2",
the_scaler = "lanczos" # Default: "lanczos"                                    #  | "bayer:bayer_scale=3", "floyd_steinberg", "sierra2", "sierra2_4a", "heckbert" (See https://goo.gl/bs5Nk1)
                                                                               #  | Scaler options "lanczos", "bicubic","bilinear" ( more: https://ffmpeg.org/ffmpeg-scaler.html)
#--------------------------------------------------------------------#
#------------------------[ RENDER OVERRIDES ]------------------------#---------
#--------------------------------------------------------------------#

#----[ SHOULD WE BYPASS ALERTS IF ENCODE WILL BE LONGER THAN USUAL? ]
bypass_huffyuv_and_raw_avi_warnings = True #(Default: True ) [True or False] #  | True will skip all warning prompts and render anyway.

#----[ PERMIT A 3D SCENE STRIP IN VSE ] (Experimental/ Glitchy)                #  | Scene strips are unreliable when rendering with Multiple blender instances
permit_scene_strips = False #(Default: False) [True or False]                  #  | that have keyframed viewport objects. Instead, Render out keyframed
                                                                               #  | objects as an image sequence, import them into VSE, then use this script.
 #----[ COLOR MANAGEMENT SPEEDUP / OVERRIDE )                                  #
color_management_defauts_render_speed_up = False #(Default: False) [True or False]  | By default, Blender 2.8 uses Color Management settings that triple render time.
                                                                               #  | This Sets 'View Transform'='Standard' and 'Look'='None' (Which are Blender 2.79 defaults)
  #------------------------------------------------------------------#
#>#-----------------[ .BLEND OVERRIDE FILE CONTENTS ]----------------#---------#  | This is a great place to put common settings that you somtimes forget
  #------------------------------------------------------------------#         #  | to set in your blend files. These settings are altered right before
#>>>> START OF .BLEND OVERRIDE FILE SETTINGS <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<#  | the render begins.
blendfile_override_setting = "import bpy\n"                                    #
blendfile_override_setting += "for scene in bpy.data.scenes: \n"               #
blendfile_override_setting += "    scene.render.ffmpeg.audio_codec = 'NONE'\n" #  | Please leave the setting: audio_codec = 'NONE'.
# UNHASH OR ADD OTHER OVERRIDES HERE - USING FOLLOWING FORMAT                  #  | Audio is exported and compressed seperately. Turning audio on
#blendfile_override_setting += "    scene.render.resolution_percentage = 100\n"#  | will just slow down render time. By default, this script will
#blendfile_override_setting += "    scene.render.ffmpeg.minrate = 0\n"         #  | use the codec and bitrate you set in the blender render settings.
#blendfile_override_setting += "    scene.render.ffmpeg.maxrate = 9000\n"      #  | Include "    " (4 spaces) before scene.render.* - python requires it.
#blendfile_override_setting += "    scene.render.ffmpeg.muxrate = 10080000\n"  #
#blendfile_override_setting += "    scene.render.ffmpeg.packetsize = 2048\n"   #  | It is also worth noting that audio can't be manipulated through the override
#blendfile_override_setting += "    scene.render.ffmpeg.buffersize = 1792\n"   #  | file because Audio is processed at a different time than the video.
#>>>> END OF .BLEND OVERRIDE FILE SETTINGS <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<#  | Instead, audio should be configured in the Audio/Video settings (line 158)

#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX#
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
#                                           Don't Edit Anything Below this line unless you know what you are doing                                            #
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX#

#______________________________________________________________________________
#
#                        OPERATING SYSTEM SPECIFIC SETTINGS
#______________________________________________________________________________

if True:

    if my_platform == "Windows": # Windows 10
        start_blender = start_ffmpeg = r'start " " /max /B '                       #  | Leave this setting. Win10 v1809+ build broke start - now needs /max arg to work.
        wait_here = ampersand = use_bash = ""                                      #  | Windows doesn't use - leave empty
        render_filename = "render.bat"                                             #  | Executable OS Commands Stored here
        make_script_executable = ""

    elif my_platform == "Darwin": # APPLE OSX
        start_blender = start_ffmpeg = ""                                          #  | Only Windows uses this - Set to empty
        wait_here = "wait\n"                                                        #  | this wait prevents execution until blender is done.
        ampersand = "&"                                                            #  | This places blender instance in background.
        render_filename = "render.sh"                                              #  | Executable OS Commands Stored here
        use_bash = "bash "                                                         #  | We run a bash script (render.sh)
        make_script_executable = "chmod a+x"                                       #  | We need to make the file executable

    elif my_platform == "Linux": # GNU/LINUX
        start_blender = start_ffmpeg = ""                                          #  | Only Windows uses this - Set to empty
        wait_here = "wait\n"                                                        #  | This is used to wait until background commands finish
        ampersand = "&"                                                            #  | This is used to send commmand to background
        render_filename = "render.sh"                                              #  | Executable OS Commands Stored here
        use_bash = "bash "                                                         #  | We run a bash script (render.sh)
        make_script_executable = "chmod a+x"                                       #  | We need to make the file executable

    else: # OTHER OPERATING SYSTEMS WITH ACCESS TO BASH SHELL
        start_blender = start_ffmpeg = ""                                          #  | Only Windows uses this - Set to empty
        wait_here = "wait\n"                                                        #  | This is used to wait until background commands finish
        ampersand = "&"                                                            #  | This is used to send commmand to background
        render_filename = "render.sh"                                              #  | Executable OS Commands Stored here
        use_bash = "bash "                                                         #  | We run a bash script (render.sh)
        make_script_executable = "chmod a+x"                                       #  | We need to make the file executable

#______________________________________________________________________________
#
#                              BASIC CONFIGURATION
#______________________________________________________________________________

if True:

    #----[ SET SCRIPT DEFAULTS VARIABLES ]
    blender_command = "" # (Default= "")

    #----[ GIVE TEMP FILE-FOLDERS NAMES ]
    working_dir_temp = os.path.abspath(tempfile.mkdtemp(prefix='render-script-'))

    path_to_av_source = os.path.join(working_dir_temp, "AV_Source")
    temp_png_palette = os.path.join(path_to_av_source, "palette.png")
    temp_to_wav = os.path.join(path_to_av_source, "Full_Audio")
    temp_video_without_audio = os.path.join(path_to_av_source, "Joined_Video")

    path_to_other_files = os.path.join(working_dir_temp, "Other_Files")            #  | Look at "render." file in this folder to see the "secret sauce."
    settings_file = os.path.join(path_to_other_files, "OverrideSettings.py")
    concat_file = os.path.join(path_to_other_files, "Concat_Video_List.txt")
    render_file = os.path.abspath(os.path.join(path_to_other_files, render_filename))

    #----[ PCM MIXDOWN SETTINGS (LOSSLESS) ]
    export_audio_container = "WAV" # (Default: "WAV")
    export_audio_codec = "PCM" # (Default: "PCM")
    export_audio_bitrate = 384 # kb/s (Default: 384)                               #  | This setting is ignored by PCM (It's set because it's there.)
    export_audio_split_channels = False # (Default: False) [True or False]         #  | Turning this to True may cause loss of some audio

    #----[ DOCUMENTED BITRATE RANGE FOR SUPPORTED AUDIO CODECS ]                   #  | Wikipedia was my source for these bitrate limits
    max_audio_bitrate_ac3 = 640 # kb/s (AC3)                                       #  | If you know of better settings, email me.
    max_audio_bitrate_aac = 529 # kb/s (AAC)
    max_audio_bitrate_mp3 = 320 # kb/s (MP3)
    max_audio_bitrate_mp2 = 384 # kb/s (MP2)
    max_audio_bitrate_opus = 500 # kb/s (OPUS)
    min_audio_bitrate_ac3 = min_audio_bitrate_mp2 = 32 # kb/s (AC3) (MP2)
    min_audio_bitrate_aac = min_audio_bitrate_mp3 = 8 # kb/s (AAC) (MP3)
    min_audio_bitrate_opus = 45 # kb/s (OPUS)

    #----[ FALLBACK AUDIO BITRATES ]
    max_audio_bitrate = 320 # kb/s
    min_audio_bitrate = 32 # kb/s

    #----[ DETECT IF BLENDER AND FFMPEG PATHS ARE CORRECTLY CONFIGURED ]
    def verify_cmd(path, prog):
        if shutil.which(path) is None:
            print(80 * "#")
            print(f"\n {prog} program was not found. Please set the correct path to {prog} in the\n render script.")
            print("\n The render script is set to look for Blender at the following location:\n")
            print(f" {path}\n")
            print(80 * "#")
            exit()
    verify_cmd(blender_path, "Blender")
    verify_cmd(ffmpeg_path, "FFmpeg")

#______________________________________________________________________________
#
#               GET RENDER PROPERTY SETTINGS FROM THE .BLEND FILE
#______________________________________________________________________________

if True:

    # Blender version reported by .blend file
    blender_ver = str(bpy.data.version[0]) + "" + str(bpy.data.version[1]) + "0"  # edited out bpy.data.version[2] due to changes in blender 2.83
    blender_ver = int(blender_ver)                                                #  | 2790 int value (2.79.0)
    # Blender version being used for rendering
    blender_ver_running = str(bpy.app.version[0]) + "" + str(bpy.app.version[1]) + "0"  # edited out bpy.app.version[2] due to changes in blender 2.83
    blender_ver_running = int(blender_ver_running)

    if blender_ver_running != blender_ver:
        print(80 * "#")
        print(f"\n Your .blend file \'encoding section\' is setup for version{str(bpy.data.version)}, but you are\n "
              f"rendering with {str(bpy.app.version)}. Please open the .blend file in blender{str(bpy.app.version)},"
              f"\n configure the encoding settings, and save the .blend file. This will make\n sure that blender has "
              f"set all of the correct variables for your project.\n")
        print(80 * "#")
        exit()

    # Set Defaults for Variables that are used below
    number_of_scenes = 0                                                           #  | Set Scene number to 0 so we can count number of VSE scenes.
    scene_strip_in_vse_is_3d = False                                               #  | Assume there are no 3d Scene Strips in the sequencer
    sound_strips = 0                                                               #  | Assume we have no sound strips
    scene_name_present = False                                                     #  | if "Scene" isn't found you will get an Alert.

    for scene in bpy.data.scenes:

        if scene.name == "Scene":                                                  #  | We cycle through all the scenes, but only take settings from scene named "Scene"

            scene_name_present = True

            #Image/Video that work on all versions of blender 2.7+         (eg)
            blender_x_resolution = scene.render.resolution_x #             (800)
            blender_y_resolution = scene.render.resolution_y #             (600)
            blender_res_percent = scene.render.resolution_percentage #     (50)
            blender_file_format = scene.render.image_settings.file_format #(FFMPEG)
            blender_vid_format = scene.render.ffmpeg.format #              (MPEG4)
            blender_video_codec = scene.render.ffmpeg.codec #              (H264)
            blender_video_bitrate = scene.render.ffmpeg.video_bitrate #    (8000)
            blender_gop = scene.render.ffmpeg.gopsize #                    (18)
            blender_video_bitrate = scene.render.ffmpeg.video_bitrate #    (8000)
            blender_gop = scene.render.ffmpeg.gopsize #                    (18)
            blender_color_mode = scene.render.image_settings.color_mode#   (RGB)

            # If 2.78c or lower get these settings
            blender_constant_rate_factor = scene.render.ffmpeg.constant_rate_factor #    (HIGH)
            blender_ffmpeg_preset = scene.render.ffmpeg.ffmpeg_preset #                  (FAST)
            #Check Lossless output
            if blender_constant_rate_factor == "LOSSLESS":
                blender_use_lossless_output = True
            else:
                blender_use_lossless_output = False

            if blender_constant_rate_factor == "NONE":
                use_constant_bitrate = True
            else:
                use_constant_bitrate = False

            #Scale resolution
            blender_x_times_res_percent =\
            int((blender_res_percent * 0.01)*blender_x_resolution) #       (400)   #  | These settings allow us to use the "scale resolution"
            blender_y_times_res_percent=\
            int((blender_res_percent * 0.01)*blender_y_resolution) #       (300)   #  | option below the (X,Y) resolution settings.

            #GIF Scale Resolution
            if render_gif:
                if custom_gif_scale_x_value == "":
                    gif_scale = blender_x_times_res_percent                        #  | By default we use blenders resolution setting
                else:
                    gif_scale = int(custom_gif_scale_x_value)

            #Audio                                                        (eg)
            blender_audio_codec = scene.render.ffmpeg.audio_codec #       (AAC)
            blender_audio_bitrate = scene.render.ffmpeg.audio_bitrate #   (192)
            blender_audio_channels = scene.render.ffmpeg.audio_channels # (False)
            blender_audio_volume = scene.render.ffmpeg.audio_volume #     (1.0)

            if force_audio_mixrate in ("44100","48000","96000","192000"):
                blender_audio_mixrate = int(force_audio_mixrate)
                #Set the audio sample rate to script's user setting
                scene.render.ffmpeg.audio_mixrate = int(force_audio_mixrate)       #  | We set the mixrate directly because it's not included in the export function.
            elif force_audio_mixrate != "":
                print(80 * "#" + "\n\n force_audio_mixrate is set wrong in this script.\n\n" + 80 * "#")
                exit()
            else:
                blender_audio_mixrate = scene.render.ffmpeg.audio_mixrate

           #Framerate                                                      (eg)
            blender_fps = scene.render.fps #                               (24)
            blender_fps_base = scene.render.fps_base #                     (1.001)
            the_framerate_float = round(blender_fps / blender_fps_base,2) #(23.98)

            #GIF Framerate
            if render_gif:
                if gif_framerate == "":
                    gif_framerate = the_framerate_float

            #Start and End Frames                                          (eg)
            start_frame_is = scene.frame_start #                           (1)
            end_frame_is = scene.frame_end #                               (1000)
            total_frames = end_frame_is - start_frame_is #       (999)
            total_frames += 1 #                                  (1000)  #  | We need to add 1 because the first frame is included

            #Render Engine                                                 (eg)
            blender_render_engine = scene.render.engine #                  (CYCLES)

            #Autosplit                                                     (eg)
            blender_use_autosplit = scene.render.ffmpeg.use_autosplit #    (True)

        number_of_scenes += 1                                                      #  | How many scenes are we dealing with...

        try:
            for seq in scene.sequence_editor.sequences_all:                        #  | Generally, we don't use Scene Strips, but if the Scene Strips
                if seq.bl_rna.name == "Scene Sequence" and scene.name == "Scene":  #  | only use a Sequencer, it will work. Only 3D breaks.
                    if not seq.use_sequence:
                        scene_strip_in_vse_is_3d = True
        except AttributeError:                                                     #  | When VSE is empty, there is no Attribute, so we catch the error.
            print("VSE is Empty")

        try:
            for seq in scene.sequence_editor.sequences_all:
                if seq.bl_rna.name == "Sound Sequence":
                    sound_strips += 1                                              #  | Count the number of total Sound Strips in all Scenes.
                    print("Sound Found")
        except AttributeError:                                                     #  | When VSE is empty, there is no Attribute , so we catch the error.
            print("VSE EMPTY")

    #----[ CHECK FOR SCENE NAMED "Scene" ]
    if not scene_name_present:                                                     #  | We must have a scene named "Scene" to get settings from.
        print(80 * "#")
        print('\n\n ! NO SCENE NAMED "Scene" ALERT !\n\n Please name your primary scene, "Scene" . This is required '
              'so that blender\n knows which scene it should take settings from. \n\n')
        print(80 * "#")
        exit()

    if sound_strips == 0:                                                          #  | Turn off Audio if there are 0 Sound Strips, otherwise, use 1st detected
        blender_audio_codec = "NONE"                                               #  | Audio Codec

    if blender_audio_codec != "NONE":                                              #  | If we're rendering audio, we can collect the Sample Format setting from User Pref.

        try_sample_format = bpy.context.preferences.system.audio_sample_format

        if try_sample_format in ("U8","S16","S24","S32"):
            if export_audio_format == "":
                export_audio_format = try_sample_format
        elif try_sample_format == "FLOAT":
            if export_audio_format == "":
                export_audio_format = "F32"
        elif try_sample_format == "DOUBLE":
            if export_audio_format == "":
                export_audio_format = "F64"

    #----[ Switch Color Management settings to Match 2.79 defaults]

    if color_management_defauts_render_speed_up:

        if bpy.context.scene.view_settings.view_transform != 'Standard':
            blendfile_override_setting += "    bpy.context.scene.view_settings.view_transform = 'Standard'\n"

        if bpy.context.scene.view_settings.look != 'None':
            blendfile_override_setting += "    bpy.context.scene.view_settings.look = 'None'\n"

#______________________________________________________________________________
#
#                      CHECK FOR MINIMUM CPU REQUIREMENTS
#______________________________________________________________________________

if True:

    #----[ DETECT NUMBER OF LOGICAL CPU CORES AVAILABLE ]                          #  | cpu_count = max number of possible render instances.
    logical_cores_available = multiprocessing.cpu_count()                          #  | Having more instances than count number has NO render time advantage.

    #----[ SET NUMBER OF LOGICAL CPU CORES USED WITH BLENDER INSTANCES ]
    cores_enabled = logical_cores_available - reserved_cpu_logical_cores           #  | cores_enabled = actual number of video segments created

    if not force_one_instance_render:                                              #  | When forceOneInstanceRender = True, we render with only 1 blender instance.

        #----[ DOES CPU HAVE MULTIPLE LOGICAL CORES ]                              #  | blender instance, with 1 core, are able to render anything you
        if logical_cores_available == 1:                                           #  | want, without UI - Even 3D scenes. The benefit is that you will
            print(80 * "#")
            print("\n\n Your CPU logical core number is less than 2. This script is\n designed to be used with CPUs "
                  "that have multiple logical cores.\n To run script with single core, set force_one_instance_render "
                  "= True \n Script has exited.\n\n")
            print(80 * "#")
            exit()

        #----[ MINIMUM CPU LOGICAL CORE REQUIREMENT TO RUN SCRIPT]                 #  | All CPU's with more than 1 core get this setting by default
        min_cores_met = 2

        #----[ DOES CPU HAVE MORE THAN 1 LOGICAL CORE IT CAN USE? ]
        if cores_enabled < 2 and logical_cores_available > 1 and not bypass_low_cpu_warnings:
            try:
                min_cores_met = int(input(80 * "#" \
                                          + "\n\n Your computer is using less than 2 CPU cores.\n\n There will only "
                                            "be a, render time, performance increase if you use ALL\n of your CPU "
                                            "Cores. This should work, but it may cause interaction with\n your "
                                            "computer to slow down.\n To run script with single core, "
                                            "set force_one_instance_render = True \n\n" \
                                          + 80 * "#" + "\n\n [Enter 2] to use 2 CPU cores, or simply press ENTER(RETURN) to exit: "))
            except ValueError:
                print(80 * "#")
                print("\n\n Script exited because you need at least 2 cores for this script\n To run script with "
                      "single core, set force_one_instance_render = True \n\n")
                print(80 * "#")
                exit()

        #----[ ONLY CONTINUE IF MINIMUM NUMBER OF LOGICAL CORES IS MET ]
        if min_cores_met != 2:
            print(80 * "#")
            print("\n\n Script exited because you need at least 2 cores for this script\n\n")
            print(80 * "#")
            exit()

        if cores_enabled < 2 and logical_cores_available > 1:
            cores_enabled = 2                                                      #  | We set CPU logical cores to 2.

    else:                                                                          #  | This "else:" bypasses CPU LIMIT, allowing us to use
        cores_enabled = 1                                                          #  | external FFmpeg with 1 core with any .blend project.
        permit_scene_strips = True                                                 #  | 3D Scene Strips work as expected with 1 instance

#______________________________________________________________________________
#
#                           CHECK FOR IMAGE SEQUENCE
#______________________________________________________________________________

if True:
    #----{ DETECT IF USER SELECTED AN IMAGE FORMAT ]
    if blender_file_format in ("BMP","IRIS","PNG","JPEG","JPEG2000","TARGA",\
        "TARGA_RAW","CINEON","DPX","OPEN_EXR_MULTILAYER","OPEN_EXR","HDR","TIFF"): #  | This renders an Image Sequence and Audio file
        blender_image_sequence = True                                              #  | to a folder instead of muxing an audio/video file
        #----[ IF IMAGES SEQUENCE IS SET, DON'T ALLOW GIF RENDERING ]              #  | With this script, GIF's can only be produced from movie formats.
        if render_gif:
            print(80 *"#")
            print(f"\n\n You have configured this script to render an animated gif and selected an\n Image Sequence "
                  f"format of {blender_file_format}. These options are mutually exclusive.\n Either Change to a movie "
                  f"format to render an animated gif, or set\n render_gif = False. \n\n")
            print(80 * "#")
            exit()
    else:
        blender_image_sequence = False

#______________________________________________________________________________
#
#                                   WARNINGS
#______________________________________________________________________________

if True:

    #----[ MAKE SURE WE HAVE AT LEAST 1 FRAMES PER RENDER INSTANCE ]
    if total_frames < cores_enabled:
        print(80 * "#")
        print(f"\n\n ! NOT ENOUGH FRAMES ALERT !\n\n You must render at least [ {str(cores_enabled)} ] frames\n\n")
        print(80 * "#")
        exit()

    #----[ CHECK FOR PATH THAT USE ' IN THEM ]
    if "'" in full_root_filepath or "'" in path_to_av_source or "'" in output_video_file:
        print(80 * "#")
        print("\n\n ! APOSTROPHE ALERT !\n\n Your .blend filepath has an APOSTROPHE in it. Please remove the "
              "APOSTROPHE\n from your path name and never use an APOSTROPHE in a file or folder\n name ever again. "
              "While we are at it, you really shouldn't ever use\n SPACES in a file or folder name either, "
              "but I will allow it. ;)\n\n Underscore_is_your_best_friend. \n\n")
        print(80 * "#")
        exit()

    #----[ Check if scaled resolution is divisible by 2 ]
    if blender_x_times_res_percent % 2 != 0 or blender_y_times_res_percent % 2 != 0:
        print(80 * "#")
        print("\n\n Your resolution isn\'t Divisible by 2. Blender can only render \n" \
              + "X & Y valuse\n that are divisible by 2 with no remainder. " \
              + f"Your resolution is {blender_x_times_res_percent} x {blender_y_times_res_percent} \n\n")
        print(80 * "#")
        exit()

    #----[ ARE SCENE STRIPS ALLOWED IN THE VSE ]
    if not permit_scene_strips:                                                    #  | Multi Instance rendering requires dividing the project frame range. When
                                                                                   #  | keyframes have been inserted into viewport objects, and you render out a
        if scene_strip_in_vse_is_3d:                                               #  | divided frame range, keyframes break. Therefore, we disable scene strips.
            print(80 * "#")
            print("\n\n Your VSE contains 'Scene Strips.' If your Scene Strip simply contains another\n Sequencer "
                  "SCENE, you will need to Checkmark 'USE Sequence' in the Scene Strip \n properties. Otherwise, "
                  "You have chosen not to permit 3D Scenes with\n the following script setting:\n\n "
                  "permit_scene_strips = False \n\n You can change that setting to True, or remove the Scene Strip "
                  "from the VSE.\n\n Note:\n Keyframed objects in the viewport can have glitchy results - this safety "
                  "is\n in place to prevent wasting your render time. The one scenario where you\n would want to "
                  "allow 3D Scene Strips to Render is when your Viewport Scene\n objects are static (no keyframes). "
                  "Keyframes attached to viewport objects\n lose sync when rendering with this script. \n\n")
            print(80 * "#")
            exit()

    #----[ CHECK IF LOSSLESS VIDEO CHECKBOX IS MARKED WHEN WE DON'T WANT IT ]
    if blender_use_lossless_output and blender_video_codec != 'H264':              #  | Blender leaves the lossless output checkbox set even after switching codecs.
        print(80 * "#")
        print("\n\n Please open your .blend file, go to the encoding section, switch to the 'H264'\n codec, "
              "and uncheck the 'Lossless Output' checkbox. Then set your codec of\n choice. This will prevent the "
              "script from accidentally using 'Lossless Output'\n when you want to use a bitrate setting.\n\n")
        print(80 * "#")
        exit()

    #----[ CHECK LOSSLESS OUTPUT OPTION AGAINST CONTAINER ]                        #  | When rendering a lossless video codec, AVI is the most compatible Container.
    if blender_use_lossless_output and not blender_image_sequence:
        if blender_vid_format != "AVI" and blender_vid_format != "H264":
            print(80 * "#")
            print(f"\n\n You selected a {blender_vid_format} container to hold lossless video. Please reopen the "
                  f"blend\n file and change to an 'AVI' container. This warning also happens if you left\n your "
                  f"'lossless output' checkbox marked. Please open your .blend file, go to\n the encoding section, "
                  f"switch to the 'H264' codec, and uncheck the\n 'Lossless Output' checkbox. Then set your codec of "
                  f"choice. This will prevent\n the script from accidentally using 'Lossless Output' when you want to "
                  f"use a\n bitrate setting.\n\n")
            print(80 * "#")
            exit()

    if not bypass_huffyuv_and_raw_avi_warnings:

        should_we_continue = 0 # default to continue

        #----[ DETECT FORMATS THAT HAVE LONG FFMPEG STREAM MAPPING TIMES ]         #  | Stream Mapping takes so long that script only renders slightly faster.
        if blender_file_format == "AVI_RAW":
            try:
                should_we_continue = int(input(80 * "#"
                                               + f"\n\n {blender_file_format} will only render around 10% faster than "
                                                 f"the standard Blender Interface. This is due to a long stream "
                                                 f"mapping time. Use AVI(H264) [Lossless] codec\n instead by opening "
                                                 f"blender and saving the new setting.\n\n ( Hide Future Warnings by "
                                                 f"setting bypass_huffyuv_and_raw_avi_warnings = True )\n\n"
                                               + 80 * "#"
                                               + "\n\n [1] to CONTINUE ANYWAY or Press [ENTER/RETURN] to Quit: "))
            except ValueError:
                print("Exiting Script...")
                exit()
            if should_we_continue != 1:
                print("Exiting Script...")
                exit()

        #----[ DETECT CODECS THAT HAVE LONG FFMPEG STREAM MAPPING TIMES ]          #  | Stream Mapping takes so long that the render time is about the same.
        if blender_video_codec == "HUFFYUV" and should_we_continue != 1:           #  | Use AVI(H264)[Lossless] instead
            try:
                should_we_continue = int(input(80 * "#"
                                               + f"\n\n {blender_video_codec} will render at about the same speed as "
                                                 f"the stardard Blender Interface.\n This is due to a long stream "
                                                 f"mapping time. Use AVI(H264) [Lossless] codec\n instead by opening "
                                                 f"blender and saving the newsetting.\n\n ( Hide Future Warnings by "
                                                 f"setting bypass_huffyuv_and_raw_avi_warnings = True ) \n\n"
                                               + 80 * "#"
                                               + "\n\n Press [1] to CONTINUE ANYWAY or Press [ENTER/RETURN] to Quit: "))
            except ValueError:
                print("Exiting Script...")
                exit()
            if should_we_continue != 1:
                print("Exiting Script...")
                exit()

        #----[ DETECT CODECS THAT DON'T SUPPORT CONSTANT RATE FACTOR ]
        if blender_video_codec != "H264" and blender_video_codec != "MPEG4" and blender_video_codec != "WEBM":
            if blender_constant_rate_factor != "NONE":
                print(80 * "#")
                print("\n Please reopen your .blend file, temporarily switch to H264 Codec. Select 'None'\n from "
                      "'Output Quality', then reselect the non-H264 codec that you want to use.\n You will need to "
                      "set the Constant Video Bitrate settings as well.\n Save and rerun the script. \n (Only H264 "
                      "supports the Constant Quality Settings; so you need to force \n Constant Bitrate instead.)\n")
                print(80 * "#")
                exit()

    #----[ DETECT IF FRAMESEVER IS SET ]
    if blender_file_format == "FRAMESERVER":
        print(80 * "#")
        print(f"\n Please reopen your .blend file and SAVE with a different Movie Format option.\n You selected: "
              f"{blender_file_format}. It isn't supported with this script.\n\n")
        print(80 * "#")
        exit()

    if blender_use_autosplit:
        print(80 * "#")
        print("\n Please reopen your .blend file and UNCHECK the 'AUTOSPLIT OUTPUT' option \n that is located in the "
              "encoding section.\n\n")
        print(80 * "#")
        exit()

#______________________________________________________________________________
#
#                 SET THE EXTENSIONS FOR AUDIO/VIDEO CODECS
#______________________________________________________________________________

if True:

    # ----[ GIFS DON'T USE AUDIO ]
    if render_gif:
        blender_audio_codec = "NONE"  # | GIF setting will disable Audio

    def make_lossless_audio():
        global blendfile_override_setting

    if blender_image_sequence or blender_file_format in ("AVI_JPEG", "AVI_RAW"):
        if not force_lossless_audio:
            blender_audio_codec = "NONE"
        else:
            blender_audio_codec = "PCM"
            blender_audio_bitrate = 192
            blender_audio_volume = 1.0
            blendfile_override_setting += \
                '    scene.render.ffmpeg.audio_codec = "PCM"\n' \
                + '    scene.render.ffmpeg.audio_bitrate = 192\n' \
                + '    scene.render.ffmpeg.audio_volume = 1.0\n'
            separate_audio_video = True

    if blender_file_format in ("AVI_JPEG", "AVI_RAW"):
        file_extension = ".avi"
    elif blender_vid_format in ("AVI", "H264", "XVID"):
        file_extension = ".avi"
    elif blender_vid_format == "DV":
        file_extension = ".dv"
    elif blender_vid_format == "FLASH":
        file_extension = ".flv"
    elif blender_vid_format == "MKV":
        file_extension = ".mkv"
    elif blender_vid_format == "MPEG1":
        file_extension = ".mpg"
    elif blender_vid_format == "MPEG2":
        file_extension = ".dvd"
    elif blender_vid_format == "MPEG4":
        file_extension = ".mp4"
    elif blender_vid_format == "OGG":
        file_extension = ".ogv"
    elif blender_vid_format == "QUICKTIME":
        file_extension = ".mov"
    elif blender_vid_format == "WEBM":
        file_extension = ".webm"
    else:
        print(f'Unknown blender_vid_extension {blender_vid_format}')
        exit(1)
    output_video_file += file_extension

    if blender_audio_codec is not None:
        if blender_audio_codec == "AAC":
            hold_audio_codec = "m4a"
        elif blender_audio_codec == "VORBIS":
            hold_audio_codec = "ogg"
        else:
            hold_audio_codec = blender_audio_codec.lower()                         # | Used for audio extension of all but aac
        output_audio_file += "." + hold_audio_codec

#______________________________________________________________________________
#
#                               DETECT OVERWRITES
#______________________________________________________________________________

if True:

    writing_files = []
    overwriting_files = []


    def verify_overwrites(pa):
        writing_files.append(pa)
        if os.path.exists(pa):
            overwriting_files.append(pa)


    if render_gif:
        verify_overwrites(output_gif_file)
    elif blender_image_sequence:
        verify_overwrites(output_seq_dir)
        if blender_audio_codec != "NONE":
            verify_overwrites(output_audio_file)
    else:
        verify_overwrites(output_video_file)
        if separate_audio_video and blender_audio_codec != "NONE":
            verify_overwrites(output_audio_file)

    if len(overwriting_files) > 0 and not auto_overwrite_files:
        print("FATAL: The following files will be overwritten:")
        for f in overwriting_files:
            print(f"  {f}")
        print("Set `auto_overwrite_files` to True, or manually remove the files.")
        exit(1)

#______________________________________________________________________________
#
#                             SCRIPT SETTINGS BANNER                           #  | Messy because Blender won't unmark settings, it hides and ignores.
#______________________________________________________________________________

#----[ DISPLAY THESE SETTINGS IN THE BANNER BEFORE RENDERING ]
if display_script_settings_banner:
    if my_platform == "Windows":
        print(25 * " " + "Press [ CTRL + BREAK ] to QUIT\n")

    elif my_platform == "Darwin":
        print(25 * " " + "Press [ CTRL + C ] to QUIT\n")

    elif my_platform == "Linux":
        print(25 * " " + "Press [ CTRL + C ] to QUIT\n")

    else:
        print(25 * " " + "Press [ CTRL + C ] to QUIT\n")

    print(17 * "#" + " THE VIDEO EDITOR'S RENDER SCRIPT FOR BLENDER " + 17 * "#"+ "\n")

    print(f" Working Temp Dir [{working_dir_temp}]\n")

    print(f" Use [ {cores_enabled} of {logical_cores_available} ] Logical CPU Cores ", end =" ")

    if show_render_status:
        print(" (Show Render Status [ON] (Slower))\n")
    else:
        print(" (Show Render Status [OFF] (faster))\n")

    if color_management_defauts_render_speed_up:
        print('| Color Mananagement Speedup Override is ON. This sets "View Transform" \n| and "Look" to 2.7X '
              'Defaults -- It\'s 3X faster (Script Line 205)\n')

    if show_cpu_core_lowram_notice:
        print("| For best render time, each Core needs 1.6GB to 3GB RAM. Reserve more CPU |\n| Cores if you "
              "experience severe slowdown due to Low RAM. (Script Line 141)|\n")

    if force_one_instance_render:
        print(" Script will Force 1 blender Instance. (MultiCore is [ OFF ])\n")

    if bypass_low_cpu_warnings:
        print(" Low CPU warnings are turned [ OFF ]\n")

    if permit_scene_strips:
        print(" Scene strips have been turned [ ON ] (May be Buggy)\n")

    if bypass_huffyuv_and_raw_avi_warnings:
        print(" HUFFYUV and RAW_AVI Warnings turned [ OFF ]\n")

    if auto_delete_temp_files:
        print(" Auto Deletion of Temp Files is [ ON ]\n")

    if len(overwriting_files) > 0:
        print(" WARNING: Some output files (***) will be overwritten:")
    else:
        print(" Output files:")
    for f in writing_files:
        if f in overwriting_files:
            print(f"   [{f}]***")
        else:
            print(f"   [{f}]")
    print('')

    print_banner = 30 * "-" + "[ RENDER SETTINGS ]" + 30 * "-" + "\n\n"

    if number_of_scenes > 1:
        print_banner += f" Your Project has [ {number_of_scenes} Scenes ], make sure that you save your blend " \
                        f"file with\n the first Scene showing. (First Scene is usually named, \"Scene\")\n\n"

    if blender_image_sequence:
        print_banner += f"  IMAGE SEQUENCE: [ {blender_file_format} ] [ {blender_x_times_res_percent} x {blender_y_times_res_percent} ]"
        print_banner += f" [ {the_framerate_float} FPS ]\n"
        print_banner += f"                   [ Frames: {start_frame_is} - {end_frame_is} ] [ Color Mode: {blender_color_mode} ]\n"

    if not blender_image_sequence:
        hide_codec = False

        if blender_file_format in ("AVI_JPEG","AVI_RAW"):
            print_banner += "  VIDEO: [ " + blender_file_format
            hide_codec = True
        elif blender_vid_format == "QUICKTIME":
            print_banner += "  VIDEO: [ MOV"                               #  | Quicktime Format uses MOV container
        elif blender_vid_format == "H264":
            print_banner += "  VIDEO: [ AVI"                               #  | H264 Format uses AVI container
        else:
            print_banner += "  VIDEO: [ " + blender_vid_format

        if not hide_codec:
            if blender_video_codec == "MPEG4":
                print_banner += " ( DIVX ) ] [ "                           #  | DIVX oddly reports that it uses MPEG4 codec
            elif blender_vid_format in ("MPEG1","MPEG2","FLASH","XVID", "DV"):
                print_banner += " ] [ "                                    #  | Remove False Codec Reporting
            elif blender_vid_format == "H264":
                print_banner += " (H264) ] [ "
            else:
                print_banner += f" ( {blender_video_codec} ) ] [ "
        else:
            print_banner += " ] [ "                                        #  | This close the AVI_JPEG and AVI_RAW settings

        print_banner += f"{blender_x_times_res_percent} x {blender_y_times_res_percent} ]"
        print_banner += f" [ {the_framerate_float} FPS ] [ GOP {blender_gop} ]\n"

        if blender_use_lossless_output and blender_video_codec == 'H264':
            print_banner += "          [ Lossless ] "
        else:
            if use_constant_bitrate:
                print_banner += f"          [ Bitrate: {blender_video_bitrate} kb/s ] "
            else:
                print_banner += f"        [ Quality: {blender_constant_rate_factor} ({blender_ffmpeg_preset})] "

            print_banner += f"[ Frames: {start_frame_is} - {end_frame_is} ] [ Color Mode: {blender_color_mode} ]\n"

    if render_gif:
        print_banner += f"\n  GIF RENDER is [ ON ]\n ([ {gif_framerate} FPS ] [ Stats:{stats_mode} ] "
        print_banner += f"[ Dither: {dither_options} ] [ X Scale: {str(gif_scale)}] [Scaler:{the_scaler}])\n"

    if blender_audio_codec != "NONE" and not render_gif:
        print_banner += "\n  AUDIO: [ " + blender_audio_codec
        if use_libfdk_acc:
            print_banner += " (libfdk)"
        print_banner += " ]"
        if use_ffmpeg_audio_bitrates:
            print_banner += f" [ {custom_audio_bitrate} kb/s ] ( FFmpeg Custom Bitrate [ ON ] )"
        else:
            print_banner += f" [ {blender_audio_bitrate} kb/s ]"

        print_banner += f" [ VOLUME: {int(round(blender_audio_volume * 100))}% ]\n"
        print_banner += f"          \n"
        print_banner += f"[ Sample Rate: {blender_audio_mixrate} ] [ Audio Format: {export_audio_format} ]"

    if force_one_instance_render:
        print_banner += f"\n  Render Engine: {blender_render_engine}\n"
        print_banner += 80 * "-"

    print(print_banner)

    print("\n" + 80 * "#" + "\n")

    while banner_wait_time:
        time_format = f'Execution Will Begin in {banner_wait_time:02d} seconds'
        print(time_format, end='\r')
        time.sleep(1)
        banner_wait_time -= 1

#______________________________________________________________________________
#
#                           CREATE FILES AND FOLDERS
#______________________________________________________________________________

if True:

    #----[ REMOVE OLD OUTPUTS ]
    if auto_overwrite_files: # should always be true, but just in case
        for f in overwriting_files:
            if not os.path.isdir(f):
                os.unlink(f)
            elif f == output_seq_dir:
                for fx in os.listdir(output_seq_dir):
                    os.unlink(os.path.join(output_seq_dir, fx))
            else:
                print(f'Fatal: refuse to overwrite a whole directory {f}')
                exit(2)

    #----[ CREATE FOLDERS TO STORE GENERATED TEMP FILES ]
    os.makedirs(path_to_av_source)
    os.makedirs(path_to_other_files)

    #----[ CREATE .BLEND OVERRIDE FILE ]
    with open(settings_file, "w+") as f:
        f.write(blendfile_override_setting)

#_______________________________________________________________________________
#
#                                 AUDIO SECTION
#_______________________________________________________________________________

#----[ START STOPWATCH TO TIME RENDERING ]
start_of_render_time = time.time()

if blender_audio_codec != "NONE":

    #----[ CHECK IF USER WANTS TO CONVERT TO A LOSSY AUDIO CODEC ]
    if blender_audio_codec == "PCM":
        user_wants_to_convert_audio = False
    else:
        user_wants_to_convert_audio = True

    # ----[ SET AUDIO FILE EXTENSIONS ]
    if export_audio_codec == "PCM":
        export_audio_file_extension = ".wav"
    else:
        export_audio_file_extension = "." + export_audio_codec.lower()

    if my_platform == "Windows":
        print("\n\n Cancel this Script at any time by pressing [ CTRL + BREAK ] \n")
    else:
        print("\n\n Cancel this Script at any time by pressing [ CTRL + C ] \n")

    print(f" Extracting Audio as {export_audio_container}({export_audio_codec})")
    temp_pcm = temp_to_wav + export_audio_file_extension

    blender_audio_extract_time_start = time.time()                             #  | Start PCM audio timer
    bpy.ops.sound.mixdown(
        filepath=temp_pcm,
        relative_path=False,
        check_existing=False,
        accuracy=export_audio_accuracy,
        container=export_audio_container,
        codec=export_audio_codec,
        format=export_audio_format,
        bitrate=export_audio_bitrate,
        split_channels=export_audio_split_channels,
    )
    if blender_audio_volume != 1.0:                                            #  | If Project Volume is changed, adjust it.
        move_wav_from = f"{temp_to_wav}_newVolume{export_audio_file_extension}"
        fix_volume = f'"{ffmpeg_path}" -loglevel warning -strict -2 -i "{temp_pcm}" ' \
                     + f'-af "volume={blender_audio_volume}" "{move_wav_from}"'
        subprocess.call(fix_volume, shell=True)
        os.remove(temp_pcm)                                            #  | Delete the orginal WAV file
        shutil.move(move_wav_from, temp_pcm)                           #  | Replace original WAV file with fixVolume version.
    blender_audio_extract_time_end = time.time()                               #  | End lossless audio timer

    if not user_wants_to_convert_audio:
        if blender_image_sequence or separate_audio_video:
            shutil.move(temp_pcm, output_audio_file)
            path_to_the_audio = None # won't use
        else:
            path_to_the_audio = temp_pcm
    else:

        #----[ CREATE LOSSY AUDIO COMMAND STRING ]
        wav_to_compressed_audio = f'"{ffmpeg_path}" -loglevel warning -strict -2 -i "{temp_pcm}"'
        if use_libfdk_acc:                                                         #  | If libfdk_acc is available it can be used here.
            wav_to_compressed_audio += " -c:a libfdk_acc "
        else:
            wav_to_compressed_audio += f" -c:a {blender_audio_codec.lower()} "

        #----[ SET SUPPORTED AUDIO BITRATE RANGES ]
        if blender_audio_codec == "AC3":
            min_audio_bitrate = min_audio_bitrate_ac3
            max_audio_bitrate = max_audio_bitrate_ac3
        elif blender_audio_codec == "AAC":
            min_audio_bitrate = min_audio_bitrate_aac
            max_audio_bitrate = max_audio_bitrate_aac
        elif blender_audio_codec == "MP2":
            min_audio_bitrate = min_audio_bitrate_mp2
            max_audio_bitrate = max_audio_bitrate_mp2
        elif blender_audio_codec == "MP3":
            max_audio_bitrate = max_audio_bitrate_mp3
            min_audio_bitrate = min_audio_bitrate_mp3

        #----[ IF USING FFMPEG BITRATE, KEEP IN SUPPORTED RANGE ]
        if use_ffmpeg_audio_bitrates:
            if custom_audio_bitrate < min_audio_bitrate:
                blender_audio_bitrate = min_audio_bitrate
            elif custom_audio_bitrate > max_audio_bitrate:
                blender_audio_bitrate = max_audio_bitrate
            else:
                blender_audio_bitrate = custom_audio_bitrate
        else:
            #----[ IF USING BLENDER'S BITRATE, KEEP IN SUPPORTED RANGE ]
            if blender_audio_bitrate < min_audio_bitrate:
                blender_audio_bitrate = min_audio_bitrate
            if blender_audio_bitrate > max_audio_bitrate:
                blender_audio_bitrate = max_audio_bitrate
        wav_to_compressed_audio += f" -b:a {blender_audio_bitrate}k"

        if blender_image_sequence or separate_audio_video:
            compressed_audio = output_audio_file
        else:
            compressed_audio = temp_to_wav + "." + hold_audio_codec
        wav_to_compressed_audio += f' "{compressed_audio}"'

        print(f' Converting Audio using {blender_audio_codec} codec using bitrate of {blender_audio_bitrate}k')

        #----[ CONVERT WAV TO COMPRESSED FORMAT ]
        audio_conversion_time_start = time.time()                              #  | Start audio conversion timer
        subprocess.call(wav_to_compressed_audio, shell=True)
        audio_conversion_time_end = time.time()                                #  | End audio conversion timer

        #----[ MAKE SURE THAT A LOSSY FILE WAS CREATED ]
        if not os.path.isfile(compressed_audio):
            print(" There was an error compressing your audio. Please change your render settings.")
            exit()

        if blender_image_sequence or separate_audio_video:
            path_to_the_audio = None # won't use
        else:
            path_to_the_audio = compressed_audio

#______________________________________________________________________________
#
#              CREATE STRING FOR THE BACKGROUND BLENDER INSTANCES
#______________________________________________________________________________

if True:

    #----[ SET NUMBER OF FRAMES THAT WILL BE RENDERED ON EACH ENABLED CORE ]
    portion_of_frames_per_core = math.ceil(total_frames / cores_enabled)

    #----[ INITIAL LOOP VARIABLES ]
    next_core = 1
    new_start_frame_number = start_frame_is
    new_end_frame_number = start_frame_is + portion_of_frames_per_core

    while next_core <= cores_enabled:

        blender_command += start_blender
        #----[ IF WINDOWS PLATFORM IS PRESENT, CREATE INDIVIDUAL LOCK FILES ]
        if my_platform == "Windows":
            blender_command += fr'9>\"%lock%{next_core}\" '  #  | only Windows needs to create a lock file for each blender job.

        blender_command += \
            f'"{blender_path}" -b "{os.path.abspath(bpy.context.blend_data.filepath)}"' \
            + f' -P "{settings_file}"' \
            + f' -E {blender_render_engine}' \
            + f' -s {new_start_frame_number:d}' \
            + f' -e {new_end_frame_number:d}'

        if not blender_image_sequence:
            fn = f'{next_core:d}{file_extension}'
            blender_command += f' -o "{os.path.join(path_to_av_source, fn)}" -a {ampersand}\n'
        else:
            blender_command += f' -o "{output_seq_dir}//" -F {blender_file_format} -x 1 -a {ampersand}\n'

        new_start_frame_number = new_end_frame_number + 1
        new_end_frame_number = new_start_frame_number + portion_of_frames_per_core

        if new_end_frame_number > end_frame_is:
            new_end_frame_number = end_frame_is

        next_core += 1

    #----[ THE WINDOWS LOCK FILE ROUTINE (ENCAPSULATES BLENDER INSTANCE STRING) ]
    if my_platform == "Windows":                                                   #  | Without testable lock files, Windows
                                                                                   #  | doesn't WAIT to finish the blender jobs
        wait_blender_routine =\
            '@echo off\n'\
            + 'setlocal\n'\
            + 'set "lock=%temp%\wait%random%.lock"\n'\
            + '\n'

        #----[ ADD OUR BACKGROUND BLENDER COMMAND STRING HERE ]
        wait_blender_routine += blender_command

        wait_blender_routine +=\
            '\n'\
            + ':Wait for all Instances to finish \n'\
            + '1>nul 2>nul ping /n 2 ::1\n'\
            + 'for %%F in ("%lock%*") do (\n'\
            + '  (call ) 9>"%%F" || goto :Wait\n'\
            + ') 2>nul\n'\
            + '\n'\
            + '::delete the lock files\n'\
            + 'del "%lock%*"\n'

        blender_command = wait_blender_routine

#______________________________________________________________________________
#
#                      VIDEO CONCATENATION (if not img seq)
#                    MUX AUDIO AND VIDEO INTO ONE MEDIA FILE
#______________________________________________________________________________

if my_platform != "Windows":
    full_command_string = "#!/bin/bash\n\nset -euxo pipefail\n"
else:
    full_command_string = ""
full_command_string += blender_command + wait_here

if not blender_image_sequence:

    vid_file_list = ""
    for i in range(cores_enabled):
        fn = f'{i+1:d}{file_extension}'
        vid_file_list += f"file '{os.path.join(path_to_av_source, fn)}'\n"
    with open(concat_file, "w+") as f:
        f.write(vid_file_list)

    #----[ CREATE COMMAND STRING FOR VIDEO CONCATENATION ]
    full_command_string += f'"{ffmpeg_path}" -hide_banner -strict -2 -f concat -safe 0 -i "{concat_file}" -c copy '
    if (blender_audio_codec != "NONE" and not separate_audio_video) or render_gif:
        full_command_string += f'"{temp_video_without_audio}{file_extension}"\n'
    else:
        full_command_string += f'"{output_video_file}"\n'

    #----[ CREATE A STRING THAT ADDS AUDIO TO VIDEO ]
    if blender_audio_codec != "NONE" and not separate_audio_video:
        full_command_string += \
            f'"{ffmpeg_path}" -hide_banner -strict -2 -i "{temp_video_without_audio}{file_extension}"' \
            + f' -i "{path_to_the_audio}"' \
            + f' {post_full_audio} "{output_video_file}" {post_full_audio_arg2}\n'

#______________________________________________________________________________
#
#                              CREATE ANIMATED GIF
#______________________________________________________________________________

if not blender_image_sequence and render_gif:
    full_command_string += \
        f'"{ffmpeg_path}" -loglevel warning -i "{temp_video_without_audio}{file_extension}" ' \
        + f'-vf "fps={gif_framerate},scale={gif_scale}:-1:flags={the_scaler},palettegen=stats_mode={stats_mode}" ' \
        + f'-y "{temp_png_palette}"\n'

    full_command_string += \
        f'"{ffmpeg_path}" -loglevel warning -i "{temp_video_without_audio}{file_extension}" ' \
        + f'-i "{temp_png_palette}" ' \
        + f'-lavfi "fps={gif_framerate},scale={gif_scale}:-1:flags={the_scaler} [x]; [x][1:v] paletteuse=dither={dither_options}" ' \
        + f'-y "{output_gif_file}"\n'

#______________________________________________________________________________
#
#                     EXECUTE COMMAND STRINGS FROM TERMINAL
#______________________________________________________________________________

if True:

    #----[ WRITE COMMAND STRINGS TO FILE ]
    with open(render_file, "w+") as f:
        f.write(full_command_string)

    #----[ CREATE EXECUTABLE RENDER FILE COMMAND ]
    commands_to_execute = f'{use_bash}"{render_file}"'
    print(commands_to_execute)

    #----[ EXECUTE THE RENDER COMMAND FILE ]
    if not show_render_status:                                                #  | Render Status happens in this section. Thanks to https://github.com/mitxela
        subprocess.call(commands_to_execute, shell=True) # run script in terminal
    else:
        proc = subprocess.Popen(commands_to_execute, shell=True, stdout=subprocess.PIPE)

        pattern = re.compile(r'^ Time:') # printed after each frame has rendered
        rendered_frames = 0

        for line in proc.stdout:
            if pattern.match(line.decode('utf-8')):
                rendered_frames += 1
                print(
                    f"Progress: {100 * rendered_frames / total_frames:02.2f}% ({rendered_frames:d} / {total_frames:d})",
                    end='\r')
        proc.wait()
        print('')

#______________________________________________________________________________
#
#                               SCRIPT TIMER INFO
#______________________________________________________________________________

if True:

    def show_time(st, t):
        m, s = divmod(int(t), 60)
        h, m = divmod(m, 60)
        if h > 0:
            print(f"\n {st} took {h:d} Hours {m:02d} Minutes {s:02d} Seconds\n")
        elif m > 0:
            print(f"\n {st} took {m:02d} Minutes {s:02d} Seconds\n")
        else:
            print(f"\n {st} took {s:02d} Seconds\n")


    print(80 * "#" + "\n\n")
    if blender_audio_codec != "NONE":
        show_time('Audio Extract', blender_audio_extract_time_end - blender_audio_extract_time_start)
        if user_wants_to_convert_audio:
            show_time('Audio Encode', audio_conversion_time_end - audio_conversion_time_start)
    show_time('Render (incl. ffmpeg concat and A/V mux)', time.time() - start_of_render_time)
    print("\n\n" + 80 * "#")

#______________________________________________________________________________
#
#                              DELETE MEDIA FILES
#______________________________________________________________________________

#----[ DELETE WORKING DIRECTORY ]
if auto_delete_temp_files:
    try:
        shutil.rmtree(working_dir_temp)
    except:
        print(80 *"#")
        print(f" {working_dir_temp} is locked by the Operating System. So it can\'t be Deleted\n automatically. "
              f"This happens when a file in the {working_dir_temp} is open in\n your file browser or terminal and "
              f"the script attempts to Delete. This doesn\'t\n harm the final video render in any way. This "
              f"script will run normally the next\n time you run it. Just remember to stop viewing the files in "
              f"the\n {working_dir_temp} before the script finishes.")
