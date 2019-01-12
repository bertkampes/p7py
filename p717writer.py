#!python3
#
#########################################################################################
### p717writer.py (python3)
###
### Demo program to write IOGP p717 wellbore survey data exchange format, used during development of the format.
###
### This is sample code, provided AS-IS.  Do with it whatever you want, but make sure to check.
###
### To run this program, install python3 on your computer (www.python.org).
### In Windows, open a command prompt by typing "cmd" in the start menu.  Then type
###
###   python p717writer.py  (to be made in a p7200 converter; for now testing...)
###
### The program runs in the single folder where the source files and data files are located.
###   p717classes.py: definition of classes
###   p717records.py: the format spec, including mandatory records and number of fields
###   data1.csv:      some random input
###   p717epsg.py:    sample how to connect to epsg.registry online
###
###
### Program version v0.8: draft based on v0.8 of user spec
###
### Bert Kampes, 2018-07-14
#########################################################################################
import os
import sys
import logging
import csv

### Get p717 record definitions from an include file by using import * (no namespace) 
from p717records import *
### Get p717 classes such as FIELD, STRUCTURE, WELL, WELLBORE, SURVEY, RIG, ...  See file for details
from p717classes import *


###########################################################
### Small helper functions
###########################################################
def usage():
    print('')
    print('Usage: p717writer inputfile.p7200')
    print('')
    print('   This program will attempt to read the p7200 input file and produce a p717 output file')
    print('')
    exit()



###########################################################
### MAKE THIS INTO A MAIN(args) SOME DAY...
###########################################################
### Parse command line input to set input file, output file (default same with extension added), logging options
### compile into executable for distribution or bat file to drag files into or interactive

inputfile     = 'data1.csv'
num_arguments = len(sys.argv)-1
if num_arguments!=1: usage()

inputfile = sys.argv[1]
if not os.path.isfile(inputfile):
    print('cannot fine p72000 inputfile: ' + inputfile)
    usage()

 
###########################################################
### Create a logger and write to console and new output file
###########################################################
logging.basicConfig(filename='p72000to17writer.log', filemode='w',
                    level=logging.DEBUG,
                    format='%(asctime)-8s: %(levelname)-8s: %(message)s',
                    datefmt='%H:%M:%S')

# define a Handler which writes INFO messages or higher to the sys.stderr
console   = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)-8s: %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


### Handle program input
import datetime
logging.info("-----------------------------------------------------------------")
logging.info("p717writer v1.0 %s", str(datetime.datetime.now()))
logging.info("input file:    \"%s\"", inputfile)
logging.info("output folder: \"%s\"", ".")
logging.info("-----------------------------------------------------------------")
logging.info("")
file_extension = ("."+inputfile).split(".")[-1]
logging.debug("File extension: .%s", file_extension)
if file_extension.lower()=="p717":
    logging.warning("Input file extension is \".p717\" not possible")
    usage()

### Set output file name
date    = datetime.date.today()
outname = inputfile + "." + str(date) + ".p717"

### Check if output folder is writable



###########################################################
### Assume p7200 has a single survey
### 1. create p717 objects by using a dummy row
### 2. fill the variables by reading p72000 file
### 3. write the p717 lines using write_record functions
###########################################################
dictCRS       = {} # Coordinate Reference System

### Well Object Points
dictWOBJ      = {} # O7 records; H7,4,0,0   --> put them with other objects after reading them



###########################################################
### Test 1 write IOGP record and CRS  
###########################################################
# clean these rows out; then set the p72000 variables - for now keep it in
logging.warning("don't forget to reset these to empty strings! after testing - move this to test function and call that...")
logging.info("")
logging.info("Creating empty p717 objects...")

#row1  = "IOGP,IOGP P7,7,1.0,1,2017:03:25,17:40:01,Example.P717,".split(",")
row11 = "HC,0,1,1,Project Name,Pegasus,Pegasus Field,Texas,United States,USA,NAD27 / Texas Central + NGVD29 depth (ftUS),4,ftUS,ftUS)".split(",")
#row2  = "HC,0,2,1,Structure Definition,1,Pad A,SRP,1,Centre Slot A1,Onshore".split(",")
#row3  = "HC,0,3,1,Well Definition,1,1,WRP,2,207/29-A6,207/29-A6,DTI,,,,As-drilled,UKCS Block 207/29,2012:05:15".split(",")
#row4  = "HC,0,4,1,Wellbore Definition,1,1,207/29-2Z,207/29-2Z,OGA,,,,Existing,207/29,, ST=Y,1750.5,1,2012:06:01".split(",")
#row5  = "HC,0,5,1,ZDP Rig/Workover Definition,1,Unknown Rig,KB,275.5,0.5, 8.5, 2011:01:01".split(",")
#row6  = "HC,0,6,1,Survey Definition,1,1,1,Final Run,Gyro,2,Open Hole,7-5/8, In,1100.0,2150.0,ft,Grid North,,2012:07:01,2012:07:02".split(",")
row61 = "HC,0,7,1,Operator/Survey Contractor (Acqn),1,Highland Oil,Tain Drilling,TD101,".split(",")
row62 = "HC,0,7,2,Operator/Survey Contractor (Proc),1,Lowland Exploration and Production,Directional Services Inc,DS501,1994:04:15".split(",")

Project   = PROJECT()
Structure = STRUCTURE()
Well      = WELL()
Wellbore  = WELLBORE()
Rig       = RIG()
Survey    = SURVEY()

#Project   = PROJECT(row1)
Project.set_rec_Project_Name(row11)
#Structure = STRUCTURE(row2)
#Well      = WELL(row3)
#Wellbore  = WELLBORE(row4)
#Rig       = RIG(row5)
#Survey    = SURVEY(row6)
Survey.set_rec_Operator_Survey_Contractor_Acqn(row61)
Survey.set_rec_Operator_Survey_Contractor_Proc(row62)


### Set Geodetic objects
# interactive: provide EPSG codes of hor&vert - then parse the fields.
row1  = "HC,1,3,0,CRS Number/EPSG Code/Name/Source                  ,1, 4326,WGS 84                          ,8.5,2014:06:27,EPSG,Global CRS for well object position records".split(",")
row2  = "HC,1,3,0,CRS Number/EPSG Code/Name/Source                  ,2, 4230,ED50                            ,8.5,2014:06:27,EPSG,Used for Geographical coordinates in PosLog".split(",")
row3  = "HC,1,3,0,CRS Number/EPSG Code/Name/Source                  ,3,23031,ED50 / UTM zone 31N             ,8.5,2014:06:27,EPSG,Used for Structure and Displacements Origin CRS".split(",")
row4  = "HC,1,3,0,CRS Number/EPSG Code/Name/Source                  ,4, 8051,MSL depth (ft),,,,                                   Used for Water Depth and TVD below VRS".split(",")
row5  = "HC,1,3,0,CRS Number/EPSG Code/Name/Source                  ,5,     ,ED50 / UTM zone 31N + MSL depth (ft),,,,             Used for Compound CRS for Projected + TVD below VRS coordinates in PosLog and WRP".split(",")
row31 = "HC,1,6,1,Coordinate System Axis 1                          ,3,1,1,Easting ,east ,E,1,metre".split(",")
row32 = "HC,1,6,1,Coordinate System Axis 2                          ,3,2,2,Northing,north,N,1,metre".split(",")
row41 = "HC,1,6,1,Coordinate System Axis 1                          ,4,1,214,Depth,down,D,15,foot".split(",")
row51 = "HC,1,4,0,CRS Number/EPSG Code/Type/Name                    ,5,,7,compound,ED50 / UTM zone 31N + MSL depth (ft)".split(",")
row52 = "HC,1,4,1,Compound Horizontal CRS                           ,5,3,23031,ED50 / UTM zone 31N".split(",")
row53 = "HC,1,4,2,Compound Vertical CRS                             ,5,4, 8051,MSL depth (ft)".split(",")

# CS axes not required but would be very useful - how else are we going to know which is Easting and which is Northing.
dictCRS[1] = CRS(row1)
dictCRS[2] = CRS(row2)
dictCRS[3] = CRS(row3)
dictCRS[3].set_rec_Coordinate_Axis_Details(row31)
dictCRS[3].set_rec_Coordinate_Axis_Details(row32)
dictCRS[4] = CRS(row4)
dictCRS[4].set_rec_Coordinate_Axis_Details(row41)
dictCRS[5] = CRS(row5)
dictCRS[5].set_rec_CRS_details(row51)
dictCRS[5].set_rec_Compound_CRS_Horizontal_Identification(row52,dictCRS)
dictCRS[5].set_rec_Compound_CRS_Vertical_Identification(row53,dictCRS)

### CT (dummy example)
row = "HC,1,7,0,Transformation Number/EPSG Code/Name/Source       ,1,1311,ED50 to WGS 84 (18),8.5,2014:06:27,EPSG,".split(",")
Cotrans = CT(row)

### P7 Header
row1 = "H7,0,0,0,File Contents Description…,Definitive survey of 207/29-1Z wellbore from 2001,".split(",")
row2 = "H7,0,1,0,Processing Details…       ,Reformatted to P7/17 format by Well Data Processors INC".split(",")
#row3 = "H7,0,2,0,Legacy File Name…         ,3,207_29-1A.p72000,,".split(",")
Project.set_rec_File_Contents_Description(row1)
Project.set_rec_File_Processing_Details(row2)

### P7 records (populated for test only) - to be replaced with empty strings, populated by p72000 read values.
row1  = "H7,1,0,0,Structure Details,1,Top of template,192.0, 8021.4, 2011:06:21,0, True North,30.207".split(",")
row2  = "H7,1,1,0,Well Details,1,Centre slot A1,Template installation report,A1,32.0,22, 15.0, 10.0".split(",")
#row3  = "H7,1,3,0,ZDP Rig/Workover Details,1,64.5,64.5".split(",")
row4  = "H7,1,4,0,Survey Details,1,1,1,MD-Drillpipe,1,Indicated Depth,1,8,AZ_GRID,3, Calculated from AZ_MAGN,1,2.151,-1.123,35342, 1972:06:28, 1,1.5, 9.807394,1,1".split(",")
row41 = "H7,1,4,1,Survey Tie Point Details,1,2015.00,-2.50,1.30,2008.7".split(",")



Structure.set_rec_Structure_Details(row1)
Well.set_rec_Well_Details(row2)
#Rig.set_rec_Rig_Details(row3)
Survey.set_rec_Survey_Details(row4)
Survey.set_rec_Survey_Tie_Point_Details(row41)

### test MTREF
row1  = "H7,3,0,0,Measurement Tool Definition,2,High-Speed Gyro,HSG,2,Gyro-Tools Inc,unknown serial number".split(",")
row11 = "H7,3,0,1,Data Retrieval,2,1,Stored in tool,,".split(",")
row12 = "H7,3,0,1,Measurement Trigger,2,2,some text,,".split(",")
Survey.set_rec_Measurement_Tool_Definition(row1)
Survey.set_rec_Measurement_Tool_Attributes(row11)
Survey.set_rec_Measurement_Tool_Attributes(row12)


### H7,4,0,0 is definition record for points, and O7 has details optionally.
### This allows e.g., formation tops or casing shoes.  But also WRP and SRP mandatory minimum.
row11 = "H7,4,0,0,Position Object Definition, 1, Origin Pad A,        1,Structure Reference Point, ,,".split(",")
row12 = "H7,4,0,0,Position Object Definition, 2, Conductor 210/16A-1, 2,Well Reference Point, on Pad A, 1, 50.0".split(",")
row13 = "H7,4,0,0,Position Object Definition, 3, Origin Pad B,        1,Structure Reference Point, ,,".split(",")
row14 = "H7,4,0,0,Position Object Definition, 4, Conductor 210/16A-2, 2,Well Reference Point, on Pad B, 1, 50.0".split(",")
logging.warning("add BHL, ZDP perhaps...  formations, etc.")

key11 = safe_cast_to_int(row11,5)
dictWOBJ[key11] = WOBJ(row11)
key12 = safe_cast_to_int(row12,5)
dictWOBJ[key12] = WOBJ(row12)
key13 = safe_cast_to_int(row13,5)
dictWOBJ[key13] = WOBJ(row13)
key14 = safe_cast_to_int(row14,5)
dictWOBJ[key14] = WOBJ(row14)

#+++
row31 = "O7,0,1, Origin Pad-A, SRP, 425353.84,6623785.69,118.4, 59.74384278,1.67198083, 59.74328556,1.67031667, 1.4,1.2".split(",")
row32 = "O7,0,2, RefPt Well 1, WRP, 425353.84,6623785.69,118.4, 59.74384278,1.67198083, 59.74328556,1.67031667, 1.4,1.2".split(",")
row33 = "O7,0,3, Origin Pad-B, SRP, 425353.84,6623785.69,118.4, 59.74384278,1.67198083,            ,          ,    ,   ".split(",")
row34 = "O7,0,4, RefPt Well 2, WRP, 425353.84,6623785.69,118.4, 59.74384278,1.67198083, 59.74328556,1.67031667, 1.4,1.2".split(",")
key31 = safe_cast_to_int(row31,2)
dictWOBJ[key31].set_rec_O7_Position_Record(row31)
key32 = safe_cast_to_int(row32,2)
dictWOBJ[key32].set_rec_O7_Position_Record(row32)
key33 = safe_cast_to_int(row33,2)
dictWOBJ[key33].set_rec_O7_Position_Record(row33)
key34 = safe_cast_to_int(row34,2)
dictWOBJ[key34].set_rec_O7_Position_Record(row34)


###
logging.warning("grav model definitions to be reviewed;  I changed them v094")

row1 = "H7,5,0,0,Geomagnetic Model Definition,1,Single Point Supplied for Survey by Operator,IGRF1972,1972,".split(",")
row2 = "H7,5,1,0,Gravity Model Details, 1,IGF80".split(",")
Survey.set_rec_Geomagnetic_Model_Definition(row1)
Survey.set_rec_Gravity_Model_Definition(row2)

### Skip raw_input extension fields

### poslog with 3 extension fields
#row1 = "H7,6,5,0,Position Log Type Definition,1,Composite,1,1,Minimum Curvature,6666,LMP,0,,0, 3, 1;;var_N;1, 2;;var_E;1, 3;;var_D;1".split(",")
#Poslog = POSLOG(row1)
Poslog = POSLOG()

row1 = "P7,0,1,1,1,A001Mb_MWD,10,D,8,  Other, 173.09, 2.19,292.15,   3.74, -12.63, 173.00,6623785.69,425353.84, 117.00,59.74384278,1.671980833, 97; 98; 99".split(",")
row2 = "P7,0,1,1,1,A001Mb_MWD,10,D,2,Planned, 200.00, 2.19,292.15,   4.27, -13.94, 209.88,6623786.22,425352.53, 153.88,59.74384722,1.671957222, 97; 98; 99".split(",")
row3 = "P7,0,1,1,1,A001Mb_MWD,10,D,2,Planned, 300.00, 5.00,300.00,   6.88, -18.93, 299.70,6623788.83,425347.55, 243.70,59.74386972,1.671867778, 97; 98; 99".split(",")
row4 = "P7,0,1,1,1,A001Mb_MWD,10,D,2,Planned, 780.77,45.21, 62.97, 100.45, 123.34,   734.32,6623882.37,425489.77, 678.32,59.74473500,1.674363889, 97; 98; 99".split(",")
row5 = "P7,0,1,1,1,A001Mb_MWD,10,D,2,Planned,4294.98,45.21, 62.97,1234.00,2345.00, 3210.00,6625015.54,427710.69, 3154.00,59.75530000,1.713474167, 97; 98; 99".split(",")
row6 = "P7,0,1,1,1,A001Mb_MWD,10,D,2,Planned,4380.15,45.21, 62.97,1261.47,2398.00, 3270.00,6625043.00,427764.51, 3214.00,59.75555583,1.714422222, 97; 98; 99".split(",")
Poslog.set_rec_P7_Position_Log_Record(row1)
Poslog.set_rec_P7_Position_Log_Record(row2)
Poslog.set_rec_P7_Position_Log_Record(row3)
Poslog.set_rec_P7_Position_Log_Record(row4)
Poslog.set_rec_P7_Position_Log_Record(row5)
Poslog.set_rec_P7_Position_Log_Record(row6)

### raw data
row11 = "M7,0,1,1,2014:09:17:13:15:22.0,1,1740.0,36.0, 75.43,41.92,158.75,1705.16,1, 4.177509,3.972274,7.934024,10182.6299,36850.9976,52571.98776,9.807103,65003.81429,71.921632,304.220706,-133.557428,9.806986, 65094.495067,71.939312,-2.0,0.0,".split(",")
row12 = "M7,0,1,1,2014:09:17:13:15:22.0,1,1740.0,36.0, 75.43,41.92,158.75,1705.16,1, 4.177509,3.972274,7.934024,10182.6299,36850.9976,52571.98776,9.807103,65003.81429,71.921632,304.220706,-133.557428,9.806986, 65094.495067,71.939312,-2.0,0.0,".split(",")
row13 = "M7,0,1,1,2014:09:17:13:15:22.0,1,1740.0,36.0, 75.43,41.92,158.75,1705.16,1, 4.177509,3.972274,7.934024,10182.6299,36850.9976,52571.98776,9.807103,65003.81429,71.921632,304.220706,-133.557428,9.806986, 65094.495067,71.939312,-2.0,0.0,".split(",")
row21 = "G7,0,2,1,2014:09:17:13:15:22.0,1,1740.0,36.0,75.0,42.48,158.54,1705.16,1, 4.1797, 3.9694,7.9337,-1.0089,10.3147,-9.4003,9.80665,60.0,15.041, 303.8984,-133.5220,9.80665,60.0,15.041,0.0,".split(",")
Survey.set_rec_M7_MWD_Raw_Sensor_Data_Record(row11)
Survey.set_rec_M7_MWD_Raw_Sensor_Data_Record(row12)
Survey.set_rec_M7_MWD_Raw_Sensor_Data_Record(row13)
logging.info("following line will give a critical error because survey2 raw data set to survey 1")
Survey.set_rec_G7_Gyro_Raw_Sensor_Data_Record(row21)




###########################################################
### Read p72000 file into Objects 
###########################################################
logging.info("")
logging.info("Reading p72000 file contents")
#H8002 EPSG Projected CRS Name: ED50 / UTM zone 31N
#H8003 EPSG Projected CRS Code: 23031
#H8004 EPSG Vertical CRS Code: 5100
#H8005 EPSG Vertical CRS Name: Mean Sea Level
#H0230 Projected CRS Units: 1
#H0231 Geographical CRS Units: 1

p72000_row = 'H8002 EPSG Projected CRS Name: ED50 / UTM zone 31N'
key = p72000_row.split()[0]
val = p72000_row.split(":")[1]

#inputfilestream = open(inputfile, newline='')
#reader          = csv.reader(inputfilestream)
#row_count = 0

#read the p72000 file in memory and scan it?
#if record = H8002 then fill CRS...
    
  
  
###########################################################
### Write p717 file
###########################################################
logging.info("")
logging.info("Writing the p717 file...")
logging.info("")


### Open output file
console.setLevel(logging.INFO)
        
### Create new outputfile
logging.info("  Creating output file: %s", outname)
outfh   = open(outname, 'w') # create new file


logging.warning("when reading from p72000 dont forget to convert heights if not in vertCRS units...")


###
outfh.write("==================================================================\n")
outfh.write("This p717 file converted from p7200 input as test.\n")
outfh.write("Created by p717writer.py on {}\n".format(str(datetime.datetime.now())))
outfh.write("input file: {}\n".format(inputfile))
outfh.write("p717writer based on format specification draft v1.0 2018-07-15 provided AS-IS for demonstration purposes only!\n")
outfh.write("==================================================================\n")
outfh.write("\n")

### Write Common Header Records
Project.write_rec_IOGP_File_Identification_Record(outfh)
Project.write_rec_Project_Name(outfh)
Structure.write_rec_Structure_Definition(outfh)
Well.write_rec_Well_Definition(outfh)
Wellbore.write_rec_Wellbore_Definition(outfh)
Rig.write_rec_Rig_Definition(outfh)
Survey.write_rec_Survey_Definition(outfh)
outfh.write("\n")

Survey.write_rec_Operator_Survey_Contractor_Acqn(outfh)
Survey.write_rec_Operator_Survey_Contractor_Proc(outfh)
outfh.write("\n")

### Geodetic Definitions (must be loaded in CRS objects as shown above - from p72000 or interactively from prompt)
for CRSREF in dictCRS:
    CRS = dictCRS[CRSREF]
    CRS.write_rec_CRS_Implicit_Identification(outfh)
outfh.write("\n")
outfh.write("CC,0,0,0,Explicit CRS definition records follow for each CRS not in EPSG database\n") 
for CRSREF in dictCRS:
    CRS = dictCRS[CRSREF]
    if CRS.CRS_epsg<=0:
        CRS.write_rec_CRS_Details(outfh)
    if int(CRSREF) in [3,4]:    
        CRS.write_rec_Coordinate_Axis_Details(outfh)
    #HC,1,3,0,CRS Number/EPSG Code/Name/Source,1, 4326,WGS 84,8.5,2014:06:27,EPSG,Global CRS for well object position records
    #HC,1,4,0,CRS Number/EPSG Code/Type/Name  ,1,4326,2,geographic 2D,WGS 84
    #HC,1,4,4,Geodetic Datum                  ,1,6326,World Geodetic System 1984,1984:01:01
    #HC,1,4,5,Prime Meridian                  ,1,8901,Greenwich,0,3,degree
    #HC,1,4,6,Ellipsoid                       ,1,7030,WGS 84,6378137,1,metre,298.2572236
    #HC,1,6,0,Coordinate System               ,1,6422,Ellipsoidal 2D CS,3,Ellipsoidal,2
    #HC,1,6,1,Coordinate System Axis 1        ,1,1,106,Geodetic latitude ,north,Lat ,3,degree
    #HC,1,6,1,Coordinate System Axis 2        ,1,2,107,Geodetic longitude,east ,Long,3,degree        
    ### Compound components
    if CRS.CRS_type_code==7:
        CRS.write_rec_Compound_CRS_Horizontal_Identification(outfh)
        CRS.write_rec_Compound_CRS_Vertical_Identification(outfh)
outfh.write("\n")
Cotrans.write_rec_CT_Implicit_Identification(outfh)
outfh.write("\n")


### P7 specific records
outfh.write("CC,0,0,0,The P7-Specific header records follow\n")
Project.write_rec_File_Contents_Description(outfh)
Project.write_rec_File_Processing_Details(outfh)
#outfh.write("H7,0,0,0,File Contents Description               ,Sample p717 created by computer program,\n")
#outfh.write("H7,0,1,0,Processing Details                      ,Manually re-formatted after initial conversion\n")

Structure.write_rec_Structure_Details(outfh)
Well.write_rec_Well_Details(outfh)
#Rig.write_rec_Rig_Details(outfh)
Survey.write_rec_Survey_Details(outfh)

Survey.write_rec_Survey_Tie_Point_Details(outfh)

outfh.write("\n")
Survey.write_rec_Measurement_Tool_Definition(outfh)
Survey.write_rec_Measurement_Tool_Attributes(outfh)

### skip WOBJ now...
outfh.write("\n")
outfh.write("CC,0,0,0,Position Objects follow\n")
for key in dictWOBJ:
    dictWOBJ[key].write_rec_Position_Object_Definition(outfh)
outfh.write("\n")
for key in dictWOBJ:
    dictWOBJ[key].write_rec_O7_Position_Record(outfh)


###
outfh.write("\n")
Survey.write_rec_Geomagnetic_Model_Definition(outfh)
Survey.write_rec_Gravity_Model_Definition(outfh)

### Data records definition (POSLOG)
logging.warning("skipping over raw data extension fields")
logging.warning("skipping over error model definitions")
outfh.write("\n")
Poslog.write_rec_Position_Log_Type_Definition(outfh)

outfh.write("\n")
Poslog.write_rec_P7_Position_Log_Record(outfh)
outfh.write("\n")

### Write raw data records.  A survey has either MWD or Gyro.  For testing it is doing both currently.  P72000 converter would not have it anyway.
outfh.write("CC,0,0,0, Following are the MWD raw data\n")
Survey.write_rec_M7_MWD_Raw_Sensor_Data_Record(outfh)
outfh.write("\n")
outfh.write("CC,0,0,0, Following are the Gyro raw data\n")
Survey.write_rec_G7_Gyro_Raw_Sensor_Data_Record(outfh)

outfh.write("\n")    
outfh.close()



### EOF.
