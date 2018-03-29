# Scripts overview

*General Description:* In general all scripts that works with Chroma must follow the following rules:
1.  Scripts must take in two input, the path of the GCode and the path of the Parameter file
2.  Scripts output must be the same file name as the GCode entered except with the addition of "_fixed" at the end of the GCode.
    An example would be passing Sphere.GCode into a script, a new GCode should be created call Sphere_fixed.GCode
3.  Once a new script is added, it's description and functionality should be added into ScriptDetail.txt found in the src folder.
