## Config Format
```
{
    "sources": [
        {
            "api": "",
            "name": ""
        },
        {
            "api": "",
            "name": ""
        }
    ]
}
```

## Source Format
The api field can be one of the following, and dictates how the value of the name field is interpreted:
- `ffmpeg`: the name field will be treated as the filename of an mp4 file in the data repo
- `gstreamer` or `gstreamer-pipeline`: name is a complete gstreamer pipeline (make sure to include an appsink if you want it to display)
- `gstreamer-display`: name is the port (i.e. 5600) which a gstreamer pipeline will be set up to read and display on the GUI
- `gstreamer-record`: name is the port (i.e. 5600) which a gstreamer pipeline will be set up to read, display on the GUI, and record to an flv file in recordings