# What's new

## v3.4.0
- ROSAA modal integrated.
- ROSAA kinetics integrated.
- several bug fixes.
- several minor feature updates included.

## v3.3.2
- Bug fix for wrong trap time in felix file 
    - nshots will be taken from pow file if trap time in felix file is very large >50s.
---

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

---


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