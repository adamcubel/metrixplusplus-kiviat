# metrixplusplus-kiviat
Kiviat Graph Plugin for Metrix++

Clone or download as a zip and extract onto your local machine

Export this path as METRIXPLUSPLUS_PATH environment variable so that metrix++
can locate this plugin for use.

## Running the Plugin
Use the metrix++ collect command to collect data from the metrics listed below
to be able to generate the chart:
* std.code.lines.total
* std.code.lines.comments
* std.code.member.methods
* std.code.complexity.cyclomatic
* std.code.complexity.maxindent

I am still working on a way to generate the value for 'Avg Statements/Method'. For now this value on the plot defaults to zero.

Once you have collected the data on the codebase, it is possible to use this 
plugin to create a graphical representation of the data to get a high level
picture of the overall status.

To do so run the following command:
```
metrix++ kiviat --graph-dir"<directory to save the graph image>" <directory of codebase scanned>