makecert.exe ^
-n "CN=felion,O=FELION,L=Nijmegen,C=NL" ^
-r ^
-pe ^
-a sha512 ^
-len 4096 ^
-cy authority ^
-sv felion.pvk ^
-sr LocalMachine ^
-ss Root ^
felion.cer

pvk2pfx.exe ^
-pvk felion.pvk ^
-spc felion.cer ^
-pfx felion.pfx ^
-po felion