# music-player
## A simple music player using python and vlc

### Requirements
- Python 3.8 or higher
- [VLC Media Player](https://www.videolan.org/) installed on your system

### Troubleshooting
When creating this app, i ran into the following errors (can only be seen from terminal output but will slowdown startup times by 3-5 seconds):
```bash
[000002b64bb7dd80] main libvlc error: stale plugins cache: modified C:\Program Files\VideoLAN\VLC\plugins\access\libaccess_concat_plugin.dll
[000002b64bb7dd80] main libvlc error: stale plugins cache: modified C:\Program Files\VideoLAN\VLC\plugins\access\libaccess_imem_plugin.dll
[000002b64bb7dd80] main libvlc error: stale plugins cache: modified C:\Program Files\VideoLAN\VLC\plugins\access\libaccess_mms_plugin.dll
[000002b64bb7dd80] main libvlc error: stale plugins cache: modified C:\Program Files\VideoLAN\VLC\plugins\access\libaccess_realrtsp_plugin.dll
[000002b64bb7dd80] main libvlc error: stale plugins cache: modified C:\Program Files\VideoLAN\VLC\plugins\access\libaccess_srt_plugin.dll
[000002b64bb7dd80] main libvlc error: stale plugins cache: modified C:\Program Files\VideoLAN\VLC\plugins\access\libaccess_wasapi_plugin.dll
[000002b64bb7dd80] main libvlc error: stale plugins cache: modified C:\Program Files\VideoLAN\VLC\plugins\access\libattachment_plugin.dll
[000002b64bb7dd80] main libvlc error: stale plugins cache: modified C:\Program Files\VideoLAN\VLC\plugins\access\libcdda_plugin.dll
[000002b64bb7dd80] main libvlc error: stale plugins cache: modified C:\Program Files\VideoLAN\VLC\plugins\access\libdcp_plugin.dll
[000002b64bb7dd80] main libvlc error: stale plugins cache: modified C:\Program Files\VideoLAN\VLC\plugins\access\libdshow_plugin.dll
[000002b64bb7dd80] main libvlc error: stale plugins cache: modified C:\Program Files\VideoLAN\VLC\plugins\access\libdtv_plugin.dll
[000002b64bb7dd80] main libvlc error: stale plugins cache: modified C:\Program Files\VideoLAN\VLC\plugins\access\libdvdnav_plugin.dll
[000002b64bb7dd80] main libvlc error: stale plugins cache: modified C:\Program Files\VideoLAN\VLC\plugins\access\libdvdread_plugin.dll
[000002b64bb7dd80] main libvlc error: stale plugins cache: modified C:\Program Files\VideoLAN\VLC\plugins\access\libfilesystem_plugin.dll
[000002b64bb7dd80] main libvlc error: stale plugins cache: modified C:\Program Files\VideoLAN\VLC\plugins\access\libftp_plugin.dll
[000002b64bb7dd80] main libvlc error: stale plugins cache: modified C:\Program Files\VideoLAN\VLC\plugins\access\libhttps_plugin.dll
[000002b64bb7dd80] main libvlc error: stale plugins cache: modified C:\Program Files\VideoLAN\VLC\plugins\access\libhttp_plugin.dll
[000002b64bb7dd80] main libvlc error: stale plugins cache: modified C:\Program Files\VideoLAN\VLC\plugins\access\libidummy_plugin.dll
[000002b64bb7dd80] main libvlc error: stale plugins cache: modified C:\Program Files\VideoLAN\VLC\plugins\access\libimem_plugin.dll
[000002b64bb7dd80] main libvlc error: stale plugins cache: modified C:\Program Files\VideoLAN\VLC\plugins\access\liblibbluray_plugin.dll
[000002b64bb7dd80] main libvlc error: stale plugins cache: modified C:\Program Files\VideoLAN\VLC\plugins\access\liblive555_plugin.dll
[000002b64bb7dd80] main libvlc error: stale plugins cache: modified C:\Program Files\VideoLAN\VLC\plugins\access\libnfs_plugin.dll
...
```

So the way i found to fix this was to run the following command in a admin terminal:
```bash
"C:\Program Files\VideoLAN\VLC\vlc-cache-gen.exe" "C:\Program Files\VideoLAN\VLC\plugins"
```
> https://stackoverflow.com/questions/68246840/how-to-avoid-main-libvlc-error-when-using-the-python-vlc-package
