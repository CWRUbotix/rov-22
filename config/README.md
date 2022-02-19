
# pipeline_templates.json
## General Format
```
{
    "template-name": [
        "items",
        "to be",
        "concatenated"
    ],
    "template-name2": [
        "etc"
    ]
}
```

## Fields
The concatenated items will be strung together in order to create a string that will be used as a gstreamer pipeline. Each item may be one of the following:
- A string literal: this will just be pasted in verbatim
- `python.new_recording`: this will be replaced with the path of a new recording file based on the current timestamp
- `json.content`: this will be replaced with the value of the ```content``` field in the regular config file using this template

## Template List
Add new template docs here as you make them.
- `gstreamer-record`: ```content``` is the port of an input stream, to be both displayed and recorded
- `gstreamer-display`: ```content``` is the port of an input stream, to be displayed only

# Regular Config Files
## General Format
```
{
    "sources": [
        {
            "api": "CAP_GSTREAMER",
            "template": "gstreamer-display",
            "content": "5600"
        },
        {
            "api": "CAP_GSTREAMER",
            "content": "some gstreamer pipeline here"
        }
    ]
}
```

## Fields
- `api`: can be any valid OpenCV2 Video Capture API
- `template`: optional or one of the following; it dictates how the ```content``` field is interpreted:
	- `file` (the string literal "file"): ```content``` is treated as a filename to be read with the specified ```api```
    - Not included or unrecognized value: ```content``` is pasted in verbatim as a pipeline
    - Template key defined in pipeline_templates.json: ```content``` is processed as specified in the template