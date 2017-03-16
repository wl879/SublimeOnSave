# OnSave plugin for Sublime Text 3

Executes commands on file save. 

## Installation

* If you have **Package Control** installed, simply search for **On Save** to install.

  ​

* Clone source code to **Sublime Text packages folder**.

  ```sh
  git clone https://github.com/wl879/SublimeOnSave.git OnSave
  ```



## Usage

Create a "**.onsave**" file in you project dir, Or **right click** folder at side bar


```yaml
# This is a example whih typescript configuration

VAR: 
	# defind typescript path
	tsc: "/usr/local/bin/tsc"
	# specify ECMAScript target version
    target: --target ES5
ENV:
	PATH: /usr/bin/
# optional 
CONSOLE : right

LISTENER:  
	# typeScript compiler:
	-	CMD : $tsc $FILE --outDir $DIR $target
		WATCH : *.ts, *.tsx
	
	#  concatenate and emit output to test.js.
	-	CMD : $tsc $ROOT/utils/*.ts --outFile $ROOT/test.js $target
        WATCH : utils/*.ts
        EXCLUDE: bad.ts
        TIMEOUT : 5000
    
    # run $ROOT/test.js, and display debug output 
    -	CMD : node $ROOT/test.js
		CONSOLE : right

#  $ROOT       = .onsave file directory
#  $FILE       = current file path
#  $FILENAME   = current file name
#  $BASENAME   = current file name, not postfix
#  $DIR        = current file directory

# CONSOLE options
#  false       = not diaplay
#  name left   = diaplay at left view
#  name right  = diaplay at right view
#  name bottom = diaplay at bottom view

# WATCH options
# pattern are separated by commas，reserved words has "BUILD","NOBUILD"
#  - BUILD     = watch (super + b) key binding 
#  - NOBUILD   = just watch (on save) event

# ENV options
#  - CWP     = changes the current working directory to the given path.
#  - PATH
#  - HOME
#  ...

```



## Screenshots


![OnSave plugin](https://raw.githubusercontent.com/wl879/screenshots/master/pics/onsaveplugin.png)

![OnSave plugin](https://raw.githubusercontent.com/wl879/screenshots/master/pics/onsaveplugin.gif)






















