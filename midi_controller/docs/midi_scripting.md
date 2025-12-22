MIDI

# MIDI Scripting Device API reference <a href="app_feature.htm" class="link-img"><span class="image placeholder" data-original-image-src="img_glob/global_onlyfledition.gif" data-original-image-title="This feature is available only in Fruity Edition and Producer Edition." height="25"></span></a>

**MIDI scripting** allows native **support for any MIDI controller**. Scripts are written in 'Python' code, stored in a plain text file, that FL Studio uses to translate commands between the controller and FL Studio. MIDI communication can go in both directions; The controller can access features in the FL Studio code (as listed below), and FL Studio can send data back to the controller (such as lighting pads or showing track names).

FL Studio MIDI **scripts are based on <a href="https://www.python.org/about/gettingstarted/" class="extLink" target="_blank">Python</a>**. You do not need to install anything, FL Studio will handle scripts directly. When scripts are created in the folders shown below, the scripted device will display in the **Controller type** menu under the [MIDI Settings](envsettings_midi.htm) tab. From there, select the controller and use it as normal.

**NOTES:**

- **Script hierarchy** - As FL Studio natively handles many MIDI functions and messages, this allows you to write **simple scripts** to handle specific cases or inputs and leave the rest to **FL Studio's generic MIDI support**. For example, you do not need to tell FL Studio what to do with MIDI notes. If the script doesn't specifically make changes to default behavior, FL Studio will handle them as normal.
- **Scripts are complex** - With power and flexibility comes complexity. MIDI scripting is intended for **hardware manufacturers** and **advanced users** to create custom support for MIDI controllers. If you are new to programming, MIDI scripting will be confronting and confusing at first. This is normal, but patience and persistence will be rewarded! There are some simple examples to get started on our user forum listed below.

#### Support Forum

FL Studio customers can access the <a href="https://support.image-line.com/redirect/midi_scripting_forum" class="extLink" target="_blank">MIDI Controller Scripting</a> forum to discuss scripting, share scripts, make feature requests and report issues.

#### Script Locations and File Names

FL Studio will check the following locations for MIDI Scripts and related files:

- **Script files** - Scripted device files are located in the [User data folder](envsettings_files.htm#userdata) under *... Documents\Image-Line\FL Studio\Settings\Hardware\\**devicename\device\_devicename.py***.
  - **Script folder naming** - The sub folder '**devicename**' is arbitrary and can be anything you like. Normally you would use the name of the MIDI hardware you are scripting for.
  - **Script file naming** - The 'device\_**devicename**' (bold part) can be anything you like to identify the MIDI script file. **NOTE:** 'device\_**devicename**.py' is **mandatory** for the device to be processed by FL Studio. You can use spaces and capitals for **devicename** e.g. 'device\_**My PHAT Controller**.py'.
  - **The controller name** - Shown in the [MIDI Settings](envsettings_midi.htm) &gt; **Controller type** menu is defined on **first line** of 'device\_devicename.py' script file, e.g. **\#name=AKAI FL Studio Fire**. This will appear in the device list as '**AKAI FL Studio Fire (user)**'. The **(user)** suffix is to distinguish your device scripts from installed factory scripts.  
    The controller name is **required** and your script will be not recognized by FL Studio without it!
  - **[Editing .py script files](midi_scripting.htm#script_editing)** - Use any text editor. If you are editing existing scripts, make a backup of the original files.
- **Device (launchmap) pages** (optional) - Files are located in *... Documents\Image-Line\FL Studio\Settings\Hardware\\**devicename**\\**Page(number).scr***. Device pages are special use-case and not normally used for standard MIDI controllers.
  - **Launchmap files** - Launchmaps are custom files that provide different behavior for a controller depending on what mode it is launched in. See the MIDI Controller reference post <a href="https://forum.image-line.com/viewtopic.php?f=1914&amp;t=92193" class="extLink" target="_blank">Custom controller layouts</a>. See also the [launchMapPages module](#script_module_launchpad).
- **Custom modules** - You can include custom or external modules by placing them in the FL Studio installation, **shared library folder**:
  - **[Windows](app_flstudioinstallationfiles.htm#windows_cleaninstall)** - ... /Program Files (x86)/Image-Line/Shared/Python/**Lib**
  - **[macOS](app_flstudioinstallationfiles.htm#macos_install)** - ... \Library\Application support\Image-line\Shared\Python\\**Lib**

**NOTE:** You do not need to install the Python compiler to edit and maintain these scripts, you can open and edit **.py files** with any text editor. FL Studio MIDI scripting is based on events **(Script events)** fired by FL Studio and responses **(Callbacks)** to these events.

#### Getting Started Tutorials

**The basics of working with Script Files:**

To start from scratch, you need to create a script file, in the correct location in the FL Studio [User data folder](envsettings_files.htm#userdata). This section and video shows you how to do that, step-by-step.

1.  **Create a folder** - Using the file browser in your Operating System of choice, browse to your FL Studio [User data folder](envsettings_files.htm#userdata), usually '...Documents\Image-Line\FL Studio\Settings\Hardware\\**YourScriptSubFolder**', where 'YourScriptSubFolder' is a sub folder you created for your script.
2.  **Create a script file** - In the 'YourScriptSubFolder' folder, create a plain text file '**device\_YourScriptName.txt**'. Open the text file and add the following line of text, which will be the script name that appears in the [MIDI Settings](envsettings_midi.htm) &gt; **Controller type** list:
    - \# name=My First Script

    **NOTE:** There's more information about predefined paramaters [here](#script_parameters).
3.  **Change the file extension type to .py** - Change the file extension type from .txt to .py. To do this you must have file-type extensions activated in the browser on your computer. After that, just rename a plain text file 'device\_ThisIsMyFistScript**.txt**' to 'device\_ThisIsMyFistScript**.py**', for example. You can also use the operating system options to open files of type .py in the text editor of your choice.
4.  **Select your script in the MIDI Settings** - You will now see your script in the **MIDI Settings &gt; Controller type** list as **My First Script (user)**.
5.  **Edit the script** - Open this script in FL Studio from the **VIEW (menu) &gt; Script output &gt; Edit script (button)**
6.  The following video shows steps 4 and 5 above.

**This video shows how to find MIDI data coming from a controller, to use in a script:**

After creating a script. You will probably want to identify data coming from your controller you want to link to a function in FL Studio, this video shows such an example.

**NOTE:** For the **Interpreter** tab to work you must select a script from the MIDI Settings &gt; Controller type option.

The script used in this tutorial is available <a href="https://forum.image-line.com/viewtopic.php?p=1483607#p1483607" class="extLink" target="_blank">here</a>.

#### Script Modules

Script functions (**callbacks**) are the instructions FL Studio will recognize and act upon in the Python code. Callbacks are organized in **modules** according to FL Studio target features (Playlist, Patterns, Device etc.). To use callbacks in script, you must load the callback module by including it at the top of the script with 'import':

- **import *module*** (e.g. import playlist) - **NOTE:** Module names use **Lower <a href="https://en.wikipedia.org/wiki/Camel_case" class="extLink" target="_blank">Camel Case</a>**. Available modules:
  - [playlist](#script_module_playlist)
  - [channels](#script_module_channels)
  - [mixer](#script_module_mixer)
  - [patterns](#script_module_patterns)
  - [arrangement](#script_module_arrangements)
  - [ui](#script_module_ui)
  - [transport](#script_module_transport)
  - [device](#script_module_device)
  - [plugins](#script_module_plugin)
  - [general](#script_module_general)
  - [launchMapPages](#script_module_launchpad)

#### Script Functions

**Callbacks** are functions that execute features or act on components in FL Studio. You can for example, use a callback function to name an instrument Channel, move a Channel up/down or delete it. Or, more simply remap the transport buttons in FL Studio to your controller. In other words, **callbacks** give you deep control over FL Studio and how it operates. To use function in script use following syntax:

- **module.functionName(arguments)** - Where 'module' is module name. **NOTE:** Function names use **Lower Camel Case**.

#### Script Events

Script events are functions called by FL Studio, if script needs to respond to the event, add event function to script:

- **def eventName(arguments)** - Write response code inside this function. **NOTE:** Event names use **Camel Case**

#### Script predefined parameters

Script '**predefined parameters**' are a way to tell FL Studio some additional information about your script. Include predefined parameters at the top of main .py file. Predefines include:

- **name** (required) - The name of your script shown in the [MIDI Settings &gt; Controller type](envsettings_midi.htm) list.
- **url** (optional) - Image-Line MIDI Scripting forum link, where users can discuss or get help for your script. URLs must start with https://forum.image-line.com. For example, the link to the 'Working Scripts list' is <a href="https://forum.image-line.com/viewtopic.php?f=1994&amp;t=228179" class="extLink" target="_blank">https://forum.image-line.com/viewtopic.php?f=1994&amp;t=228179</a>. You can link to any post in the MIDI Scripting forum.
- **receiveFrom** (optional) - Specify the device name to receive MIDI events from. If specified, FL Studio will dispatch messages (sent via device.dispatch function) from the specified device.
- **supportedDevices** (optional) - Comma separated list of device names supported by your script. If specified, FL Studio will automatically link a script to devices matching names in this list.
- **supportedHardwareIds** (optional) - Comma separated list of device hardware id's supported by your script. If specified, FL Studio will automatically link the script to devices with same hardware ids. **TIP:** You can use partial hardware ID's to omit device firmware version numbers.

**Example:**

- \# name=My Launch Control script  
  \# url=https://forum.image-line.com/viewtopic.php?p=1494175#p1494175  
  \# supportedDevices=Launch Control XL,Launch Control XL mkII  
  \# receiveFrom=Forward Device  
  \# supportedHardwareIds=00 20 29 61 00 00 00 00 00 02 07  

#### Tools for Testing Functions and Editing Scripts

Open the [VIEW menu &gt; Script output](menu_view.htm#script_output) window:

- **Interpreter** - This Tab allows you to enter and test Script commands to check they work as expected.

- **Script** - When a MIDI Script is selected in the MIDI Settings the **second tab** will show with the name of the device (in this case FL STUDIO FIRE). When there are **unhandled MIDI events**, the data will be displayed here. **NOTE:** The [Debugging log tab](envsettings_debug.htm) also shows ALL incoming MIDI data.

  <span class="image placeholder justImages" original-image-src="img_shot/midiscripting_viewoutput_script.png" original-image-title="" width="600"></span>

  **NOTE:** If your script loads and compiles correctly, you will see **init ok**, Initialization OK, in the Script window.

  - **Clear output** - Clears the tabs data.
  - **Edit script** - Open the current script in the system text editor to make changes.
  - **Reload** - Apply the edited script so you don't need to restart FL Studio to test it.

## Script events

<table class="tableList" style="width:98%">
<colgroup>
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
</colgroup>
<thead>
<tr>
<th scope="row">Name</th>
<th scope="row">Arguments</th>
<th scope="row">Documentation</th>
<th scope="row">Version</th>
</tr>
</thead>
<tbody>
<tr>
<td>OnInit</td>
<td>-</td>
<td>Called when the script has been started.</td>
<td>1</td>
</tr>
<tr>
<td>OnDeInit</td>
<td>-</td>
<td>Called before the script will be stopped.</td>
<td>1</td>
</tr>
<tr>
<td>OnMidiIn</td>
<td><a href="#eventType">eventData</a></td>
<td>Called first when a MIDI message is received. Set the event's handled property to True if you don't want further processing - (only raw data is included here: handled, timestamp, status, data1, data2, port, sysex, <a href="#pmeFlags">pmeflags</a>)<br />
use this event for filtering, use OnMidiMsg event for actual processing ...</td>
<td>1</td>
</tr>
<tr>
<td>OnMidiMsg</td>
<td><a href="#eventType">eventData</a></td>
<td>Called for all MIDI messages that were not handled by OnMidiIn.</td>
<td>1</td>
</tr>
<tr>
<td>OnSysEx</td>
<td><a href="#eventType">eventData</a></td>
<td>Called for note sysex messages that were not handled by OnMidiIn.</td>
<td>1</td>
</tr>
<tr>
<td>OnNoteOn</td>
<td><a href="#eventType">eventData</a></td>
<td>Called for note on messages that were not handled by OnMidiMsg.</td>
<td>1</td>
</tr>
<tr>
<td>OnNoteOff</td>
<td><a href="#eventType">eventData</a></td>
<td>Called for note off messages that were not handled by OnMidiMsg.</td>
<td>1</td>
</tr>
<tr>
<td>OnControlChange</td>
<td><a href="#eventType">eventData</a></td>
<td>Called for CC messages that were not handled by OnMidiMsg.</td>
<td>1</td>
</tr>
<tr>
<td>OnProgramChange</td>
<td><a href="#eventType">eventData</a></td>
<td>Called for program change messages that were not handled by OnMidiMsg.</td>
<td>1</td>
</tr>
<tr>
<td>OnPitchBend</td>
<td><a href="#eventType">eventData</a></td>
<td>Called for pitch bend change messages that were not handled by OnMidiMsg.</td>
<td>1</td>
</tr>
<tr>
<td>OnKeyPressure</td>
<td><a href="#eventType">eventData</a></td>
<td>Called for key pressure messages that were not handled by OnMidiMsg.</td>
<td>1</td>
</tr>
<tr>
<td>OnChannelPressure</td>
<td><a href="#eventType">eventData</a></td>
<td>Called for channel pressure messages that were not handled by OnMidiMsg.</td>
<td>1</td>
</tr>
<tr>
<td>OnMidiOutMsg</td>
<td><a href="#eventType">eventData</a></td>
<td>Called for short MIDI out messages sent from MIDI Out plugin - (event properties are limited to: handled, status, data1, data2, port, midiId, midiChan, midiChanEx)</td>
<td>1</td>
</tr>
<tr>
<td>OnIdle</td>
<td>-</td>
<td>Called from time to time. Can be used to do some small tasks, mostly UI related. For example: update activity meters.</td>
<td>1</td>
</tr>
<tr>
<td>OnProjectLoad</td>
<td>int <a href="OnProjectLoadStatus">status</a></td>
<td>Called when project is loaded</td>
<td>16</td>
</tr>
<tr>
<td id="OnRefreshEvent">OnRefresh</td>
<td>int <a href="#OnRefreshFlags">flags</a></td>
<td>Called when something changed that the script might want to respond to.</td>
<td>1</td>
</tr>
<tr>
<td>OnDoFullRefresh</td>
<td>-</td>
<td>Same as OnRefresh, but everything should be updated.</td>
<td>1</td>
</tr>
<tr>
<td>OnUpdateBeatIndicator</td>
<td>int value</td>
<td>Called when the beat indicator has changes - "value" can be off = 0, bar = 1 (on), beat = 2 (on)</td>
<td>1</td>
</tr>
<tr>
<td>OnDisplayZone</td>
<td>-</td>
<td>Called when playlist zone changed</td>
<td>1</td>
</tr>
<tr>
<td>OnUpdateLiveMode</td>
<td>int lastTrack</td>
<td>Called when something about performance mode has changed.</td>
<td>1</td>
</tr>
<tr>
<td>OnDirtyMixerTrack</td>
<td>int index</td>
<td>Called on mixer track(s) change, 'index' indicates track index of track that changed or -1 when all tracks changed<br />
collect info about 'dirty' tracks here but do not handle track(s) refresh, wait for OnRefresh event with HW_Dirty_Mixer_Controls flag</td>
<td>1</td>
</tr>
<tr>
<td>OnDirtyChannel</td>
<td>int index, int
flag</td>
<td>Called on channel rack channel(s) change, 'index' indicates channel that changed or -1 when all channels changed<br />
collect info about 'dirty' channels here but do not handle channels(s) refresh, wait for OnRefresh event with HW_ChannelEvent flag</td>
<td>16</td>
</tr>
<tr>
<td>OnFirstConnect</td>
<td>-</td>
<td>Called when device is connected for the first time (ever)</td>
<td>17</td>
</tr>
<tr>
<td>OnUpdateMeters</td>
<td>-</td>
<td>Called when peak meters needs to be updated<br />
call device.setHasMeters() in onInit to use this event!</td>
<td>1</td>
</tr>
<tr>
<td>OnWaitingForInput</td>
<td>-</td>
<td>Called when FL Studio is set in <a href="https://www.image-line.com/support/flstudio_online_manual/html/toolbar_panels.htm#panel_shortcuticons_wait" target="_blank">waiting mode</a></td>
<td>1</td>
</tr>
<tr>
<td>OnSendTempMsg</td>
<td>string message, int duration</td>
<td>Called when hint message (to be displayed on controller display) is sent to the controller<br />
duration of message is in ms</td>
<td>1</td>
</tr>
</tbody>
</table>

## Modules and functions

<span id="script_module_playlist"></span>

### Playlist module

Playlist module allows you to control FL Studio [Playlist](https://www.image-line.com/support/flstudio_online_manual/html/playlist.htm)

Command

Arguments

Result

Documentation

Version

getTrackName

int index

string

Returns the name of the track at "index".

1

setTrackName

int index, string name

\-

Changes the name of the track at "index" to "name".

1

getTrackColor

int index

int

Returns the color of the track at "index" as an RGBA value.

1

setTrackColor

int index, int color

\-

Changes the color of the track at "index" to the value of "color".

1

isTrackMuted

int index

int

Returns True if the track at "index" is muted.

1

muteTrack

int index, (int value\* = -1), (int inGroup\*\* = 0)

\-

Toggle whether the track at index is muted. An unmuted track will become muted and a muted track will become unmuted.  
Set optional value to 1(mute) or to 0(unmute) track.  
Set optional 'inGroup' to 1 to mute/unmute track group (alt + click in FL)

1, \*30, \*33

isTrackMuteLock

int index

int

Returns True if the Mute for track at "index" is locked.

2

muteTrackLock

int index

\-

Toggles the Mute lock status of the track at "index".

2

isTrackSolo

int index

int

Returns True if the track at "index" is currently solo'd.

1

soloTrack

int index, (int value = -1), (int inGroup\* = 0)

\-

toggle the solo state of the track at "index"  
set optional 'value' to 1 to solo track or to 0 unsolo track  
set optional 'inGroup' to 1 to solo/unsolo track group (alt + right click in FL)

1, \*30

isTrackSelected

int index

int

Returns True if the track at "index" is selected.

12

selectTrack

int index

\-

Toggle selection of the track at "index".

12

selectAll

\-

\-

Select all playlist tracks.

12

deselectAll

\-

\-

Deselect all playlist tracks.

12

getTrackActivityLevel

int index

float

Returns the activity level of the track at "index" (zero if not active, &gt; 0 if active).

1

getTrackActivityLevelVis

int index

float

Returns the visual activity level of the track at "index" as a normalized value.

1

getDisplayZone

\-

int

Returns current display zone in the playlist or zero if none.

1

lockDisplayZone

int index, int value

\-

Lock display zone at "index".

1

liveDisplayZone

int left, int top, int right, int bottom, (int duration = 0)

\-

Set the display zone in the playlist to the specified co-ordinates - use optional 'duration' parameter to make display zone temporary

1

getLiveLoopMode

int [index](#getLiveLoopModeResult)

int

Get live loop mode.

1

getLiveTriggerMode

int index

int

Get live trigger mode - Result is one of the [constants](#getLiveTriggerModeResult)

1

getLivePosSnap

int index

int

Get live pos snap - Result is one of the [constants](#getLiveSnapResult)

1

getLiveTrigSnap

int index

int

Get live trig snap - Result is one of the [constants](#getLiveSnapResult)

1

getLiveStatus

int index, (int [mode](#getLiveStatusMode) = LB\_Status\_Default)

int

Get live status for track at "index" - Result depends on mode.

1

getLiveBlockStatus

int index, int blockNum, (int [mode](#getLiveStatusMode) = LB\_Status\_Default)

int

Get live block status for track at "index" and for block "blockNum"  
Result depends on mode -

1

getLiveBlockColor

int index, int blockNum

int

Get live block color for track at "index" and for block "blockNum"

1

triggerLiveClip

int index, int blockNum, int [flags](#triggerLiveClipFlags), (float velocity = -1)

\-

Trigger live clip for track at "index" and for block "blockNum". Set blockNum to -1 and use the TLC\_Fill flag to stop live clips on this track.

1

refreshLiveClips

int index, int value

\-

Refresh live clips for track at "index".

1

incLivePosSnap

int index, int value

\-

Increase live pos snap for track at "index"

1

incLiveTrigSnap

int index, int value

\-

Increase live trig snap for track at "index".

1

incLiveLoopMode

int index, int value

\-

Increase live loop mode for track at "index"

1

incLiveTrigMode

int index, int value

\-

Increase live trig mode for track at "index"

1

getVisTimeBar

\-

int

Get time bar.

1

getVisTimeTick

\-

int

Get time tick.

1

getVisTimeStep

\-

int

Get time step.

1

getPerformanceModeState

\-

int

Returns 1 when the PL is in performance mode, 0 when it's not.

21

### Channels module

Channels module allows you to control FL Studio [Channels](https://www.image-line.com/support/flstudio_online_manual/html/channelrack.htm)

'index' is respecting channel groups, 'indexGlobal' is global index

Command

Arguments

Result

Documentation

Version

selectedChannel

(int canBeNone = 0), (int offset = 0), (int indexGlobal = 0)

int

Returns 'index' (respecting groups) of the first selected channel  
When there is no selection, function will return 0 (or -1 if canBeNone is 1)  
Use optional 'offset' parameter to find other selected channels  
Set optional 'indexGlobal' to 1 to return global channel index instead of index respecting groups  

5

channelNumber

(int canBeNone = 0), (int offset = 0)

int

Returns 'indexGlobal' of the first selected channel  
When there is no selection, function will return -1 (or 0 if canBeNone is 1)  
Use optional 'offset' parameter to find other selected channels

1

channelCount

(int globalCount\* = 0)

int

Returns the number of channels respecting groups - set optional globalCount\* parameter to 1 to get count of all channels

1, \*3

getChannelName

int index, (bool useGlobalIndex\* = False)

string

Returns the name of the channel at "index".

1, \*33

setChannelName

int index, string name, (bool useGlobalIndex\* = False)

\-

Changes the name of the channel at "index" to "name".

1, \*33

getChannelColor

int index, (bool useGlobalIndex\* = False)

int

Returns the color of the channel at "index".

1, \*33

setChannelColor

int index, int color, (bool useGlobalIndex\* = False)

\-

Changes the color of the channel at "index" to the value of "color".

1, \*33

isChannelMuted

int index, (bool useGlobalIndex\* = False)

int

Returns True if the channel at "index" is muted.

1, \*33

muteChannel

int index, (int value = -1), (bool useGlobalIndex\* = False)

\-

Toggles the muted state of the channel at "index" if value is default, otherwise mute channel if value is 1, or unmute if value is 0.

1, \*33

isChannelSolo

int index, (bool useGlobalIndex\* = False)

int

Returns True if the channel at "index" is soloed.

1, \*33

soloChannel

int index, (int value\* = -1), (bool useGlobalIndex\*\* = False)

\-

Toggles the state of the channel at "index" if value is default. Otherwise solo channel if value is 1 and unsolo if value is 0.

1, \*30, \*\*33

getChannelVolume

int index, (int useDb\* = 0), (bool useGlobalIndex\*\* = False)

float

Returns the normalized volume (between 0 and 1.0) of the channel at "index" - set optional useDb to 1 to get volume in dB

1, \*14, \*\*33

setChannelVolume

int index, float volume, (int [pickupMode](#pickupModes)\* = PIM\_None), (bool useGlobalIndex\*\* = False)

\-

Changes the volume for the channel at "index" - volume is a value between 0 and 1.0  
use optional pickupMode to override FL default pickup option

1, \*13, \*\*33

getChannelPan

int index, (bool useGlobalIndex\* = False)

float

Returns the pan value for the channel at "index", as a value between -1.0 and +1.0.

1, \*33

setChannelPan

int index, float pan, (int [pickupMode](#pickupModes)\* = PIM\_None), (bool useGlobalIndex\*\* = False)

\-

Change the pan value of the channel at "index" to the value of "pan" - The value should be between -1.0 and +1.0 - use optional pickupMode to override FL default pickup option

1, \*13, \*\*33

getChannelPitch

int index, (int mode = 0), (bool useGlobalIndex\* = False)

float/int

Returns the pitch value for the channel at "index", as a value between -1.0 and +1.0 - use optional mode parameter to return pitch in semitones (mode = 1) or to return pitch range (mode = 2)

8, \*33

setChannelPitch

int index, float value, (int pitchUnit = 0), (int [pickupMode](#pickupModes)\* = PIM\_None), (bool useGlobalIndex\*\* = False)

\-

Change the pitch value of the channel at "index" - The value should be between -1.0 and +1.0 - use optional pitchUnit parameter to send value in semitones (pitchUnit = 1) or to change pitch range (pitchUnit = 2)  
use optional pickupMode to override FL default pickup option

8, \*13, \*\*33

getChannelType

int index, (bool useGlobalIndex\* = False)

int

Returns the type of channel, can be one of the following [values](#getChannelTypeValues)

19, \*33

isChannelSelected

int index, (bool useGlobalIndex\* = False)

int

Returns True if the channel at "index" is selected.

1, \*33

selectOneChannel

int index, (bool useGlobalIndex\* = False)

\-

Select channel at "index" exclusively.

8, \*33

selectChannel

int index, (int value = -1), (bool useGlobalIndex\* = False)

\-

Toggle the selection of the channel at "index" - to not toggle, set value to 1 (select) or 0 (deselect)

1, \*33

selectAll

\-

\-

Select all channels in the current channel group.

1

deselectAll

\-

\-

Deselect all channels in the current channel group.

1

getChannelMidiInPort

int index, (bool useGlobalIndex\* = False)

int

Returns MIDI port for channel at "index" or one of the following:  
-3 receive notes from touch keyboard  
-2 this channel will only receive notes when it's the selected channel  
-1 receive notes from typing keyboard  

1, \*33

getChannelIndex

int index

int

Returns 'indexGlobal' for channel at "index" (respecting the groups).

1

getTargetFxTrack

int index, (bool useGlobalIndex\* = False)

int

Returns target FX track for channel at "index".

1, \*33

setTargetFxTrack

int channelIndex, int mixerIndex, (bool useGlobalIndex\* = False)

\-

Routes the channel at "channelIndex" to the mixer track at "mixerIndex".

28, \*33

isHighLighted

\-

int

Returns True when red highlight rectangle is active in channel rack.

1

*Channel events:*

getRecEventId

int index, (bool useGlobalIndex\* = False)

int

Returns eventID for channel at "index".  
Use this eventID in [processRECEvent](#processRECEvent).  
Example (to get eventId for volume of first channel):  
  
` eventId = midi.REC_Chan_Vol + channels.getRecEventId(0) `

1

incEventValue

int eventId, int step, float res\*

int

Get event value increased by step. Use (optional\*) res paremeter to specify increment resolution.  
Use result as new value in [processRECEvent](#processRECEvent)  
Example (to increase volume of first channel):  
  
` step = 1`  
`eventId = midi.REC_Chan_Vol + channels.getRecEventId(0)`  
`newValue = channels.incEventValue(eventId, step)`  
`general.processRECEvent(eventId, newValue, midi.REC_UpdateValue | midi.REC_UpdateControl) `

1, \*20: res is optional, default = 1/24

processRECEvent

int eventId, int value, int flags

int

This function is deprecated here and moved to general module. More info [here](#processRECEvent)

1, 7(deprecated)

*Channel grid bits:*

isGridBitAssigned

int index, (bool useGlobalIndex\* = False)

int

Returns 1 when grid bit for channel at "index" is assigned.

30, \*33

getGridBit

int index, int position, (bool useGlobalIndex\* = False)

int

Returns grid bit at "position" for channel at "index".

1, \*33

setGridBit

int index, int position, int value, (bool useGlobalIndex\* = False)

\-

Set grid bit value at "position" for channel at "index".

1, \*33

getStepParam

int step, int [param](#stepParams), int offset, int startPos, (int padsStride = 16), (bool useGlobalIndex\* = False)

int

Get step parameter for step at "step"

1, \*33

getCurrentStepParam

int index, int step, int [param](#stepParams), (bool useGlobalIndex = False)

int

Get current step parameter for channel at "index" and for step at "step".

1

setStepParameterByIndex

int index, int patNum, int step, int [param](#stepParams), int value, (bool useGlobalIndex = False)

\-

Set current step parameter for channel at "index" and for step at "step".  
set optional useGlobalIndex to 1 to use global channel index

1

getGridBitWithLoop

int index, int position, (bool useGlobalIndex\* = False)

int

Get grid bit with loop for channel at "index".

1, \*33

showGraphEditor

bool temporary, int [param](#stepParams), int step, int index, (bool useGlobalIndex\* = False)

\-

Show graph editor for channel at "index" and for step at "step".  
set temporary to false to keep editor open

1, \*20

*Misc.*

isGraphEditorVisible

\-

bool

Returns whether the graph editor is currently visible.

showEditor

int index, (int value\* = -1), (bool useGlobalIndex\*\* = False)

\-

Show editor (plugin window) for channel at "index" - set optional 'value'\* to 1 to show or to 0 to hide editor

1, \*3, \*\*33

focusEditor

int index, (bool useGlobalIndex\* = False)

\-

Focus editor (plugin window) for channel at "index".

1, \*33

showCSForm

int index, (int state\* = 1), (bool useGlobalIndex\*\* = False)

\-

Show channel settings (or plugin window for plugins) for channel at "index" - use optional state to 0 (close), 1 (open), -1 (toggle) channel settings window

1, \*9, \*\*33

midiNoteOn

int indexGlobal, int note, int velocity, (int channel = -1)

\-

Set MIDI note for channel at "indexGlobal".

1

getActivityLevel

int index, (bool useGlobalIndex\* = False)

float

Returns activity level for channel at "index".

9, \*33

quickQuantize

int index, (int startOnly = 1), (bool useGlobalIndex\* = False)

\-

Perform quick quantize for channel at "index".

9, \*33

rerollLoopStarterLoop

int index, (bool useGlobalIndex = True)

\-

Same as clicking the dice button on Loopstarter audio loops channels.

39

### Mixer module

Mixer module allows you to control FL Studio [Mixer](https://www.image-line.com/support/flstudio_online_manual/html/mixer.htm). **NOTE:** Track number 0 is always the **Master**.

<table class="tableList" style="width:98%">
<colgroup>
<col style="width: 20%" />
<col style="width: 20%" />
<col style="width: 20%" />
<col style="width: 20%" />
<col style="width: 20%" />
</colgroup>
<thead>
<tr>
<th>Command</th>
<th>Arguments</th>
<th>Result</th>
<th>Documentation</th>
<th scope="row">Version</th>
</tr>
</thead>
<tbody>
<tr>
<td>trackNumber</td>
<td>-</td>
<td>int</td>
<td>Returns the index of the currently selected mixer track.</td>
<td>1</td>
</tr>
<tr>
<td>trackCount</td>
<td>-</td>
<td>int</td>
<td>Returns the current track count. Deprecated, use getTrackCount</td>
<td>1, 38 (deprecated)</td>
</tr>
<tr>
<td>getTrackCount</td>
<td>-</td>
<td>int</td>
<td>Returns the current track count.</td>
<td>38</td>
</tr>
<tr>
<td>getTrackInfo</td>
<td>int <a href="#TrackInfoMode">trackType</a></td>
<td>int</td>
<td>Returns track info.</td>
<td>1</td>
</tr>
<tr>
<td>setTrackNumber</td>
<td>int index, (int <a href="#CurrentTrackFlags">flags</a> = -1)</td>
<td>-</td>
<td>Sets the currently selected mixer track.</td>
<td>1</td>
</tr>
<tr>
<td>trackCount</td>
<td>-</td>
<td>int</td>
<td>Returns the number of tracks.</td>
<td>1</td>
</tr>
<tr>
<td>getTrackName</td>
<td>int index, (int maxLen = -1)</td>
<td>string</td>
<td>Returns the name of the track at index.</td>
<td>1</td>
</tr>
<tr>
<td>setTrackName</td>
<td>int index, string name</td>
<td>-</td>
<td>Changes the name of the track at index to "name".</td>
<td>1</td>
</tr>
<tr>
<td>getTrackColor</td>
<td>int index</td>
<td>int</td>
<td>Returns the color of the track at index.</td>
<td>1</td>
</tr>
<tr>
<td>setTrackColor</td>
<td>int index, int color</td>
<td>-</td>
<td>Changes the color of the track at index to "color".</td>
<td>1</td>
</tr>
<tr>
<td>getSlotColor</td>
<td>int index, int slot</td>
<td>int</td>
<td>Returns the color of the slot of the track at index as an RGBA value.</td>
<td>32</td>
</tr>
<tr>
<td>setSlotColor</td>
<td>int index, int slot, int color</td>
<td>-</td>
<td>Changes the color of the slot track at index to the value of "color".</td>
<td>32</td>
</tr>
<tr>
<td>isTrackArmed</td>
<td>int index</td>
<td>int</td>
<td>Returns True if the track at index is armed.</td>
<td>1</td>
</tr>
<tr>
<td>armTrack</td>
<td>int index</td>
<td>-</td>
<td>Toggle the armed state of the track at index.</td>
<td>1</td>
</tr>
<tr>
<td>isTrackSolo</td>
<td>int index</td>
<td>int</td>
<td>Returns True if the track at index is soloed.</td>
<td>1</td>
</tr>
<tr>
<td>soloTrack</td>
<td>int index, (int value = -1), (int <a href="#trackSoloMode">mode</a> = -1)</td>
<td>-</td>
<td>without value this function will toggle the solo state of the track at index - set optional 'value' to 1 to solo track or to 0 unsolo track<br />
</td>
<td>1</td>
</tr>
<tr>
<td>isTrackEnabled</td>
<td>int index</td>
<td>-</td>
<td>Returns True if the track at index is enabled.</td>
<td>1</td>
</tr>
<tr>
<td>isTrackAutomationEnabled</td>
<td>int index, int plugIndex</td>
<td>-</td>
<td>Returns True if the track at index has automation enabled.</td>
<td>1</td>
</tr>
<tr>
<td>enableTrack</td>
<td>int index</td>
<td>-</td>
<td>Toggle the enabled state of the track at index.</td>
<td>1</td>
</tr>
<tr>
<td>isTrackMuted</td>
<td>int index</td>
<td>-</td>
<td>Returns True if the track at index is muted.</td>
<td>2</td>
</tr>
<tr>
<td>muteTrack</td>
<td>int index, (int value* = -1)</td>
<td>-</td>
<td>Toggles the Mute status of the track at index if value is default. Otherwise mutes track if value is 1 and unmutes if value is 0.</td>
<td>2, *30</td>
</tr>
<tr>
<td>isTrackMuteLock</td>
<td>int index</td>
<td>int</td>
<td>Returns True if the Mute for track at index is locked.</td>
<td>13</td>
</tr>
<tr>
<td id="getTrackPluginId">getTrackPluginId</td>
<td>int index, int plugIndex</td>
<td>int</td>
<td>Returns plugin id of plugin with plugIndex on the track at index.</td>
<td>1</td>
</tr>
<tr>
<td>isTrackPluginValid</td>
<td>int index, int plugIndex</td>
<td>int</td>
<td>Returns True if plugin with plugIndex on the track at index. is valid</td>
<td>1</td>
</tr>
<tr>
<td>getTrackVolume</td>
<td>int index, (int mode* = 0)</td>
<td>float</td>
<td>Returns the normalized volume (between 0 and 1.0) of the track at index - set optional mode to 1 to get volume in dB</td>
<td>1, *14</td>
</tr>
<tr>
<td>setTrackVolume</td>
<td>int index, float volume, (int <a href="#pickupModes">pickupMode</a>* = PIM_None)</td>
<td>-</td>
<td>Changes the volume of the track at index - volume is value between 0 and 1.0<br />
use optional pickupMode to override FL default pickup option</td>
<td>1, 13(pickup)</td>
</tr>
<tr>
<td>getTrackPan</td>
<td>int index</td>
<td>float</td>
<td>Returns the pan value (between -1.0 and 1.0) for the track at index.</td>
<td>1</td>
</tr>
<tr>
<td>setTrackPan</td>
<td>int index, float pan, (int <a href="#pickupModes">pickupMode</a>* = PIM_None)</td>
<td>-</td>
<td>Changes the panning for the track at index.<br />
pan value is between -1.0 and 1.0 - use optional pickupMode to override FL default pickup option</td>
<td>1, 13(pickup)</td>
</tr>
<tr>
<td>getTrackStereoSep</td>
<td>int index</td>
<td>float</td>
<td>Returns the stereo separation value (between -1.0 and 1.0) for the track at index - set optional 'pickup' to 1 to use pickup function, or to 2 to follow FL global pickup setting</td>
<td>12, 13(pickup)</td>
</tr>
<tr>
<td>setTrackStereoSep</td>
<td>int index, float sep, (int pickupMode = 0)</td>
<td>-</td>
<td>Changes the stereo separation for the track at index.<br />
sep value is between -1.0 and 1.0.</td>
<td>12</td>
</tr>
<tr>
<td>getPluginMixLevel</td>
<td>int index, int plugIndex</td>
<td>float</td>
<td>Returns value of mix level for plugin at plugIndex on mixer track at index.</td>
<td>37</td>
</tr>
<tr>
<td>setPluginMixLevel</td>
<td>int index, int plugIndex, value float, (int <a href="#pickupModes">pickupMode</a>* = PIM_None)</td>
<td>-</td>
<td>Set value for mix level for plugin at plugIndex on mixer track at index.</td>
<td>37</td>
</tr>
<tr>
<td>isTrackSelected</td>
<td>int index</td>
<td>int</td>
<td>Returns True if the track at index is selected.</td>
<td>1</td>
</tr>
<tr>
<td>selectTrack</td>
<td>int index</td>
<td>-</td>
<td>Toggle selection of the track at index.</td>
<td>1</td>
</tr>
<tr>
<td>setActiveTrack</td>
<td>int index</td>
<td>-</td>
<td>Exclusively select the track at index.</td>
<td>27</td>
</tr>
<tr>
<td>selectAll</td>
<td>-</td>
<td>-</td>
<td>Select all mixer tracks.</td>
<td>1</td>
</tr>
<tr>
<td>deselectAll</td>
<td>-</td>
<td>-</td>
<td>Deselect all mixer tracks.</td>
<td>1</td>
</tr>
<tr>
<td>setRouteTo</td>
<td>int index, int destIndex, int value, (bool updateUI* = False)</td>
<td>-</td>
<td>Set route for track at index to "destIndex". Set optional updateUI to true to update mixer UI (same as afterRoutingChanged)</td>
<td>1, *36</td>
</tr>
<tr>
<td>setRouteToLevel</td>
<td>int index, int destIndex, float level</td>
<td>-</td>
<td>Set routeTo level, level is normalized value</td>
<td>36</td>
</tr>
<tr>
<td>getRouteToLevel</td>
<td>int index, int destIndex</td>
<td>float</td>
<td>Get routeTo levelas normalized value</td>
<td>36</td>
</tr>
<tr>
<td>getRouteSendActive</td>
<td>int index, int destIndex</td>
<td>int</td>
<td>Returns True if route sends from track at index to "destIndex" is active.</td>
<td>1</td>
</tr>
<tr>
<td>afterRoutingChanged</td>
<td>-</td>
<td>-</td>
<td>Notify FL about routing changes.</td>
<td>1</td>
</tr>
<tr>
<td>getEventValue</td>
<td>int index, (int value = MaxInt), (int smoothTarget = 1)</td>
<td>int</td>
<td>Returns event value from MIDI.</td>
<td>1</td>
</tr>
<tr>
<td>remoteFindEventValue</td>
<td>int index, (int flags = 0)</td>
<td>float</td>
<td>Returns event value.</td>
<td>1</td>
</tr>
<tr>
<td>getEventIDName</td>
<td>int index, (int shortName = 0)</td>
<td>str</td>
<td>Returns event name (set shortName to True for short name).</td>
<td>1</td>
</tr>
<tr>
<td>getEventIDValueString</td>
<td>int index, int value</td>
<td>string</td>
<td>Returns event value as string.</td>
<td>1</td>
</tr>
<tr>
<td>getAutoSmoothEventValue</td>
<td>int index, (int locked = 1)</td>
<td>int</td>
<td>Returns auto smooth event value.</td>
<td>1</td>
</tr>
<tr>
<td>automateEvent</td>
<td>int index, int value, int <a href="#RecEventFlags">flags</a>, (int speed = 0), (int <a href="#IsIncrementFlags">isIncrement</a> = 0), (float res = EKRes)</td>
<td>int</td>
<td>Automate event</td>
<td>1</td>
</tr>
<tr>
<td>getTrackPeaks</td>
<td>int index, int <a href="#TrackPeakMode">mode</a></td>
<td>float</td>
<td>Returns peaks for track at "index"<br />
returned value is between 0 (silence) and 1 (0db) or &lt; 1 (clipping)</td>
<td>1</td>
</tr>
<tr>
<td>getTrackRecordingFileName</td>
<td>int index</td>
<td>string</td>
<td>Returns recording file name for track at "index"</td>
<td>1</td>
</tr>
<tr>
<td>linkTrackToChannel</td>
<td>int mode</td>
<td>-</td>
<td>Link track to channel<br />
"mode" can be one of the: ROUTE_ToThis = 0, ROUTE_StartingFromThis = 1</td>
<td>1</td>
</tr>
<tr>
<td>linkChannelToTrack</td>
<td>int channel, int track, (int select = 0)</td>
<td>-</td>
<td>Link channel to track<br />
"channel" is channel index respecting groups, set optional 'select' to 1 to make track selected</td>
<td>23</td>
</tr>
<tr>
<td>getSongStepPos</td>
<td>-</td>
<td>int</td>
<td>Returns song step position.</td>
<td>1</td>
</tr>
<tr>
<td>getCurrentTempo</td>
<td>(int asInt = 0)</td>
<td>int/float</td>
<td>Returns current tempo - set optional "asInt" to True to get result as int</td>
<td>1</td>
</tr>
<tr>
<td>getRecPPS</td>
<td>-</td>
<td>int</td>
<td>Returns recording pps.</td>
<td>1</td>
</tr>
<tr>
<td>getSongTickPos</td>
<td>(int <a href="#SongTickPosFlags">mode</a> = ST_Int)</td>
<td>int/float</td>
<td>Returns song ticks pos.</td>
<td>1</td>
</tr>
<tr>
<td>getLastPeakVol</td>
<td>int audioChannel</td>
<td>float</td>
<td>Returns last peak volume. Set audioChannel to 0 for left volume or to 1 for right volume.</td>
<td>9</td>
</tr>
<tr>
<td>getTrackDockSide</td>
<td>int index</td>
<td>int</td>
<td>Returns dock side of the mixer track (index). (0 = left, 1 = center, 2 = right)<br />
listen to <a href="#OnRefreshEvent">OnRefresh</a> event (HW_Dirty_Mixer_Controls) flag to update on dock changes</td>
<td>13</td>
</tr>
<tr>
<td>isTrackSlotsEnabled</td>
<td>int index</td>
<td>int</td>
<td>Returns state of mixer track (index) 'Enable effect slots' option.</td>
<td>19</td>
</tr>
<tr>
<td>enableTrackSlots</td>
<td>int index, (int value = -1)</td>
<td>int</td>
<td>Toggle mixer track (index) 'Enable effect slots' option. (value: -1 = toggle, 0 = disable, 1 = enable)</td>
<td>19</td>
</tr>
<tr>
<td>isTrackRevPolarity</td>
<td>int index</td>
<td>int</td>
<td>Returns state of mixer track (index) 'reverse polarity' option.</td>
<td>19</td>
</tr>
<tr>
<td>revTrackPolarity</td>
<td>int index, (int value = -1)</td>
<td>int</td>
<td>Toggle mixer track (index) 'reverse polarity' option. (value: -1 = toggle, 0 = disable, 1 = enable)</td>
<td>19</td>
</tr>
<tr>
<td>isTrackSwapChannels</td>
<td>int index</td>
<td>int</td>
<td>Returns state of mixer track (index) 'swap l/r channels' option.</td>
<td>19</td>
</tr>
<tr>
<td>swapTrackChannels</td>
<td>int index, (int value = -1)</td>
<td>int</td>
<td>Toggle mixer track (index) 'swap l/r channels' option. (value: -1 = toggle, 0 = disable, 1 = enable)</td>
<td>19</td>
</tr>
<tr>
<td>focusEditor</td>
<td>int index, int plugIndex</td>
<td>-</td>
<td>Focus editor (plugin window) for plugIndex on the track at "index".</td>
<td>25</td>
</tr>
<tr>
<td>getActiveEffectIndex</td>
<td>-</td>
<td>tuple[int index, int plugIndex] | None</td>
<td>Returns tracks index and pluIndex for focused effect editor or none of no effect editor is focused.</td>
<td>25</td>
</tr>
<tr>
<td>getEqBandCount</td>
<td>-</td>
<td>int</td>
<td>Returns number of Eq bands</td>
<td>35</td>
</tr>
<tr>
<td>getEqGain</td>
<td>int index, int band, (int mode)</td>
<td>float</td>
<td>Returns Eq gain for band in track (index) as normalized value. Set optional mode to 1 to get value in Db.</td>
<td>35</td>
</tr>
<tr>
<td>setEqGain</td>
<td>int index, int band, float value</td>
<td>-</td>
<td>Set Eq gain for band in track (index) as normalized value.</td>
<td>35</td>
</tr>
<tr>
<td>getEqFrequency</td>
<td>int index, int band, (int mode)</td>
<td>float</td>
<td>Returns Eq frequency for band in track (index) as normalized value. Set optional mode to 1 to get value in Hz.</td>
<td>35</td>
</tr>
<tr>
<td>setEqFrequency</td>
<td>int index, int band, float value</td>
<td>-</td>
<td>Set Eq frequency for band in track (index) as normalized value.</td>
<td>35</td>
</tr>
<tr>
<td>getEqBandwidth</td>
<td>int index, int band</td>
<td>float</td>
<td>Returns Eq bandwidth for band in track (index) as normalized value.</td>
<td>35</td>
</tr>
<tr>
<td>setEqBandwidth</td>
<td>int index, int band, float value</td>
<td>-</td>
<td>Set Eq bandwidth for band in track (index) as normalized value.</td>
<td>35</td>
</tr>
</tbody>
</table>

### Patterns module

Patterns module allows you to control FL Studio [Playlist Patterns](https://www.image-line.com/support/flstudio_online_manual/html/playlist_patterns.htm)

<table class="tableList" style="width:98%">
<colgroup>
<col style="width: 20%" />
<col style="width: 20%" />
<col style="width: 20%" />
<col style="width: 20%" />
<col style="width: 20%" />
</colgroup>
<thead>
<tr>
<th>Command</th>
<th>Arguments</th>
<th>Result</th>
<th>Documentation</th>
<th scope="row">Version</th>
</tr>
</thead>
<tbody>
<tr>
<td>patternNumber</td>
<td>-</td>
<td>int</td>
<td>Returns the current pattern number.</td>
<td>1</td>
</tr>
<tr>
<td>patternCount</td>
<td>-</td>
<td>int</td>
<td>Returns the number of patterns.</td>
<td>1</td>
</tr>
<tr>
<td>patternMax</td>
<td>-</td>
<td>int</td>
<td>Returns the maximum pattern number.</td>
<td>1</td>
</tr>
<tr>
<td>getPatternName</td>
<td>int index</td>
<td>string</td>
<td>Returns the name of the pattern at "index".</td>
<td>1</td>
</tr>
<tr>
<td>setPatternName</td>
<td>int index, string name</td>
<td>-</td>
<td>Changes the name of the pattern at "index" to "name".</td>
<td>1</td>
</tr>
<tr>
<td>getPatternColor</td>
<td>int index</td>
<td>int</td>
<td>Returns the color of the pattern at "index".</td>
<td>1</td>
</tr>
<tr>
<td>setPatternColor</td>
<td>int index, int color</td>
<td>-</td>
<td>Changes the color of the pattern at "index" to "color".</td>
<td>1</td>
</tr>
<tr>
<td>getPatternLength</td>
<td>int index</td>
<td>int</td>
<td>Returns the length of the pattern at "index", in beats.</td>
<td>1</td>
</tr>
<tr>
<td>getBlockSetStatus</td>
<td>int left, int top, int right, int bottom</td>
<td>int</td>
<td>Returns the status of the live block - Result is one of the LB_Status_Simplest option <a href="#getLiveBlockStatusModeSimplest">constants</a></td>
<td>1</td>
</tr>
<tr>
<td>ensureValidNoteRecord</td>
<td>int index, (int playNow = 0)</td>
<td>-</td>
<td>Ensure valid note of the pattern at "index".</td>
<td>1</td>
</tr>
<tr>
<td>jumpToPattern</td>
<td>int index</td>
<td>-</td>
<td>Jum to the pattern at "index"</td>
<td>1</td>
</tr>
<tr>
<td>findFirstNextEmptyPat</td>
<td>int <a href="#findFirstNextEmptyPat">flags</a>, (int x = -1), (int y = -1)</td>
<td>-</td>
<td>Find first empty pattern at position x, y</td>
<td>1</td>
</tr>
<tr>
<td colspan="5"></td>
</tr>
<tr>
<td colspan="5"><em>Picker panel functions:</em></td>
</tr>
<tr>
<td>isPatternSelected</td>
<td>int index</td>
<td>int</td>
<td>Returns True if patterns at "index" is selected in Picker panel.</td>
<td>2</td>
</tr>
<tr>
<td>isPatternDefault</td>
<td>int index</td>
<td>int</td>
<td>Returns True if patterns at "index" is default (empty and unchanged by user).</td>
<td>23</td>
</tr>
<tr>
<td>selectPattern</td>
<td>int index, (int value = -1), (int preview = 0)</td>
<td>-</td>
<td>Select pattern at "index" in Picker panel - value: -1 (toggle), 0 (deselect) 1 (select)<br />
preview: set to 1 to preview pattern</td>
<td>2</td>
</tr>
<tr>
<td>clonePattern</td>
<td>(int index = -1)</td>
<td>-</td>
<td>Clone selected pattern(s), or clone panel specified by index (optional)</td>
<td>25</td>
</tr>
<tr>
<td>movePattern</td>
<td>(int direction = 1)</td>
<td>-</td>
<td>Move selected pattern(s) up (1) or down(-1)</td>
<td>39</td>
</tr>
<tr>
<td>selectAll</td>
<td>-</td>
<td>-</td>
<td>Select all patterns in Picker panel.</td>
<td>2</td>
</tr>
<tr>
<td>deselectAll</td>
<td>-</td>
<td>-</td>
<td>Deselect all patterns in Picker panel.</td>
<td>2</td>
</tr>
<tr>
<td>burnLoop</td>
<td>int index, (int storeUndo = 1), (int updateUi = 1)</td>
<td>-</td>
<td>Returns activity level for channel at "index" - Set Optional storeUndo to 0 to not store undo step. Set Optional updateUi to 0 to not update ui.</td>
<td>9</td>
</tr>
<tr>
<td colspan="5"></td>
</tr>
<tr>
<td colspan="5"><em>Pattern groups:</em></td>
</tr>
<tr>
<td>getActivePatternGroup</td>
<td></td>
<td>int</td>
<td>Returns the index of the currently selected pattern group.<br />
The default "All patterns" grouping has index -1. User-defined pattern groups have indexes starting from 0.</td>
<td>28</td>
</tr>
<tr>
<td>getPatternGroupCount</td>
<td></td>
<td>int</td>
<td>Returns the number of user-defined pattern groups.<br />
The default "All patterns" grouping is not included.</td>
<td>28</td>
</tr>
<tr>
<td>getPatternGroupName</td>
<td>index int</td>
<td>str</td>
<td>Returns the name of the pattern group at index.<br />
The default "All patterns" group's name cannot be accessed.</td>
<td>28</td>
</tr>
<tr>
<td>getPatternsInGroup</td>
<td>int</td>
<td>tuple[int, ...]</td>
<td>Returns a tuple containing all the patterns in the group at index.<br />
The default "All patterns" group returns a tuple containing all the patterns that haven't been added to any other groups.</td>
<td>28</td>
</tr>
</tbody>
</table>

### Arrangement module

Arrangement module allows you to control FL Studio [Playlist Arrangements](https://www.image-line.com/support/flstudio_online_manual/html/playlist.htm#arrangements)

| Command | Arguments | Result | Documentation | Version |
|----|----|----|----|----|
| jumpToMarker | int delta, int select | \- | Select a marker - set "delta" to -1, to select the previous marker or to +1 to select the next marker - set "select" to True to select marker as well. | 1 |
| getMarkerName | int index | string | Returns the name of the requested marker - If the marker doesn't exist, an empty string is returned. | 1 |
| addAutoTimeMarker | int time, string name | \- | Add an automatic time marker at "time" with its name set to "name" | 1 |
| liveSelection | int time, int stop | \- | Set a live selection point at "time" - set "stop" to True, to use end point of the selection (instead of start). | 1 |
| liveSelectionStart | \- | int | Returns the start time of the current live selection. | 1 |
| currentTime | int snap | int | Returns the current time in the current arrangement - set "snap" to True, to get returned value snapped to the grid. | 1 |
| currentTimeHint | int mode, int time, (int setRecPPB = ), (int isLength = 0) | string | Returns a hint string for the requested "time" in the current arrangement - "mode" is 0 for pattern mode and 1 for song mode. | 1 |
| selectionStart | \- | int | Returns the start time of the current selection in the current arrangement. | 1 |
| selectionEnd | \- | int | Returns the end time of the current selection in the current arrangement. | 1 |

### User interface module

Unless otherwise specified, these functions returns how the request was [handled](#globalTransportFlags).

<table class="tableList" style="width:98%">
<colgroup>
<col style="width: 20%" />
<col style="width: 20%" />
<col style="width: 20%" />
<col style="width: 20%" />
<col style="width: 20%" />
</colgroup>
<thead>
<tr>
<th>Command</th>
<th>Arguments</th>
<th>Result</th>
<th>Documentation</th>
<th scope="row">Version</th>
</tr>
</thead>
<tbody>
<tr>
<td>jog</td>
<td>int value</td>
<td>int</td>
<td>Generic jog control. Can be used to select stuff. "value" is an increment.</td>
<td>1</td>
</tr>
<tr>
<td>jog2</td>
<td>int value</td>
<td>int</td>
<td>Alternate jog control. Can be used to relocate stuff. "value" is an increment.</td>
<td>1</td>
</tr>
<tr>
<td>strip</td>
<td>int value</td>
<td>int</td>
<td>Touch-sensitive strip. "value" is -midi.FromMIDI_Max (left most) to midi.FromMIDI_Max (right most).</td>
<td>1</td>
</tr>
<tr>
<td>stripJog</td>
<td>int value</td>
<td>int</td>
<td>Touch-sensitive strip in jog mode. "value" is an increment.</td>
<td>1</td>
</tr>
<tr>
<td>stripHold</td>
<td>int value</td>
<td>int</td>
<td>Touch-sensitive strip in hold mode - "value" is 0 for release, 1 and 2 for 1 or 2 fingers centered mode, -1 and -2 for 1 or 2 fingers jog mode.</td>
<td>1</td>
</tr>
<tr>
<td>previous</td>
<td>-</td>
<td>int</td>
<td>Generic previous control - in mixer: select previous mixer track<br />
in channel rack: select previous channel<br />
in browser: scroll to previous item<br />
in plugin: select previous preset*</td>
<td>1, *9</td>
</tr>
<tr>
<td>next</td>
<td>-</td>
<td>int</td>
<td>Generic next control - in mixer: select next mixer track<br />
in channel rack: select next channel<br />
in browser: scroll to next item<br />
in plugin: select next preset*</td>
<td>1, *9</td>
</tr>
<tr>
<td>moveJog</td>
<td>int value</td>
<td>int</td>
<td>Used to relocate items. "value" is an increment.</td>
<td>1</td>
</tr>
<tr>
<td>up</td>
<td>(int value* = 1)</td>
<td>int</td>
<td>Generic way to move up.</td>
<td>1, *4</td>
</tr>
<tr>
<td>down</td>
<td>(int value* = 1)</td>
<td>int</td>
<td>Generic way to move down.</td>
<td>1, *4</td>
</tr>
<tr>
<td>left</td>
<td>(int value* = 1)</td>
<td>int</td>
<td>Generic way to move left.</td>
<td>1, *4</td>
</tr>
<tr>
<td>right</td>
<td>(int value* = 1)</td>
<td>int</td>
<td>Generic way to move right.</td>
<td>1, *4</td>
</tr>
<tr>
<td>horZoom</td>
<td>int value</td>
<td>int</td>
<td>Zoom horizontally by the increment "value".</td>
<td>1</td>
</tr>
<tr>
<td>verZoom</td>
<td>int value</td>
<td>int</td>
<td>Zoom vertically by the increment "value".</td>
<td>1</td>
</tr>
<tr>
<td>snapOnOff</td>
<td>-</td>
<td>int</td>
<td>Toggle the snap value.</td>
<td>1</td>
</tr>
<tr>
<td>cut</td>
<td>-</td>
<td>int</td>
<td>Cut what is selected, if possible.</td>
<td>1</td>
</tr>
<tr>
<td>copy</td>
<td>-</td>
<td>int</td>
<td>Copy what is selected, if possible.</td>
<td>1</td>
</tr>
<tr>
<td>paste</td>
<td>-</td>
<td>int</td>
<td>Paste previously copied data, if possible.</td>
<td>1</td>
</tr>
<tr>
<td>insert</td>
<td>-</td>
<td>int</td>
<td>Press the insert key.</td>
<td>1</td>
</tr>
<tr>
<td>delete</td>
<td>-</td>
<td>int</td>
<td>Press the delete key.</td>
<td>1</td>
</tr>
<tr>
<td>enter</td>
<td>-</td>
<td>int</td>
<td>Press the enter key.</td>
<td>1</td>
</tr>
<tr>
<td>escape</td>
<td>-</td>
<td>int</td>
<td>Press the escape key.</td>
<td>1</td>
</tr>
<tr>
<td>yes</td>
<td>-</td>
<td>int</td>
<td>Press the 'Y' key.</td>
<td>1</td>
</tr>
<tr>
<td>no</td>
<td>-</td>
<td>int</td>
<td>Press the 'N' key.</td>
<td>1</td>
</tr>
<tr>
<td colspan="5"></td>
</tr>
<tr>
<td colspan="5"><em>FL Studio Hints:</em></td>
</tr>
<tr>
<td>getHintMsg</td>
<td>-</td>
<td>string</td>
<td>Returns program hint message</td>
<td>1</td>
</tr>
<tr>
<td>setHintMsg</td>
<td>string msg</td>
<td>-</td>
<td>Set program hint message</td>
<td>1</td>
</tr>
<tr>
<td>getHintValue</td>
<td>int value, int max</td>
<td>string</td>
<td>Returns hint for value</td>
<td>1</td>
</tr>
<tr>
<td>getTimeDispMin</td>
<td>-</td>
<td>int</td>
<td>Returns True when time display is set to 'minutes'</td>
<td>1</td>
</tr>
<tr>
<td>setTimeDispMin</td>
<td>-</td>
<td>-</td>
<td>Set time display to minutes</td>
<td>1</td>
</tr>
<tr>
<td colspan="5"></td>
</tr>
<tr>
<td colspan="5"><em>Window handling:</em></td>
</tr>
<tr>
<td>getVisible</td>
<td>int <a href="#FLWindowConstants">index</a></td>
<td>int</td>
<td>Returns visible state (0 or 1) of window specified by <a href="#FLWindowConstants">index</a></td>
<td>1</td>
</tr>
<tr>
<td>showWindow</td>
<td>int <a href="#FLWindowConstants">index</a></td>
<td>-</td>
<td>Show window specified by <a href="#FLWindowConstants">index</a></td>
<td>1</td>
</tr>
<tr>
<td>hideWindow</td>
<td>int <a href="#FLWindowConstants">index</a></td>
<td>-</td>
<td>Hide window specified by <a href="#FLWindowConstants">index</a></td>
<td>5</td>
</tr>
<tr>
<td>getFocused</td>
<td>int <a href="#FLWindowConstants">index</a></td>
<td>int</td>
<td>Returns focused state (0 or 1) of window specified by <a href="#FLWindowConstants">index</a></td>
<td>1</td>
</tr>
<tr>
<td>setFocused</td>
<td>int <a href="#FLWindowConstants">index</a></td>
<td>-</td>
<td>Set focused state (0 or 1) of window specified by <a href="#FLWindowConstants">index</a></td>
<td>2</td>
</tr>
<tr>
<td>getFocusedFormCaption</td>
<td>-</td>
<td>string</td>
<td>Returns caption of focused window</td>
<td>1</td>
</tr>
<tr>
<td>getFocusedFormID</td>
<td>-</td>
<td>int</td>
<td>Returns ID of focused window. This ID is:<br />
- <a href="#FLWindowConstants">FL Window constant</a> when Channel rack, Browser, Mixer, Playlist or Piano Roll is focused..<br />
- channel index for Generator plugins or -1 fopr invalid plugin<br />
- effect plugin id: (track &lt;&lt; 6 + index) &lt;&lt; 16</td>
<td>13</td>
</tr>
<tr>
<td>getFocusedPluginName</td>
<td>-</td>
<td>string</td>
<td>Returns Original Plugin Name of focused window</td>
<td>5</td>
</tr>
<tr>
<td>scrollWindow</td>
<td>int <a href="#FLWindowConstants">index</a>, int value, (directionFlag* = 0)</td>
<td>-</td>
<td>Scroll window specified by <a href="#FLWindowConstants">index</a><br />
value is track number(mixer), channel number(channel rack), playlist track(playlist) or channel step(channel rack), playlist bar(playlist) when directionFlag is set to 1</td>
<td>13, *15</td>
</tr>
<tr>
<td>nextWindow</td>
<td>-</td>
<td>int</td>
<td>Focus the next window.</td>
<td>1</td>
</tr>
<tr>
<td>selectWindow</td>
<td>int shift</td>
<td>int</td>
<td>Press the TAB key - set "shift" to True, to make it act as if Shift + TAB is pressed.</td>
<td>1</td>
</tr>
<tr>
<td>launchAudioEditor</td>
<td>int reuse, string filename, int index, string preset, string presetGUID</td>
<td>int</td>
<td>Launch audio editor for track at "index" and returns editor state<br />
set "reuse" to True to reuse opened audio editor (if any)<br />
"filename" is path to audio file<br />
</td>
<td>1</td>
</tr>
<tr>
<td>openEventEditor</td>
<td>int eventId, int <a href="#openEventEditorMode">mode</a>, (int newWindow = 0)</td>
<td>int</td>
<td>Launch event editor for "eventId"<br />
example: openEventEditor(channels.getRecEventId(0) + midi.REC_Chan_PianoRoll, midi.EE_PR) to open piano roll for channel 0</td>
<td>9</td>
</tr>
<tr>
<td colspan="5"></td>
</tr>
<tr>
<td colspan="5"><em>Menu handling:</em></td>
</tr>
<tr>
<td>isInPopupMenu</td>
<td>-</td>
<td>int</td>
<td>Returns True when application popup menu is active</td>
<td>1</td>
</tr>
<tr>
<td>closeActivePopupMenu</td>
<td>-</td>
<td>-</td>
<td>Close active popup menu</td>
<td>1</td>
</tr>
<tr>
<td colspan="5"></td>
</tr>
<tr>
<td colspan="5"><em>Helpers:</em></td>
</tr>
<tr>
<td>isClosing</td>
<td>-</td>
<td>int</td>
<td>Returns True if application is closing</td>
<td>1</td>
</tr>
<tr>
<td>isMetronomeEnabled</td>
<td>-</td>
<td>int</td>
<td>Returns True when metronome is enabled.</td>
<td>1</td>
</tr>
<tr>
<td>isStartOnInputEnabled</td>
<td>-</td>
<td>int</td>
<td>Returns True when start on input is enabled.</td>
<td>1</td>
</tr>
<tr>
<td>isPrecountEnabled</td>
<td>-</td>
<td>int</td>
<td>Returns True when precount is enabled.</td>
<td>1</td>
</tr>
<tr>
<td>isLoopRecEnabled</td>
<td>-</td>
<td>int</td>
<td>Returns True when loop recording is enabled.</td>
<td>1</td>
</tr>
<tr>
<td>getSnapMode</td>
<td>-</td>
<td>int <a href="#snapModeConstants">snapMode</a></td>
<td>Returns snap mode.</td>
<td>1</td>
</tr>
<tr>
<td>setSnapMode</td>
<td>int <a href="#snapModeConstants">snapMode</a></td>
<td>-</td>
<td>Set snap mode.</td>
<td>24</td>
</tr>
<tr>
<td>snapMode</td>
<td>int value</td>
<td>int</td>
<td>Select another snap mode - "value" is an increment: -1 (previous), 1 (next) mode.</td>
<td>1</td>
</tr>
<tr>
<td>getStepEditMode</td>
<td>-</td>
<td>bool</td>
<td>Returns the state of the "step edit mode" control</td>
<td>28</td>
</tr>
<tr>
<td>setStepEditMode</td>
<td>newValue: bool</td>
<td>-</td>
<td>Sets the state of the "step edit mode" control</td>
<td>28</td>
</tr>
<tr>
<td>getProgTitle</td>
<td>-</td>
<td>string</td>
<td>Returns program title</td>
<td>1</td>
</tr>
<tr>
<td>getVersion</td>
<td>(int mode* = 4)</td>
<td>string / int</td>
<td>Returns program version string (or number)<br />
optional mode parameter can be one of the following: VER_Major = 0; VER_Minor = 1; VER_Release = 2; VER_Build = 3; VER_VersionAndEdition = 4; VER_FullVersionAndEdition = 5; VER_ArchAndBuild = 6 **</td>
<td>1, *7, **13</td>
</tr>
<tr>
<td>crDisplayRect</td>
<td>int left, int top, int right, int bottom, int duration, (int <a href="#crDisplayRectFlags">flags</a>* = 0)</td>
<td>-</td>
<td>Display channel rack selection rectangle - by default selection works on channel rack steps, see <a href="#crDisplayRectFlags">flags</a> for additional options<br />
set 'duration' in ms, or use duration = midi.MaxInt to set rectangle 'on' and duration = 0 (**) to set rectangle 'off'</td>
<td>1, *14, **16</td>
</tr>
<tr>
<td>miDisplayRect</td>
<td>int start, int end, int duration, (int <a href="#crDisplayRectFlags">flags</a>** = 0)</td>
<td>-</td>
<td>Display mixer selection rectangle - define "start" and "end" track number, use 0 for Master track, 126 for Current track<br />
set 'duration' in ms, or use duration = midi.MaxInt to set rectangle 'on' and duration = 0 (*) to set rectangle 'off'</td>
<td>13, *16, **17</td>
</tr>
<tr>
<td>miDisplayDockRect</td>
<td>int start, int numTrack, int dock, int duration</td>
<td>-</td>
<td>Display selection rectangle in mixer dock- define "start" and "numTrack" track number<br />
set dock to 0 for left dock, or to 1 for right dock<br />
set 'duration' in ms, or use duration = midi.MaxInt to set rectangle 'on' and duration = 0 (*) to set rectangle 'off'</td>
<td>17</td>
</tr>
<tr>
<td colspan="5"><em>Browser handling:</em></td>
</tr>
<tr>
<td>navigateBrowser</td>
<td>int direction, int shiftHeld*</td>
<td>string</td>
<td>Navigate browser nodes or browser menu (right click menu for active node)<br />
set direction to one of the FPT_Up, FPT_Down, FPT_Left, FPT_Right constants<br />
set shiftHeld to 1 to expand/open browser node<br />
function returns caption of active node</td>
<td>22, *31</td>
</tr>
<tr>
<td>toggleBrowserNode</td>
<td>(int value = -1)</td>
<td>-</td>
<td>Toggle whether browser node is expandend.<br />
Set optional value to 1(expand) or to 0(collapse) node.</td>
<td>34</td>
</tr>
<tr>
<td>navigateBrowserTabs</td>
<td>int direction</td>
<td>string</td>
<td>Navigate browser tabs<br />
set direction to one of the FPT_Left, FPT_Right constants<br />
function returns name of the newly selected tab</td>
<td>22</td>
</tr>
<tr>
<td>selectBrowserMenuItem</td>
<td>-</td>
<td>-</td>
<td>Select browser menu item (navigated by navigateBrowser)</td>
<td>1</td>
</tr>
<tr>
<td>previewBrowserMenuItem</td>
<td>-</td>
<td>-</td>
<td>Start preview of active browser node</td>
<td>1</td>
</tr>
<tr>
<td>getFocusedNodeFileType</td>
<td>-</td>
<td>int</td>
<td>Return <a href="#BrowserFileTypes">type</a> for active node or -1 when no node is active</td>
<td>1</td>
</tr>
<tr>
<td>getFocusedNodeCaption</td>
<td>-</td>
<td>string</td>
<td>Return caption for active node or empty string when no node is active</td>
<td>1</td>
</tr>
<tr>
<td>isBrowserAutoHide</td>
<td>-</td>
<td>int</td>
<td>Return 1 when browser auto-hide option is enabled</td>
<td>1</td>
</tr>
<tr>
<td>setBrowserAutoHide</td>
<td>int autoHide</td>
<td>-</td>
<td>Set autoHide to 1 to enable browser auto-hide option</td>
<td>1</td>
</tr>
</tbody>
</table>

### Transport module

This module handles FL Studio Transport (Play, Stop, Pause & Record)

<table class="tableList" style="width:98%">
<colgroup>
<col style="width: 20%" />
<col style="width: 20%" />
<col style="width: 20%" />
<col style="width: 20%" />
<col style="width: 20%" />
</colgroup>
<thead>
<tr>
<th>Command</th>
<th>Arguments</th>
<th>Result</th>
<th>Documentation</th>
<th scope="row">Version</th>
</tr>
</thead>
<tbody>
<tr>
<td>globalTransport</td>
<td>int <a href="#globalTransportCommands">command</a>, int value, (int <a href="#pmeFlags">pmeflags</a> = PME_System), (int <a href="#globalTransportFlags">flags</a> = GT_ALL)</td>
<td>int</td>
<td>Call the GlobalTransport function with the appropriate parameters - Use this function inside one of the <a href="#eventType">eventData</a> script <a href="#script_events">events</a> and pass eventData.pmeflags as "pmeflags" parameter<br />
</td>
<td>1</td>
</tr>
<tr>
<td>start</td>
<td>-</td>
<td>-</td>
<td>Start playback.</td>
<td>1</td>
</tr>
<tr>
<td>stop</td>
<td>-</td>
<td>-</td>
<td>Stop playback.</td>
<td>1</td>
</tr>
<tr>
<td>record</td>
<td>-</td>
<td>-</td>
<td>Toggle recording.</td>
<td>1</td>
</tr>
<tr>
<td>isRecording</td>
<td>-</td>
<td>int</td>
<td>Returns True when recording is active.</td>
<td>1</td>
</tr>
<tr>
<td>getLoopMode</td>
<td>-</td>
<td>int</td>
<td>Returns the current looping mode (pattern = 0, song = 1).</td>
<td>1</td>
</tr>
<tr>
<td>setLoopMode</td>
<td>-</td>
<td>-</td>
<td>Toggle loop mode.</td>
<td>1</td>
</tr>
<tr>
<td>getSongPos</td>
<td>(int <a href="#getSongLengthMode">mode</a>* = -1)</td>
<td>float</td>
<td>Returns the song position as a normalized value (0..1) - or in specified format when mode* is set</td>
<td>1, *3</td>
</tr>
<tr>
<td>setSongPos</td>
<td>float position, (int <a href="#getSongLengthMode">mode</a>* = -1)</td>
<td>-</td>
<td>Set the song position - "position" is a normalized value (0..1) - or in specified format when mode* is set</td>
<td>1, *4</td>
</tr>
<tr>
<td>getSongLength</td>
<td>int <a href="#getSongLengthMode">mode</a></td>
<td>int</td>
<td>Get the song length.</td>
<td>3</td>
</tr>
<tr>
<td>getSongPosHint</td>
<td>-</td>
<td>string</td>
<td>Returns a hint for the current song position.</td>
<td>1</td>
</tr>
<tr>
<td>isPlaying</td>
<td>-</td>
<td>int</td>
<td>Returns True if the program is playing.</td>
<td>1</td>
</tr>
<tr>
<td>markerJumpJog</td>
<td>int value, (int <a href="#globalTransportFlags">flags</a> = GT_All)</td>
<td>-</td>
<td>Jump to a marker position - "value" is an increment.</td>
<td>1</td>
</tr>
<tr>
<td>markerSelJog</td>
<td>int value, (int <a href="#globalTransportFlags">flags</a> = GT_All)</td>
<td>-</td>
<td>Select a marker - "value" is an increment.</td>
<td>1</td>
</tr>
<tr>
<td>getHWBeatLEDState</td>
<td>-</td>
<td>int</td>
<td>Returns the state of the hardware LED beat indicator.</td>
<td>1</td>
</tr>
<tr>
<td colspan="5"></td>
</tr>
<tr>
<td colspan="5" id="playbackSpeedControl"><em>Playback speed control:</em></td>
</tr>
<tr>
<td>rewind</td>
<td>int <a href="#startStopConst">startStop</a>, (int <a href="#globalTransportFlags">flags</a> = GT_All)</td>
<td>-</td>
<td>Rewind the song position - Each call to this function with startStop = SS_Start, must be stopped with startStop = SS_Stop</td>
<td>1</td>
</tr>
<tr>
<td>fastForward</td>
<td>int speed</td>
<td>-</td>
<td>Forward the song position</td>
<td>1</td>
</tr>
<tr>
<td>continuousMove</td>
<td>int speed, int <a href="#startStopConst">startStop</a></td>
<td>-</td>
<td>Start Continuous move - This function do same as rewind and fastforward but you can control speed.<br />
Set speed (&gt; 0) to move forward and (&lt; 0) to move backward (speed = (1) is normal speed forward)<br />
Each call to this function with startStop = SS_Start, must be stopped with startStop = SS_Stop</td>
<td>1</td>
</tr>
<tr>
<td>continuousMovePos</td>
<td>int speed, int startStop</td>
<td>-</td>
<td>Start Continuous move - Set speed (&gt; 0) to move forward and (&lt; 0) to move backward (speed = (1) is normal speed forward).<br />
Set startStop to (2) to start and to (0) to stop</td>
<td>2</td>
</tr>
<tr>
<td>setPlaybackSpeed</td>
<td>float speedMultiplier</td>
<td>-</td>
<td>Set a playback speed multiplier - Set speedMultiplier = (1) is normal speed, set to value between (1/4 ... 1) for slower and between (1 ... 4) faster movement</td>
<td>1</td>
</tr>
</tbody>
</table>

### Device module

**Device module** will handle MIDI devices connected to the FL Studio MIDI interface. You send messages to output interface, retrieve linked control values... etc). MIDI scripts, assigned to an input interface, can be mapped (linked) to an Output interface via the Port Number. With mapped (linked) output interfaces, scripts can send midi messages to output interfaces by using one of the **midiOut\*\*\*** messages.

<table class="tableList" style="width:98%">
<colgroup>
<col style="width: 20%" />
<col style="width: 20%" />
<col style="width: 20%" />
<col style="width: 20%" />
<col style="width: 20%" />
</colgroup>
<thead>
<tr>
<th>Command</th>
<th>Arguments</th>
<th>Result</th>
<th>Documentation</th>
<th scope="row">Version</th>
</tr>
</thead>
<tbody>
<tr>
<td>isAssigned</td>
<td>-</td>
<td>int</td>
<td>Returns True if (linked) output interface is assigned.</td>
<td>1</td>
</tr>
<tr>
<td>getPortNumber</td>
<td>-</td>
<td>int</td>
<td>Returns the interface port number. (or -1 when port number is not assigned)<br />
this is same number as interface port number set in FL Studio Midi settings</td>
<td>1</td>
</tr>
<tr>
<td>getName</td>
<td>-</td>
<td>int</td>
<td>Returns the device name</td>
<td>7</td>
</tr>
<tr>
<td>midiOutMsg</td>
<td>int message</td>
<td>-</td>
<td>Send a MIDI message to the (linked) output interface - "message" holds the value to be sent, with the channel and command in the lower byte and the first and second data values in the next two bytes.</td>
<td>1</td>
</tr>
<tr>
<td>midiOutMsg</td>
<td>int midiId, int channel, int data1, int data2</td>
<td>-</td>
<td>Send a MIDI message to the (linked) output interface (alternative version with separate parameters)</td>
<td>2</td>
</tr>
<tr>
<td>midiOutNewMsg</td>
<td>int slotIndex, int message</td>
<td>-</td>
<td>Send a MIDI message to the (linked) output interface, but only if the value has changed - "slotIndex" is a value chosen by the caller, it should be the same as it was for the previous message that should be compared with - "message" holds the value to be sent.</td>
<td>1</td>
</tr>
<tr>
<td>midiOutSysex</td>
<td>string message</td>
<td>-</td>
<td>Send a SYSEX message to the (linked) output interface.</td>
<td>1</td>
</tr>
<tr>
<td>sendMsgGeneric (deprecated)</td>
<td>int64 id, string message, string lastMsg, (int offset = 0)</td>
<td>string</td>
<td>Send a text string as a SYSEX message to the (linked) output interface - "id" holds the first 6 bytes of the message (starting with 0xF0). The end value 0xF7 is added automatically - "message" is the text to send<br />
"lastMsg" is the string returned by the previous call to this function - function returns updated lastMsg</td>
<td>1</td>
</tr>
<tr>
<td>processMIDICC</td>
<td><a href="#eventType">eventData</a></td>
<td>-</td>
<td>Let FL process a CC message - use this function inside OnMidiMsg and pass (modified) eventData object as function parameter</td>
<td>1</td>
</tr>
<tr>
<td>forwardMIDICC</td>
<td>int message, (int forwardTo = 1)</td>
<td>-</td>
<td>Forward CC message to plugin - Use this function to forward midi cc messages to FL plugin(s) - Specify message as: message = status + (data1 &lt;&lt; 8) + (data2 &lt;&lt; 16) + (port &lt;&lt; 24)<br />
Message will be forwarded to active (focused) plugin - Use optional forwardTo parameter to send message to selected channel (forwardTo = 2) or to all plugins (0) - Remark: midi input port of plugin must be equal to port specified in message.</td>
<td>7</td>
</tr>
<tr>
<td>directFeedback</td>
<td><a href="#eventType">eventData</a></td>
<td>-</td>
<td>Send a received message on to the (linked) output interface - use this function inside OnMidiMsg and pass (modified) eventData object as function parameter</td>
<td>1</td>
</tr>
<tr>
<td>repeatMidiEvent</td>
<td><a href="#eventType">eventData</a>, (int delay = 300, int rate = 300)</td>
<td>-</td>
<td>Start repeatedly sending out the previously sent message - It will be sent first after "delay" milliseconds, and afterwards every "rate" milliseconds.</td>
<td>1</td>
</tr>
<tr>
<td>stopRepeatMidiEvent</td>
<td>-</td>
<td>-</td>
<td>Stop repeating the message sent with repeatMidiEvent.</td>
<td>1</td>
</tr>
<tr>
<td colspan="5"></td>
</tr>
<tr>
<td colspan="5"><em>Control events:</em></td>
</tr>
<tr>
<td>findEventID</td>
<td>int controlId, (int flags = [])</td>
<td>int</td>
<td>Returns eventID for controlId or REC_InvalidID when nothing is linked to this control<br />
"flags" can be one of the: FEID_Flags_Skip_Unsafe = 1 (skip unsafe (using formula) links)</td>
<td>1</td>
</tr>
<tr>
<td>getLinkedValue</td>
<td>int eventID</td>
<td>float</td>
<td>Returns normalized value of the linked control via eventID<br />
(to get control eventId, use findEventID function) - Result is -1 if there is no linked control.</td>
<td>1</td>
</tr>
<tr>
<td>getLinkedValueString</td>
<td>int eventID</td>
<td>string</td>
<td>Returns text value of linked control via eventID<br />
(to get control eventId, use findEventID function) - Result is ERR_PLUGINNOTVALID if there is no linked control.</td>
<td>10</td>
</tr>
<tr>
<td>getLinkedChannel</td>
<td>int eventID</td>
<td>int</td>
<td>Returns MIDI channel number for linked control via eventID<br />
(to get control eventId, use findEventID function) - Result is -1 if there is no linked control.</td>
<td>27</td>
</tr>
<tr>
<td>getLinkedParamName</td>
<td>int eventID</td>
<td>string</td>
<td>Returns parameter name of the control linked via eventID<br />
(to get control eventId, use findEventID function) - Result is ERR_PLUGINNOTVALID if there is no linked control.</td>
<td>10</td>
</tr>
<tr>
<td>getLinkedInfo</td>
<td>int eventID</td>
<td>int</td>
<td>Returns information about the linked control via eventID<br />
(to get control eventId, use findEventID function) - Result is -1 if there is no linked control, otherwise result is one or more of the <a href="#LinkedInfoResultFlags">constants</a></td>
<td>1</td>
</tr>
<tr>
<td>linkToLastTweaked</td>
<td>int controlIndex, int channel, (int globalLink, int eventID)</td>
<td>int</td>
<td>this function will create a regular (or global) controller link for the last tweaked parameter.<br />
set optional eventID to assign link to specific control instead of last tweaked control<br />
function returns (0) on success, (1) when nothing was tweaked or (2) when control is in use</td>
<td>21</td>
</tr>
<tr>
<td>getDeviceID</td>
<td></td>
<td>bytes</td>
<td>Returns the ID of the device, which is the identifying component of its response to a universal device enquiry Sysex message.<br />
Note that this does not include the Sysex header (0xF0, 0x7E, 0x01, 0x06, 0x02), or the ending byte (0xF7). Also note that for many devices, it will also contain the firmware version, meaning that you should may wish to ignore the final 4 bytes of the response.</td>
<td>25</td>
</tr>
<tr>
<td colspan="5"></td>
</tr>
<tr>
<td colspan="5"><em>Refresh thread:</em></td>
</tr>
<tr>
<td>createRefreshThread</td>
<td>-</td>
<td>-</td>
<td>Start a threaded refresh of the entire MIDI device.</td>
<td>1</td>
</tr>
<tr>
<td>destroyRefreshThread</td>
<td>-</td>
<td>-</td>
<td>Stop a previously started threaded refresh.</td>
<td>1</td>
</tr>
<tr>
<td>fullRefresh</td>
<td>-</td>
<td>-</td>
<td>Trigger a previously started threaded refresh - If there is none, the refresh is triggered immediately.</td>
<td>1</td>
</tr>
<tr>
<td colspan="5"></td>
</tr>
<tr>
<td colspan="5"><em>Helpers:</em></td>
</tr>
<tr>
<td>isDoubleClick</td>
<td>int index</td>
<td>int</td>
<td>Returns True if the function was called with the same index shortly before, indicating a float click.</td>
<td>1</td>
</tr>
<tr>
<td>setHasMeters</td>
<td>-</td>
<td>-</td>
<td>use this in OnInit event to tell FL Studio device use peak meters</td>
<td>1</td>
</tr>
<tr>
<td>baseTrackSelect</td>
<td>int index, int step</td>
<td>-</td>
<td>Base track selection (for control surfaces). Set step to MaxInt for reset.</td>
<td>1</td>
</tr>
<tr>
<td>hardwareRefreshMixerTrack</td>
<td>int index</td>
<td>-</td>
<td>Let FL Studio dispatch OnDirtyMixerTrack event to all midi devices. Use index = -1 for all tracks</td>
<td>1</td>
</tr>
<tr>
<td colspan="5"></td>
</tr>
<tr>
<td colspan="5"><em>Dispatching between devices:</em></td>
</tr>
<tr>
<td>dispatch</td>
<td>int ctrlIndex, int message, (bytes sysex)</td>
<td>-</td>
<td>Dispatch midi message (or sysex) to controller specified by ctrlIndex - receiver (script) must define sender(s) inside script: # receiveFrom="Sender name"</td>
<td>1</td>
</tr>
<tr>
<td>dispatchReceiverCount</td>
<td>-</td>
<td>int</td>
<td>Returns number of available receivers.</td>
<td>1</td>
</tr>
<tr>
<td>dispatchGetReceiverPortNumber</td>
<td>int ctrlIndex</td>
<td>int</td>
<td>Returns port number of receiver specified by ctrlIndex.</td>
<td>5</td>
</tr>
<tr>
<td>setMasterSync</td>
<td>int value</td>
<td>-</td>
<td>Toggle (value = 1 to enable, 0 to disable) send master synch for current device</td>
<td>18</td>
</tr>
<tr>
<td>getMasterSync</td>
<td>-</td>
<td>int</td>
<td>Returns 'send master synch' state for current device (1 = enableb)</td>
<td>19</td>
</tr>
</tbody>
</table>

### Plugins module

This module handles FL Studio plugins (by their position in mixer or channel rack)  
to access generator plugins (channel rack), specify channel rack index, for effects specify mixer index and slotIndex. Set optional useGlobalIndex to true to use global channel index.

Command

Arguments

Result

Documentation

Version

isValid

int index, (int slotIndex = -1), (bool useGlobalIndex\* = False)

int

Returns true if there is valid plugin at position of index/slotindex

8, \*26

getPluginName

int index, (int slotIndex = -1), (int userName\* = 0), (bool useGlobalIndex\*\* = False)

string

Returns plugin name for plugin at position of index/slotindex - Set optional userName parameter to 1 to get user name for plugin slot instead of original plugin name (will return plugin name if user didn't change name for slot)

8, \*12, \*\*26

getParamCount

int index, (int slotIndex = -1), (bool useGlobalIndex\* = False)

int

Returns plugin parameter count for plugin at position of index/slotindex

8, \*26

getParamName

int paramIndex, int index, (int slotIndex = -1), (bool useGlobalIndex\* = False)

string

Returns plugin parameter (paramIndex) name for plugin at position of index/slotindex

8, \*26

getParamValue

int paramIndex, int index, (int slotIndex = -1), (bool useGlobalIndex\* = False)

int

Returns plugin parameter (paramIndex) value for plugin at position of index/slotindex as normalized value

8, \*26

setParamValue

float value, int paramIndex, int index, (int slotIndex = -1), (int [pickupMode](#pickupModes)\* = PIM\_None), (bool useGlobalIndex\*\* = False)

int

Sets value (normalized) for plugin parameter (paramIndex) for plugin at position of index/slotindex  
use optional pickupMode to override FL default pickup option

8, \*17, \*\*26

getParamValueString

int paramIndex, int index, (int slotIndex = -1), (bool useGlobalIndex\* = False)

string

Returns plugin parameter (paramIndex) value as string for plugin at position of index/slotindex  
this function is only supported by some of the plugins, support for more plugins will be added later

8, \*26

getColor

int index, (int slotIndex = -1), (int [flag](#getColorFlags) = GC\_BackgroundColor), (int paramIndex = 0), (bool useGlobalIndex\* = False)

int

Returns various plugin color parameter values for plugin at position of index/slotindex

12, \*26

getName

int index, (int slotIndex = -1), (int [flag](#getNameFlags) = FPN\_Param), (int paramIndex = 0), (bool useGlobalIndex\* = False)

string

Returns various plugin name parameter values for plugin at position of index/slotindex optional paramIndex depends on [flag](#getNameFlags)

13, \*26

getPadInfo

int index, (int slotIndex), (int [paramOption](#getPadInfoFlags)), (int paramIndex), (bool useGlobalIndex\* = False)

int

Returns pad parameters for plugin at position of index/slotindex use PAD\_Count as paramOption to get number of pad parameters supported by plugin

19, \*26

getPresetCount

int index, (int slotIndex = -1), (bool useGlobalIndex\* = False)

int

Returns number of presets for plugin at position of index/slotindex

15, \*26

nextPreset

int index, (int slotIndex = -1), (bool useGlobalIndex\* = False)

\-

Navigate to next preset in plugin at position of index/slotindex

10, \*26

prevPreset

int index, (int slotIndex = -1), (bool useGlobalIndex\* = False)

\-

Navigate to previous preset in plugin at position of index/slotindex

10, \*26

### General module

This module handles general FL Studio functions

<table class="tableList" style="width:98%">
<colgroup>
<col style="width: 20%" />
<col style="width: 20%" />
<col style="width: 20%" />
<col style="width: 20%" />
<col style="width: 20%" />
</colgroup>
<thead>
<tr>
<th>Command</th>
<th>Arguments</th>
<th>Result</th>
<th>Documentation</th>
<th scope="row">Version</th>
</tr>
</thead>
<tbody>
<tr>
<td>saveUndo</td>
<td>string undoName, int <a href="#saveUndoFlags">flags</a>, (int updateHistory = 1)</td>
<td>-</td>
<td>Saves undo history point (level)<br />
set optional updateHistory parameter to 0 to hide undo point in browser history</td>
<td>1</td>
</tr>
<tr>
<td id="undo">undo</td>
<td>-</td>
<td>int</td>
<td>Undo last history level<br />
this function mimic FL Studio CTRL+Z functionality: it steps forward through the history, unless you are at the latest step (in this case, undo works as the standard one step undo/redo shortcut).</td>
<td>1</td>
</tr>
<tr>
<td>undoUp</td>
<td>-</td>
<td>int</td>
<td>Move up in undo history (up one level)</td>
<td>1</td>
</tr>
<tr>
<td>undoDown</td>
<td>-</td>
<td>int</td>
<td>Move down in undo history (down one level)</td>
<td>4</td>
</tr>
<tr>
<td>undoUpDown</td>
<td>int offset</td>
<td>int</td>
<td>Move up or down in undo history by offset</td>
<td>1</td>
</tr>
<tr>
<td>restoreUndoLevel</td>
<td>int level</td>
<td>-</td>
<td>Restore to specific undo point (level)</td>
<td>1</td>
</tr>
<tr>
<td>getUndoLevelHint</td>
<td>-</td>
<td>string</td>
<td>Returns undo level hint</td>
<td>1</td>
</tr>
<tr>
<td>getUndoHistoryPos</td>
<td>-</td>
<td>int</td>
<td>Returns undo history position</td>
<td>1</td>
</tr>
<tr>
<td>getUndoHistoryCount</td>
<td>-</td>
<td>int</td>
<td>Returns undo history length</td>
<td>1</td>
</tr>
<tr>
<td>getUndoHistoryLast</td>
<td>-</td>
<td>int</td>
<td>Returns last undo history position</td>
<td>1</td>
</tr>
<tr>
<td>setUndoHistoryPos</td>
<td>int index</td>
<td>-</td>
<td>Set undo history position</td>
<td>1</td>
</tr>
<tr>
<td>setUndoHistoryCount</td>
<td>int value</td>
<td>-</td>
<td>Set undo history count</td>
<td>1</td>
</tr>
<tr>
<td>setUndoHistoryLast</td>
<td>int index</td>
<td>-</td>
<td>Set undo history last position</td>
<td>1</td>
</tr>
<tr>
<td>getRecPPB</td>
<td>-</td>
<td>int</td>
<td>Returns the current time signature value. (Timebase * Numerator)</td>
<td>1</td>
</tr>
<tr>
<td>getRecPPQ</td>
<td>-</td>
<td>int</td>
<td>Returns the current timebase (PPQ)</td>
<td>8</td>
</tr>
<tr>
<td>getUseMetronome</td>
<td>-</td>
<td>int</td>
<td>Returns True when metronome is used</td>
<td>1</td>
</tr>
<tr>
<td>getPrecount</td>
<td>-</td>
<td>int</td>
<td>Returns precount value</td>
<td>1</td>
</tr>
<tr>
<td>getChangedFlag</td>
<td>-</td>
<td>int</td>
<td>Get FL Studio project "changed' flag<br />
Result is one of the: 0 = clean, 1 = dirty, 2 = dirty but clean for autosave</td>
<td>1</td>
</tr>
<tr>
<td>getVersion</td>
<td>-</td>
<td>int</td>
<td>Returns Midi scripting API version number</td>
<td>1</td>
</tr>
<tr>
<td>restoreUndo</td>
<td>-</td>
<td>int</td>
<td>Deprecated, use <a href="#undo">undo</a></td>
<td>1</td>
</tr>
<tr>
<td id="processRECEvent">processRECEvent</td>
<td>int <a href="#RecEventParams">eventId</a>, int value, int <a href="#RecEventFlags">flags</a></td>
<td>int</td>
<td>Process recorded event for event with eventID<br />
Use this function to do various operations (specified by flags) with FL Studio recorded events, you can for example set or get event values.<br />
Function wil return event value or REC_InvalidID (for invalid eventID)</td>
<td>7</td>
</tr>
<tr>
<td>dumpScoreLog</td>
<td>int time, (int silent = 0)</td>
<td>-</td>
<td>Dump score log, specify time to dump (time), use optional (silent) flag to supress message when score is empty</td>
<td>15</td>
</tr>
<tr>
<td>clearLog</td>
<td>-</td>
<td>-</td>
<td>Clear log</td>
<td>15</td>
</tr>
<tr>
<td>safeToEdit</td>
<td>-</td>
<td>int</td>
<td>Returns 1 when safe to use setter functions</td>
<td>29</td>
</tr>
<tr>
<td>getProjectTitle</td>
<td>-</td>
<td>string</td>
<td>Returns project title</td>
<td>38</td>
</tr>
<tr>
<td>getProjectAuthor</td>
<td>-</td>
<td>string</td>
<td>Returns project author</td>
<td>38</td>
</tr>
<tr>
<td>getProjectGenre</td>
<td>-</td>
<td>string</td>
<td>Returns project genre</td>
<td>38</td>
</tr>
</tbody>
</table>

### LaunchMapPages module

Some controllers support pages (custom controller layouts), this optional module helps to handle this pages.

LaunchMapPages <a href="https://forum.image-line.com/viewtopic.php?f=1914&amp;t=92193" target="_blank">reference</a>

| Command | Arguments | Result | Documentation | Version |
|----|----|----|----|----|
| init | string [deviceName](#devicename), int width, int height | \- | Initialize launchmap pages. | 1 |
| createOverlayMap | int offColor, int onColor, int width, int height | \- | Creates overlay map. | 1 |
| length | \- | int | Returns launchmap pages length. | 1 |
| updateMap | int index | int | Updates launchmap page at "index". | 1 |
| getMapItemColor | int index, int itemIndex | int | Returns color at "itemIndex" of page at "index" | 1 |
| getMapCount | int index | int | Returns length of items of page at "index" | 1 |
| getMapItemChannel | int index, int itemIndex | int | Returns destination channel at "itemIndex" of page at "index" | 1 |
| getMapItemAftertouch | int index, int itemIndex | int | Returns aftertouch for item at "itemIndex" of page at "index" | 1 |
| processMapItem | [eventData](#eventType), int index, int itemIndex, int velocity | \- | Process map item at "itemIndex" of page at "index" | 1 |
| releaseMapItem | [eventData](#eventType), int index | \- | Release map item at "itemIndex" of page at "index" | 1 |
| checkMapForHiddenItem | \- | \- | Checks for launchpad hidden item. | 1 |
| setMapItemTarget | int index, int itemIndex, int target | int | Set target for item at "itemIndex" of page at "index". | 1 |

## Types

#### eventData

| Parameter             | Type        | Documentation                        |
|-----------------------|-------------|--------------------------------------|
| handled               | bool (r/w)  | set to True to stop event propagtion |
| timestamp             | time (r)    | timestamp of event                   |
| status                | int (r/w)   | MIDI status                          |
| data1                 | int (r/w)   | MIDI data1                           |
| data2                 | int (r/w)   | MIDI data2                           |
| port                  | int (r)     | MIDI port                            |
| note                  | int (r/w)   | MIDI note number                     |
| velocity              | int (r/w)   | MIDI velocity                        |
| pressure              | int (r/w)   | MIDI pressure                        |
| progNum               | int (r)     | MIDI program number                  |
| controlNum            | int (r)     | MIDI control number                  |
| controlVal            | int (r)     | MIDI control value                   |
| pitchBend             | int (r)     | MIDI pitch bend value                |
| sysex                 | bytes (r/w) | MIDI sysex data                      |
| isIncrement           | bool (r/w)  | MIDI is increament state             |
| res                   | float (r/w) | MIDI res                             |
| inEv                  | int (r/w)   | Original MIDI event value            |
| outEv                 | int (r/w)   | MIDI event output value              |
| midiId                | int (r/w)   | MIDI midiID                          |
| midiChan              | int (r/w)   | MIDI midiChan (0 based)              |
| midiChanEx            | int (r/w)   | MIDI midiChanEx                      |
| [pmeflags](#pmeFlags) | int (r)     | MIDI [pmeflags](#pmeFlags)           |

## Constants

All constants below are defined in module 'midi'. Include the MIDI module at the top of the script with 'import':

- **import *midi***

#### OnProjectLoad status

| Parameter     | Value | Documentation                                        |
|---------------|-------|------------------------------------------------------|
| PL\_Start     | 0     | Called when project loading start                    |
| PL\_LoadOk    | 100   | Called when project was succesfully loaded           |
| PL\_LoadError | 101   | Called when project loading stopped because of error |

#### OnDirtyChannel flags

| Parameter   | Value | Documentation             |
|-------------|-------|---------------------------|
| CE\_New     | 0     | new channel is added      |
| CE\_Delete  | 1     | channel deleted           |
| CE\_Replace | 2     | channel replaced          |
| CE\_Rename  | 3     | channel renamed           |
| CE\_Select  | 4     | channel selection changed |

#### OnRefresh flags

<table class="tableList">
<colgroup>
<col style="width: 33%" />
<col style="width: 33%" />
<col style="width: 33%" />
</colgroup>
<thead>
<tr>
<th>Parameter</th>
<th>Value</th>
<th>Documentation</th>
</tr>
</thead>
<tbody>
<tr>
<td>HW_Dirty_Mixer_Sel</td>
<td>1</td>
<td>mixer selection changed</td>
</tr>
<tr>
<td>HW_Dirty_Mixer_Display</td>
<td>2</td>
<td>mixer display changed</td>
</tr>
<tr>
<td>HW_Dirty_Mixer_Controls</td>
<td>4</td>
<td>mixer controls changed</td>
</tr>
<tr>
<td>HW_Dirty_RemoteLinks</td>
<td>16</td>
<td>remote links (linked controls) has been added/removed</td>
</tr>
<tr>
<td>HW_Dirty_FocusedWindow</td>
<td>32</td>
<td>channel selection changed</td>
</tr>
<tr>
<td>HW_Dirty_Performance</td>
<td>64</td>
<td>performance layout changed</td>
</tr>
<tr>
<td>HW_Dirty_LEDs</td>
<td>256</td>
<td>various changes in FL which require update of controller leds<br />
update status leds (play/stop/record/active window/.....) on this flag</td>
</tr>
<tr>
<td>HW_Dirty_RemoteLinkValues</td>
<td>512</td>
<td>remote link (linked controls) value is changed</td>
</tr>
<tr>
<td>HW_Dirty_Patterns</td>
<td>1024</td>
<td>pattern changes</td>
</tr>
<tr>
<td>HW_Dirty_Tracks</td>
<td>2048</td>
<td>track changes</td>
</tr>
<tr>
<td>HW_Dirty_ControlValues</td>
<td>4096</td>
<td>plugin cotrol value changes</td>
</tr>
<tr>
<td>HW_Dirty_Colors</td>
<td>8192</td>
<td>plugin colors changes</td>
</tr>
<tr>
<td>HW_Dirty_Names</td>
<td>16384</td>
<td>plugin names changes</td>
</tr>
<tr>
<td>HW_Dirty_ChannelRackGroup</td>
<td>32768</td>
<td>Channel rack group changes</td>
</tr>
<tr>
<td>HW_ChannelEvent</td>
<td>65536</td>
<td>channel changes</td>
</tr>
</tbody>
</table>

#### Live status mode

| Parameter | Value | Documentation |
|----|----|----|
| LB\_Status\_Default | 0 (Default) | Result will be one or more of: any filled = 1, any scheduled = 2, any playing = 4 |
| LB\_Status\_Simple | 1 | Result will be one of the: empty = 0, filled = 1, none playing (or scheduled) = 2, none scheduled (and not playing) = 3 |

#### Live block status mode

| Parameter | Value | Documentation |
|----|----|----|
| LB\_Status\_Default | 0 (Default) | Result will be one or more of: filled = 1, scheduled = 2, playing = 4 |
| LB\_Status\_Simple | 1 | Result will be one of the: empty = 0, filled = 1, playing (or scheduled) = 2, scheduled (and not playing) = 3 |
| LB\_Status\_Simplest | 2 | Result will be one of the: empty = 0, filled = 1, playing or scheduled = 2 |

#### Live block status flags

| Parameter             | Value | Documentation |
|-----------------------|-------|---------------|
| LB\_Status\_Filled    | 1     | Filled        |
| LB\_Status\_Scheduled | 2     | Scheduled     |
| LB\_Status\_Playing   | 4     | Playing       |

#### Track solor mode

| Parameter | Value | Documentation |
|----|----|----|
|  |  |  |
| fxSoloModeWithSourceTracks | 1 | Solo mixer track (include tracks routed to it) |
| fxSoloModeWithDestTracks | 2 | Solo mixer track (include sends) |
| fxSoloModeWithSourceTracks + fxSoloModeWithDestTracks | 3 | Solo track and all tracks routed TO and FROM it, same as Alt/Opt+Click in FL Studio |
| fxSoloModeIgnorePrevious | 4 | Solo only this track, muting all other tracks |

#### Live loop mode

| Parameter           | Value | Documentation           |
|---------------------|-------|-------------------------|
|                     |       |                         |
| LiveLoop\_Stay      | 0     | Stay                    |
| LiveLoop\_OneShot   | 1     | One shot                |
| LiveLoop\_MarchWrap | 2     | March and wrap          |
| LiveLoop\_MarchStay | 3     | March and stay          |
| LiveLoop\_MarchStop | 4     | March and stop          |
| LiveLoop\_Random    | 5     | Random                  |
| LiveLoop\_ExRandom  | 6     | Random (avoid previous) |

#### Live trigger mode

| Parameter           | Value | Documentation   |
|---------------------|-------|-----------------|
|                     |       |                 |
| LiveTrig\_Retrigger | 0     | Retrigger       |
| LiveTrig\_Hold      | 1     | Hold and stop   |
| LiveTrig\_HMotion   | 2     | Hold and motion |
| LiveTrig\_Latch     | 3     | Latch           |

#### Live Snap

| Parameter        | Value | Documentation |
|------------------|-------|---------------|
|                  |       |               |
| LiveSnap\_Off    | 0     | Off           |
| LiveSnap\_Fourth | 1     | 1/4 beat      |
| LiveSnap\_Half   | 2     | 1/2 beat      |
| LiveSnap\_One    | 3     | 1 beat        |
| LiveSnap\_Two    | 4     | 2 beats       |
| LiveSnap\_Four   | 5     | 4 beats       |
| LiveSnap\_Auto   | 6     | Auto          |

#### Channel types

| Parameter     | Value | Documentation                             |
|---------------|-------|-------------------------------------------|
|               |       |                                           |
| CT\_Sampler   | 0     | Internal sampler                          |
| CT\_Hybrid    | 1     | generator plugin feeding internal sampler |
| CT\_GenPlug   | 2     | generator plugin                          |
| CT\_Layer     | 3     | Layer                                     |
| CT\_AudioClip | 4     | Audio clip                                |
| CT\_AutoClip  | 5     | Automation clip                           |

#### Channel rack rectangle flags

| Parameter | Value | Documentation |
|----|----|----|
|  |  |  |
| CR\_HighlightChannels | 1 | when specified, crDisplayRect works on channels instead of steps |
| CR\_ScrollToView | 2 | scroll channel rack rectangle to view |
| CR\_HighlightChannelMute | 4 | when specified, crDisplayRect works on channels and highlights only mute control |
| CR\_HighlightChannelPanVol | 8 | when specified, crDisplayRect works on channels and highlights only pan and volume controls |
| CR\_HighlightChannelTrack | 16 | when specified, crDisplayRect works on channels and highlights only track control |
| CR\_HighlightChannelName | 32 | when specified, crDisplayRect works on channels and highlights only channel name button |
| CR\_HighlightChannelSelect | 64 | when specified, crDisplayRect works on channels and highlights only channel selection control |

#### Trigger live clip flags

| Parameter | Value | Documentation |
|----|----|----|
|  |  |  |
| TLC\_MuteOthers | 1 | (TODO: needs explanation) |
| TLC\_Fill | 2 | (TODO: needs explanation) |
| TLC\_Queue | 4 | Queue mode |
| TLC\_Release | 32 | (TODO: needs explanation) |
| TLC\_NoPlayCheck | 64 | (TODO: needs explanation) |
| TLC\_NoHardwareUpdate | 1073741824 | (TODO: needs explanation) |
| TLC\_SecondPass | 2147483648 | (TODO: needs explanation) |
| TLC\_ColumnMode | 128 | Scene mode |
| TLC\_WeakColumnMode | 256 | \+ Scene mode |
| TLC\_TriggerCheckColumnMode | 512 | (TODO: needs explanation) |
| TLC\_TrackSnap | 0 | Use performance mode track setting trigger snap |
| TLC\_GlobalSnap | 8 | Use FL global snap value as trigger snap |
| TLC\_NoSnap | 16 | Bypass all tigger snap |
| TLC\_SubNum\_Normal | 0 | (TODO: needs explanation) |
| TLC\_SubNum\_ClipPos | 65536 | (TODO: needs explanation) |
| TLC\_SubNum\_GroupNum | 131072 | (TODO: needs explanation) |
| TLC\_SubNum\_Read | 196608 | (TODO: needs explanation) |
| TLC\_SubNum\_Leave | 262144 | (TODO: needs explanation) |

#### REC events

| Parameter              | Value | Documentation            |
|------------------------|-------|--------------------------|
|                        |       |                          |
| REC\_Chan\_Vol         | 0     | Channel volume           |
| REC\_Chan\_Pan         | 1     | Channel pan              |
| REC\_Chan\_FCut        | 2     | Channel filter cutoff    |
| REC\_Chan\_FRes        | 3     | Channel filter resonance |
| REC\_Chan\_Pitch       | 4     | Channel pitch            |
| REC\_Chan\_FType       | 5     | Channel filter type      |
| REC\_Chan\_PortaTime   | 6     | Channel portamento time  |
| REC\_Chan\_Mute        | 7     | Channel Mute             |
| REC\_Chan\_FXTrack     | 8     | Chanel FX target         |
| REC\_Chan\_GateTime    | 9     | Channel gate time        |
| REC\_Chan\_Crossfade   | 10    | Channel crossfade        |
| REC\_Chan\_TimeOfs     | 11    | Time offset              |
| REC\_Chan\_SwingMix    | 12    | Swing mix                |
| REC\_Chan\_SmpOfs      | 13    | Sample offset            |
| REC\_Chan\_StretchTime | 14    | Time stretch time        |
| REC\_Chan\_OfsPan      | 16    | Levels adjustment pan    |
| REC\_Chan\_OfsVol      | 17    | Levels adjustment volume |
| REC\_Chan\_OfsPitch    | 18    | Levels adjustment pitch  |
| REC\_Chan\_OfsFCut     | 19    | Levels adjustment Mod X  |
| REC\_Chan\_OfsFRes     | 20    | Levels adjustment Mod Y  |

use above parameters together with channel rec event id [getRecEventId](#getRecEventId)  
for example, to change volume for channel at 'index' use:  
*midi.REC\_Chan\_Vol + channels.getRecEventId(index)*

| Parameter            | Value     | Documentation           |
|----------------------|-----------|-------------------------|
|                      |           |                         |
| REC\_Mixer\_Vol      | 536879040 | Mixer volume            |
| REC\_Mixer\_Pan      | 536879041 | Mixer pan               |
| REC\_Mixer\_SS       | 536879042 | Mixer stereo separation |
| REC\_Mixer\_EQ\_Gain | 536879056 | Mixer EQ gain           |
| REC\_Mixer\_EQ\_Freq | 536879064 | Mixer freq              |
| REC\_Mixer\_EQ\_Q    | 536879072 | Mixer Q                 |
| REC\_Mixer\_EQ\_Type | 536879080 | Mixer type              |

use above parameters together with mixer track plugin id [getTrackPluginId](#getTrackPluginId)  
for example, to change volume for mixer track at 'index' use:  
*midi.REC\_Mixer\_Vol + mixer.getTrackPluginId(index, 0)*

#### REC event flags

| Parameter | Value | Documentation |
|----|----|----|
|  |  |  |
| REC\_UpdateValue | 1 | update the value |
| REC\_GetValue | 2 | retrieves the value |
| REC\_ShowHint | 4 | updates the hint (if any) |
| REC\_UpdatePlugLabel | 16 | updates the label for the plugin param |
| REC\_UpdateControl | 32 | updates the wheel/knob |
| REC\_FromMIDI | 64 | value from 0 to FromMIDI\_Max has to be translated |
| REC\_Store | 128 | store value when recording automation |
| REC\_SetChanged | 256 | set the changed flag |
| REC\_SetTouched | 512 | set as touched event |
| REC\_Init | 1024 | make sure to init the channel with the previous value before storing |
| REC\_NoLink | 2048 | don't check if wheels are linked |
| REC\_InternalCtrl | 4096 | sent by an internal controller |
| REC\_PlugReserved | 8192 | free to use by plugins |
| REC\_Smoothed | 16384 | smoothed up controller, almost same as internal controller |
| REC\_NoLastTweaked | 32768 | coming from last tweaked |
| REC\_NoSaveUndo | 65536 | used when undoing a previous change |
| REC\_InitStore | REC\_Init \| REC\_Store | combined parameter for control automation recording |
| REC\_Control | REC\_UpdateValue \| REC\_UpdateControl \| REC\_ShowHint \| REC\_InitStore \| REC\_SetChanged \| REC\_SetTouched | combined tag for changing values from midi controller |
| REC\_MIDIController | REC\_Control \| REC\_FromMIDI | combined tag for changing values from midi controller (when value needs to be translated) |

#### Step parameters

| Parameter  | Value | Documentation        |
|------------|-------|----------------------|
|            |       |                      |
| pPitch     | 0     | Note pitch           |
| pVelocity  | 1     | Velocity             |
| pRelease   | 2     | Release velocity     |
| pFinePitch | 3     | Fine pitch           |
| pPan       | 4     | Panning              |
| pModX      | 5     | Per step Mod X value |
| pModY      | 6     | Per step Mod Y value |
| pShift     | 7     | Shift                |
| pRepeat    | 8     | Shift                |

#### Global transport commnads

| Parameter | Value | Documentation |
|----|----|----|
| FPT\_Jog | 0 | (jog) generic jog (can be used to select stuff) |
| FPT\_Jog2 | 1 | (jog) alternate generic jog (can be used to relocate stuff) |
| FPT\_Strip | 2 | touch-sensitive jog strip, value will be in -midi.FromMIDI\_Max..midi.FromMIDI\_Max for leftmost..rightmost |
| FPT\_StripJog | 3 | (jog) touch-sensitive jog in jog mode |
| FPT\_StripHold | 4 | value will be 0 for release, 1,2 for 1,2 fingers centered mode, -1,-2 for 1,2 fingers jog mode (will then send FPT\_StripJog) |
| FPT\_Previous | 5 | (button) |
| FPT\_Next | 6 | (button) |
| FPT\_PreviousNext | 7 | (jog) generic track selection |
| FPT\_MoveJog | 8 | (jog) used to relocate items |
| FPT\_Play | 10 | (button) play/pause |
| FPT\_Stop | 11 | (button) |
| FPT\_Record | 12 | (button) |
| FPT\_Rewind | 13 | (hold) perform rewind, set value to SS\_Start to start, set to SS\_Stop to stop |
| FPT\_FastForward | 14 | (hold) perform move forward, set value to SS\_Start to start, set to SS\_Stop to stop |
| FPT\_Loop | 15 | (button) |
| FPT\_Mute | 16 | (button) |
| FPT\_Mode | 17 | (button) generic \| record mode |
|  |  |  |
| FPT\_Undo | 20 | (button) undo/redo last, \| undo down in history |
| FPT\_UndoUp | 21 | (button) undo up in history (no need to implement if no undo history) |
| FPT\_UndoJog | 22 | (jog) undo in history (no need to implement if no undo history) |
| FPT\_Punch | 30 | (hold) live selection |
| FPT\_PunchIn | 31 | (button) |
| FPT\_PunchOut | 32 | (button) |
| FPT\_AddMarker | 33 | (button) |
| FPT\_AddAltMarker | 34 | (button) add alternate marker |
| FPT\_MarkerJumpJog | 35 | (jog) marker jump |
| FPT\_MarkerSelJog | 36 | (jog) marker selection |
| FPT\_Up | 40 | (button) |
| FPT\_Down | 41 | (button) |
| FPT\_Left | 42 | (button) |
| FPT\_Right | 43 | (button) |
| FPT\_HZoomJog | 44 | (jog) change horizontal zoom in active window (playlist/piano roll) or increase/decrease font size (browser) |
| FPT\_VZoomJog | 45 | (jog) change vertical zoom in active window (playlist/piano roll) or increase/decrease font size (browser) |
| FPT\_Snap | 48 | (button) snap on/off |
| FPT\_SnapMode | 49 | (jog) snap mode |
| FPT\_Cut | 50 | (button) |
| FPT\_Copy | 51 | (button) |
| FPT\_Paste | 52 | (button) |
| FPT\_Insert | 53 | (button) |
| FPT\_Delete | 54 | (button) |
| FPT\_NextWindow | 58 | (button) TAB |
| FPT\_WindowJog | 59 | (jog) window selection |
| FPT\_F1 | 60 | (button) |
| FPT\_F2 | 61 | (button) Rename selected mixer track |
| FPT\_F3 | 62 | (button) |
| FPT\_F4 | 63 | (button) Next empty pattern with naming dialog |
| FPT\_F5 | 64 | (button) Toggle Playlist |
| FPT\_F6 | 65 | (button) Toggle Step Sequencer |
| FPT\_F7 | 66 | (button) Toggle Piano roll |
| FPT\_F8 | 67 | (button) Open Plugin Picker |
| FPT\_F9 | 68 | (button) Show/hide Mixer |
| FPT\_F10 | 69 | (button) Show/hide MIDI settings |
| FPT\_F11 | 70 | (button) Show/hide song info window |
| FPT\_F12 | 71 | (button) Executes the close all windows menu item |
| FPT\_Enter | 80 | (button) enter/accept |
| FPT\_Escape | 81 | (button) escape/cancel |
| FPT\_Yes | 82 | (button) yes |
| FPT\_No | 83 | (button) no |
| FPT\_Menu | 90 | (button) generic menu |
| FPT\_ItemMenu | 91 | (button) item edit/tool/contextual menu |
| FPT\_Save | 92 | (button) |
| FPT\_SaveNew | 93 | (button) save as new version |
| FPT\_PatternJog | 100 | (jog) pattern |
| FPT\_TrackJog | 101 | (jog) mixerr track |
| FPT\_ChannelJog | 102 | (jog) channel |
| FPT\_TempoJog | 105 | (jog) tempo (in 0.1BPM increments) |
| FPT\_TapTempo | 106 | (button) tempo tapping |
| FPT\_NudgeMinus | 107 | (hold) tempo nudge - |
| FPT\_NudgePlus | 108 | (hold) tempo nudge + |
| FPT\_Metronome | 110 | (button) metronome |
| FPT\_WaitForInput | 111 | (button) wait for input to start playing |
| FPT\_Overdub | 112 | (button) overdub recording |
| FPT\_LoopRecord | 113 | (button) loop recording |
| FPT\_StepEdit | 114 | (button) step edit mode |
| FPT\_CountDown | 115 | (button) countdown before recording |
| FPT\_NextMixerWindow | 120 | (button) tabs between plugin windows in the current mixer track |
| FPT\_MixerWindowJog | 121 | (jog) mixer window selection |
| FPT\_ShuffleJog | 122 | main shuffle (in increments of 1) |

#### Global transport flags

| Parameter   | Value | Documentation                        |
|-------------|-------|--------------------------------------|
| GT\_Cannot  | -1    | not handled                          |
| GT\_None    | 0     | none                                 |
| GT\_Plugin  | 1     | (handled by) Focused plugin          |
| GT\_Form    | 2     | (handled by) Focused form            |
| GT\_Menu    | 4     | (handled by) Menu                    |
| GT\_Global  | 8     | (handled) Globally                   |
| GT\_All     | 15    | All                                  |
| GT\_Delayed | 5     | Delayed handling (return value only) |

#### StartStop options

| Parameter | Value | Documentation |
|----|----|----|
| SS\_Stop | 0 | Stop movement |
| SS\_StartStep | 1 | Start movement, but only when FL Studio is in step editing mode. |
| SS\_Start | 2 | Start movement. |

#### Song length mode

| Parameter | Value | Documentation |
|----|----|----|
| SONGLENGTH\_MS | 0 | Length in ms |
| SONGLENGTH\_S | 1 | Length in s. |
| SONGLENGTH\_ABSTICKS | 2 | Length in absolute ticks |
| SONGLENGTH\_BARS | 3 | Length in BST format (bars part), not implemented in setSongPos |
| SONGLENGTH\_STEPS | 4 | Length in BST format (steps part), not implemented in setSongPos |
| SONGLENGTH\_TICKS | 5 | Length in BST format (ticks part), not implemented in setSongPos |

#### PME flags

| Parameter | Value | Documentation |
|----|----|----|
| PME\_System | 2 | Can do system stuff (play/pause.. mostly safe things) |
| PME\_System\_Safe | 4 | Can do critical system stuff (add markers.. things that can't be done when a modal window is shown) |
| PME\_PreviewNote | 8 | note trigger previews notes \| controls stuff |
| PME\_FromHost | 16 | when the app is hosted |
| PME\_FromMIDI | 32 | coming from MIDI event |

#### Current track flags

| Parameter                 | Value | Documentation              |
|---------------------------|-------|----------------------------|
| curfxScrollToMakeVisible  | 1     | Scroll to visible track    |
| curfxCancelSmoothing      | 2     | Cancel smooting            |
| curfxNoDeselectAll        | 4     | \[todo\] needs explanation |
| curfxMinimalLatencyUpdate | 8     | \[todo\] needs explanation |

#### Track type

| Parameter    | Value | Documentation |
|--------------|-------|---------------|
| TN\_Master   | 0     | Master        |
| TN\_FirstIns | 1     | First insert  |
| TN\_LastIns  | 2     | Last insert   |
| TN\_Sel      | 3     | Selected      |

#### IsIncrement flags

| Parameter     | Value | Documentation |
|---------------|-------|---------------|
| II\_Absolute  | 0     | Absolute      |
| II\_Increment | 1     | Increement    |
| II\_Switch    | 2     | Switch        |

#### Open event editor modes

| Parameter | Value | Documentation     |
|-----------|-------|-------------------|
| EE\_EE    | 0     | Controller editor |
| EE\_PR    | 1     | Piano Roll        |
| EE\_PL    | 2     | Playlist          |

#### Track peaks mode

| Parameter | Value | Documentation |
|----|----|----|
| PEAK\_L | 0 | Current peak for the left channel |
| PEAK\_R | 1 | Current peak for the right channel |
| PEAK\_LR | 2 | Current maximum peak of the peaks from left and right channel |
| PEAK\_L\_INV | 0 | Current peak for the left channel (inverted) |
| PEAK\_R\_INV | 1 | Current peak for the right channel (inverted) |
| PEAK\_LR\_INV | 3 | Current maximum peak of the peaks from left and right channel (inverted) |

#### Song tick modes

| Parameter | Value | Documentation             |
|-----------|-------|---------------------------|
| ST\_Int   | 0     | (TODO: needs explanation) |
| ST\_Beat  | 1     | Beat                      |
| ST\_PGB   | 2     | (TODO: needs explanation) |

#### Pickup Follow modes

| Parameter         | Value | Documentation                          |
|-------------------|-------|----------------------------------------|
| PIM\_None         | 0     | do not use pickup                      |
| PIM\_AlwaysPickup | 1     | always use pickup                      |
| PIM\_FollowGlobal | 2     | follow FL Studio global pickup setting |

#### Get linked info result flags

| Parameter              | Value | Documentation             |
|------------------------|-------|---------------------------|
| Event\_CantInterpolate | 1     | (TODO: needs explanation) |
| Event\_Float           | 2     | (TODO: needs explanation) |
| Event\_Centered        | 4     | (TODO: needs explanation) |

#### Find next empty pattern flags

| Parameter             | Value | Documentation             |
|-----------------------|-------|---------------------------|
| FFNEP\_FindFirst      | 0     | Find first pattern        |
| FFNEP\_DontPromptName | 2     | Don't prompt pattern name |

#### Get Color flags

| Parameter | Value | Documentation |
|----|----|----|
| GC\_BackgroundColor | 0 | Retrieves the darkest background color of the GUI |
| GC\_Semitone | 1 | Retrieves semitone color (Currently implemented in FPC to get pads color) |

#### GetPadName parameter options

| Parameter     | Value | Documentation                                         |
|---------------|-------|-------------------------------------------------------|
| PAD\_Count    | 0     | Retrieve number of pad parameters supported by plugin |
| PAD\_Semitone | 1     | Retrieve semitone for pad specified by padIndex       |
| PAD\_Color    | 2     | Retrieve color for pad specified by padIndex          |

#### Get Name flags (not all parameters works in all plugins)

<table class="tableList">
<colgroup>
<col style="width: 33%" />
<col style="width: 33%" />
<col style="width: 33%" />
</colgroup>
<thead>
<tr>
<th>Parameter</th>
<th>Value</th>
<th>Documentation</th>
</tr>
</thead>
<tbody>
<tr>
<td>FPN_Param</td>
<td>0</td>
<td>Retrieve name of plugin parameter (defined by paramIndex)</td>
</tr>
<tr>
<td>FPN_ParamValue</td>
<td>1</td>
<td>Retrieve text value of plugin parameter (defined by paramIndex)</td>
</tr>
<tr>
<td>FPN_Semitone</td>
<td>2</td>
<td>Retrieve name of note defined by plugin (by paramIndex)</td>
</tr>
<tr>
<td>FPN_Patch</td>
<td>3</td>
<td>Retrieve name of patch defined by plugin (by paramIndex)</td>
</tr>
<tr>
<td>FPN_VoiceLevel</td>
<td>4</td>
<td>Retrieve name of per-voice parameter defined by plugin (by paramIndex)</td>
</tr>
<tr>
<td>FPN_VoiceLevelHint</td>
<td>5</td>
<td>Retrieve (longer) name of per-voice parameter defined by plugin (by paramIndex)</td>
</tr>
<tr>
<td>FPN_Preset</td>
<td>6</td>
<td>For plugins that support internal presets (mainly for the wrapper plugin), retrieve the name for preset at paramIndex<br />
leave paramIndex parameter empty or use midi.GPN_GetCurrentPreset to get current preset name</td>
</tr>
<tr>
<td>FPN_OutCtrl</td>
<td>7</td>
<td>for plugins that output controllers, retrieve the name of output controller paramIndex</td>
</tr>
<tr>
<td>FPN_VoiceColor</td>
<td>8</td>
<td>retrieve name of per-voice color (MIDI channel) (by paramIndex)</td>
</tr>
<tr>
<td>FPN_OutVoice</td>
<td>9</td>
<td>for plugins that output voices, retrieve the name of output voice (by paramIndex)</td>
</tr>
</tbody>
</table>

#### Save undo flags

| Parameter     | Value | Documentation             |
|---------------|-------|---------------------------|
| UF\_None      | 0     |                           |
| UF\_EE        | 1     | Event editor              |
| UF\_PR        | 2     | Piano roll                |
| UF\_PL        | 4     | Playlist                  |
| UF\_EEPR      | 3     | Event editor + piano roll |
| UF\_KNOB      | 32    | Automated control         |
| UF\_AudioRec  | 256   | Audio recording           |
| UF\_AutoClip  | 512   | Automation clip           |
| UF\_PRMarker  | 1024  | Pattern marker            |
| UF\_PLMarker  | 2048  | Playlist marker           |
| UF\_Plugin    | 4096  | Plugin                    |
| UF\_SSLooping | 8192  | Step Sequencer looping    |
| UF\_Reset     | 65536 | Reset undo history        |

#### Snap mode constants

| Parameter        | Value | Documentation       |
|------------------|-------|---------------------|
| Snap\_Line       | 0     | Snap to line        |
| Snap\_Cell       | 1     | Snap to cell        |
| Snap\_None       | 3     | no snap             |
| Snap\_SixthStep  | 4     | Snap to sixth step  |
| Snap\_FourthStep | 5     | Snap to fourth step |
| Snap\_ThirdStep  | 6     | Snap to third step  |
| Snap\_HalfStep   | 7     | Snap to half step   |
| Snap\_Step       | 8     | Snap to step        |
| Snap\_SixthBeat  | 9     | Snap to sixth beat  |
| Snap\_FourthBeat | 10    | Snap to fourth beat |
| Snap\_ThirdBeat  | 11    | Snap to third beat  |
| Snap\_HalfBeat   | 12    | Snap to half beat   |
| Snap\_Beat       | 13    | Snap to beat        |
| Snap\_Bar        | 14    | Snap to bar         |

#### FL window constants

| Parameter | Value | Documentation |
|----|----|----|
| widMixer | 0 | Mixer |
| widChannelRack | 1 | Channel rack |
| widPlaylist | 2 | Playlist |
| widPianoRoll | 3 | Piano roll |
| widBrowser | 4 | Browser |
| widPlugin | 5 | Plugin window (only available inside getFocused function) |
| widPluginEffect | 6 | Effect Plugin window (only available inside getFocused/setFocused/getFocusedFormID functions) |
| widPluginGenerator | 7 | Generator Plugin window (only available inside getFocused/setFocused/getFocusedFormID functions) |

#### FL Browser node types

| Parameter         | Value | Documentation          |
|-------------------|-------|------------------------|
| SBN\_FLP          | 1     | FL studio project      |
| SBN\_ZIP          | 2     | Zipped archive         |
| SBN\_FLM          | 3     | FL studio project      |
| SBN\_FST          | 4     | FL Studio state preset |
| SBN\_DS           | 5     | Ds file                |
| SBN\_SS           | 6     | SS file                |
| SBN\_WAV          | 7     | Wav file               |
| SBN\_XI           | 8     | XI file                |
| SBN\_FPR          | 9     | Fpr file               |
| SBN\_FSC          | 10    | FSC file               |
| SBN\_SF2          | 11    | SF2 file               |
| SBN\_Speech       | 12    | Speech file            |
| SBN\_MP3          | 13    | MP3 file               |
| SBN\_OGG          | 14    | Ogg file               |
| SBN\_FLAC         | 15    | Flac file              |
| SBN\_OSM          | 16    | OSM file               |
| SBN\_REX          | 17    | REX file               |
| SBN\_DWP          | 18    | DirectWave preset      |
| SBN\_FNV          | 19    | FNV file               |
| SBN\_FXB          | 20    | FXB file               |
| SBN\_AIFF         | 21    | AIFF file              |
| SBN\_TXT          | 22    | Text file              |
| SBN\_BMP          | 23    | Image                  |
| SBN\_WV           | 24    | WV file                |
| SBN\_TS           | 25    | TS file                |
| SBN\_RBS          | 26    | RBS file               |
| SBN\_MID          | 27    | Midi file              |
| SBN\_FLEXPack     | 28    | Flex pack              |
| SBN\_NEWS         | 29    | News item              |
| SBN\_SHOP         | 30    | Shop item(unused)      |
| SBN\_LIB          | 31    | Library item           |
| SBN\_LIBOWNED     | 32    | Library item(owned)    |
| SBN\_NOTIFICATION | 33    | Notification item      |
| SBN\_DOWNLOAD     | 34    | Download item          |
| SBN\_M4A          | 35    | M4A file               |
| SBN\_INSTR        | 36    | INSTR file             |
| SBN\_REDIRECT     | 37    | Redirect item          |
