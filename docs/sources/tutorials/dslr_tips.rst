DSLR first configuration
^^^^^^^^^^^^^^^^^^^^^^^^

- Disable "auto-sleep" or "auto-off" to prevent errors while running pibooth.
- Disable Wifi feature to solve gphoto2 troubles to detect hardware.
- Disable the autofocus to avoid gphoto2 troubles to take a picture.
- Put a SD card on the camera (the captures will be kept also on the camera side)

DSLR settings
^^^^^^^^^^^^^

Most common settings for DSLR::

    Shutter speed: 1/60
    Focal Opening: F10
    ISO: 3200

    Shutter speed: 1/125
    Focal Opening: F8
    ISO: 3200

Credits goes to https://fotomax.fr/canon-camera-settings-with-a-magic-mirror-photobooth/, alternative settings are also available, mainly depending on natural light conditions.

DSLR Troubleshooting
^^^^^^^^^^^^^^^^^^^^

If the DLSR don't manage to take the photo Pibooth will show the "Oops something went wrong" screen. Most of the issues that our users encountered are either linked to:

- Not enough light (or no light at all when the lens cap has not been removed)
- Camera didn't manage to focus (that's why we advise to disable the autofocus and manually set it at the beginning)
- No SD card in the camera (as all the captures are downloaded in the processing stage)