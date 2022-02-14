# What's new
## v3.5.1-beta

- Timescan
    - Kinetic model implementation (TkFigure widget, save fit data, etc)
    - .scan file data analysed and exported in JSON format in EXPORT directory
- THz:

    - Full working THz-ROSAA kinetic model


- Major changes in program features:

    - Update from github realease
    - using vite for development and production build (instant HMR)
    - Removed db.json for electron-store module
    - Using executable python scripts instead of full python packages (safer and faster)
- Several bug fixes
---

## v3.5.0
- Plotly bug fix (Plotly is not included in window object)
- Masspec:
    - Getlabview setting can be varied to show only selected files or full files list
    - Masspectrum can now annotate a peak position (ctrl + left click) and delete annotation (ctrl + shift + left click)
- THz scans
    - Mention the number of iteration to be considered (useful in case you stopped the scan); write # iterations = number to be taken in the first line of the file
- Program updates
    - elctron-updater integrated with github as provider 
    - node API changed to preload js for electron-v14 (more secure and needed for future electron updates)

    - lot of bug fixes and improvements

---
## v3.4.0



- ROSAA modal integrated.
- ROSAA kinetics integrated.
- Individual file selection for baseline correction.
- several bug fixes.
- several minor feature updates included.

---
## v3.3.2

- Bug fix for wrong trap time in felix file 
    - nshots will be taken from pow file if trap time in felix file is very large >50s.
## v3.3.1

- Bug fix: OPO mode

## v3.3.0

- Feature updates:
    - New window for FELIX plotting (usefull for smaller screens)
    - While refreshing to get files, the selected files remains checked
    - PNotify integrated
    - WinBox.js modal integraeted
    - db.json replaced localStorage for saving datas.
- Bug fixes    
---
## v3.2.0

- Feature updates:
    - GetLabviewSettings updated
    - Theory vs Exp. feature udpated

    - Select files in file explorer by range (untill) using shift key


- Bug fixed: 
    - OPO create baseline doesn't work unless felix files are selected.
    - GetLabviewSetings bqlenses label order were reversed.
    - Table width auto overflow.
    - Theory plot with OPO mode.

    - Files refresh button added to FELIX matplotlib modal.    
---
## v3.1.1

- Bug fix: Masspec

## v3.1.0

- ROSAA simulation modal added.

- Individual page components are subdivided into smaller components for easier mangement and debugging.
- Included Terminal component in Setings for installing python dependencies and debugging.
- Included FELIX plotting in matplotlib to produce quality plots for exporting.


- Event dispatcher added for python process.

- Using Quill editor for report editor.
- Bug fix: Depletion scan dropdown menu auto updated

- Get labview settings from Masspec files
---