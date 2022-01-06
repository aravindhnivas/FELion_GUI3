signtool sign /f .\felion.pfx /p felion /fd SHA256 ..\resources\felionpy\felionpy.exe
signtool sign /f .\felion.pfx /p felion /fd SHA256 "..\dist\FELion_GUI3 Setup*.exe"