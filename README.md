# metrixplusplus-kiviat
Kiviat Graph Plugin for Metrix++

Clone or download as a zip and extract onto your local machine

Export this path as METRIXPLUSPLUS_PATH environment variable so that metrix++
can locate this plugin for use.

## Running the Plugin
Once you have collected the data on the codebase, it is possible to use this 
plugin to create a graphical representation of the data to get a high level
picture of the overall status.

To do so run the following command:
```
metrix++ kiviat --graph-dir"<directory to save the graph image>" <directory of codebase scanned>