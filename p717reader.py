#!python3
#
#########################################################################################
### p717reader.py (python3)
###
### Demo program to parse the IOGP p717 wellbore survey data exchange format, used during development of the format.
###
### This is sample code, provided AS-IS.  Do with it whatever you want, but make sure to check.
###
### To run this program, install python3 on your computer (www.python.org).
### In Windows, open a command prompt by typing "cmd" in the start menu.  Then type
###
###   python p717reader.py inputfile.p717
###
### This will create output on the screen, to the program debug file p717reader.log
### and it will create one human readable output .txt file for each survey in the inputfile.p717
###
### The program runs in the single folder where the source files and data files are located.
###   p717classes.py: definition of classes
###   p717records.py: the format spec, including mandatory records and number of fields
###   data1.p717:      some random input in p717 format (comma separated ascii)
###   p717epsg.py:    sample how to connect to epsg.registry online
###
### The program defines classes for the main entities defined in p717 (e.g., WELLBOREREF, SURVEYREF, etc.)
### Then it loops over the cvs file to find all entities
### Then it sets up the relations, and goes over the file again to fill the objects
### Finally, it creates a human readable report
### See the IOGP p717 format specification document and user guide for details.
###
###
### Program version v0.96: draft based on v0.96 of user spec
###
### Bert Kampes, 2018-07-14
#########################################################################################
import os
import sys
import logging
import csv

### Get p717 record definitions from an include file by using import * (no namespace)
from p717records import *
### Get p717 classes such as PROJECT, STRUCTURE, WELL, WELLBORE, SURVEY, RIG, ...
from p717classes import *


###########################################################
### Small helper functions
###########################################################
def usage():
    print('')
    print('Usage: p717reader inputfile.p717')
    print('')
    print('   This program will attempt to read the p717 input file and produce a human readable report for each survey in it.')
    print('   Output files are named p717reader-survey1.txt, p717reader-survey2.txt, etc.')
    print('   It writes INFO level output to the screen and DEBUG to log file p717reader.log')
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
    print('cannot find p717 inputfile: ' + inputfile)
    usage()


###########################################################
### Create a logger and write to console and new output file
###########################################################
logging.basicConfig(filename='p717reader.log', filemode='w',
                    level=logging.DEBUG,
                    format='%(asctime)-8s: %(levelname)-8s: %(message)s',
                    datefmt='%H:%M:%S')

# define a Handler which writes INFO messages or higher to the sys.stderr
console   = logging.StreamHandler()
console.setLevel(logging.DEBUG) # Change this to INFO to have less on the screen (DEBUG written to log file)
console.setLevel(logging.INFO)

formatter = logging.Formatter('%(levelname)-8s: %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


### Handle program input
import datetime
logging.info("-----------------------------------------------------------------")
logging.info("p717reader v1.0 %s", str(datetime.datetime.now()))
logging.info("input file:    \"%s\"", inputfile)
logging.info("output folder: \"%s\"", ".")
logging.info("log file:      \"%s\"", "p717reader.log")
logging.info("-----------------------------------------------------------------")
logging.info("")
file_extension = ("."+inputfile).split(".")[-1]
logging.debug("File extension: .%s", file_extension)
if file_extension.lower()!="p717":
    logging.warning("Input file extension is not \".p717\"")

### Check if output folder is writable



###########################################################
### Create dictionaries with key: value pairs; where key=REF and value=object;
###########################################################
#dictUNIT      = {} # Unit of Measure;  add to existing dictUNITREF hard-coded
dictCRS       = {} # Coordinate Reference System
dictCT        = {} # Coordinate Transformation

### These are the main lookups to the objects
Project       = None # only one PROJECT in a p717 allowed, created for IOGP record identificatin record
n_PROJECTs    = 0  # Count number of Project Name records
dictSTRUCTURE = {} # dictionary of structures, key=STRUCTUREREF, value=OBJECT
dictWELL      = {} # ...
dictWELLBORE  = {}
dictSURVEY    = {}
dictRIG       = {}
dictWOBJ      = {} # O7 records; H7,4,0,0 ### Well Object Points
dictPOSLOG    = {} # H7,6,5,0 calculated values

### Magnetic and Gravity models (expect 1)
dictMAGREF    = {}
dictGRAVREF   = {}

dictMTREF     = {}  # to do - add Measurement Tools.  These can be found in Survey Definition and may be 

###########################################################
### First pass over p717 file: fill dictionaries for mandatory objects;
###########################################################

logging.info("")
logging.info("First pass over file to get main object entities...")
inputfilestream = open(inputfile, newline='')
reader          = csv.reader(inputfilestream)
row_count = 0
for row in reader:
    row_count+=1
    if row_count<1000: logging.debug("ROW %s: %s", '{:3d}'.format(row_count), row)# print line to log in case an error follows, but not for huge files

    ### PROJECT Definition
    if is_record(row, rec_IOGP_File_Identification_Record):
        logging.debug("Found IOGP File Identification")
        Project=PROJECT(row) #create object with constructor
        n_PROJECTs+=1
        
    ### UNITS
    elif is_record(row, rec_Unit_Of_Measure_Definition):
        key = safe_cast_to_int(row,5)
        unit_abbreviation = row[6].strip()   # don't know if there is an abbreviation column...
        logging.debug("Found UoM UNITREF:                         %s", key)
        #dictUNIT[key]=UNITOFMEASURE(row) #create object with constructor
        log.warning("to do: add to dictUNITREF")
        dictUNITREF[key] = unit_abbreviation

    ### CRS
    elif is_record(row, rec_CRS_Implicit_Identification):
        key = safe_cast_to_int(row,5)
        logging.debug("Found CRSREF:                              %s", key)
        dictCRS[key]=CRS(row) #create object with constructor
    ### CT
    elif is_record(row, rec_CT_Implicit_Identification):
        key = safe_cast_to_int(row,5)
        logging.debug("Found COTRANSREF:                          %s", key)
        dictCT[key]=CT(row) #create object with constructor

    ### STRUCTURE Definition
    elif is_record(row, rec_Structure_Definition):
        key = safe_cast_to_int(row,5)
        logging.debug("Found Structure Definition STRUCTUREREF:   %s", key)
        dictSTRUCTURE[key]=STRUCTURE(row) #create object with constructor

    ### WELL Identification
    elif is_record(row, rec_Well_Definition):
        key = safe_cast_to_int(row,5)
        logging.debug("Found well identification WELLREF:         %s", key)
        dictWELL[key]=WELL(row) #create object with constructor

    ### WELLBORE Identification: links back to a well
    elif is_record(row, rec_Wellbore_Definition):
        key = safe_cast_to_int(row,5)
        logging.debug("Found Wellbore Identification WELLBOREREF: %s", key)
        dictWELLBORE[key]=WELLBORE(row)

    ### SURVEY Definition: links back to a wellbore and rig
    elif is_record(row, rec_Survey_Definition):
        key = safe_cast_to_int(row,5)
        logging.debug("Found Survey Definition SURVEYREF:         %s", key)
        dictSURVEY[key]=SURVEY(row)

    ### RIG Definition: links back to a structure and a survey
    elif is_record(row, rec_Rig_Definition):
        key = safe_cast_to_int(row,5)
        logging.debug("Found Rig Details ZDPREF:                  %s", key)
        dictRIG[key]=RIG(row)

    ### WOBJ : Well Object Definition: e.g., WRP
    elif is_record(row, rec_Position_Object_Definition):
        key = safe_cast_to_int(row,5)
        logging.debug("Found Well Object WOBJREF:                 %s", key)
        dictWOBJ[key]=WOBJ(row)

    ### POSLOG: Position Log Record Type Definition
    elif is_record(row, rec_Position_Log_Type_Definition):
        key = safe_cast_to_int(row,5)
        logging.debug("Found POSLOGTYPE definition:               %s", key)
        dictPOSLOG[key]=POSLOG(row)

    ### MAGREF
    elif is_record(row, rec_Geomagnetic_Model_Definition): 
        key = safe_cast_to_int(row,5)
        logging.debug("Found MAGREF definition:               %s", key)
        dictMAGREF[key]=row # store row, associate with Survey later
    
    ### GRAVREF
    elif is_record(row, rec_Gravity_Model_Definition):
        key = safe_cast_to_int(row,5)
        logging.debug("Found GRAVREF definition:               %s", key)
        dictGRAVREF[key]=row # store row, associate with Survey later




###########################################################
### Perform some checks on the found objects
###########################################################
n_crss       = len(dictCRS)
n_cts        = len(dictCT)
logging.debug('Number of CRSs defined:       %s', n_crss)
logging.debug('Number of CTs defined:        %s', n_cts)
if n_crss<2:
    logging.critical("Not enough CRSs defined") # assume Hor + Vert min.
if n_cts<1:
    logging.warning("No Coordinate Transformation records found.")
    logging.warning("This may be allowed in case the base geogCRS is WGS 84 or if no coordinates are transformed.")

### Well Objects
n_wobjs  = len(dictWOBJ)
logging.debug('Number of well objects defined: %s', n_wobjs)
if n_wobjs<1:
    logging.critical("Not enough Well Objects defined")
logging.debug("debug overview of WOBJREF:")
for key in dictWOBJ:
    logging.debug("%d: %s (%s)", dictWOBJ[key].WOBJREF, dictWOBJ[key].wobj_short_name, dictWOBJ[key].wobj_type_name)
    
### Record Type Definitions
n_poslog = len(dictPOSLOG)
logging.debug('Number of poslogtypes defined: %s', n_poslog)
if n_poslog<1:
    logging.critical("Not enough n_poslog defined")


### Main entities
n_surveys    = len(dictSURVEY)
n_rigs       = len(dictRIG)
n_wellbores  = len(dictWELLBORE)
n_wells      = len(dictWELL)
n_structures = len(dictSTRUCTURE)

logging.info('  Number of surveys found:    %s', n_surveys)
logging.info('  Number of rigs found:       %s', n_rigs)
logging.info('  Number of wellbores found:  %s', n_wellbores)
logging.info('  Number of wells found:      %s', n_wells)
logging.info('  Number of structures found: %s', n_structures)


# Check that at least 1 of each is defined
if n_surveys==0:
    logging.critical("No survey definition records found")
if n_rigs==0:
    logging.critical("No rig definition records found")
if n_wellbores==0:
    logging.critical("No wellbore definition records found")
if n_wells==0:
    logging.critical("No well definition records found")
if n_structures==0:
    logging.critical("No structure definition records found")
if n_PROJECTs==0:
    logging.critical("No PROJECT definition record found")
if n_PROJECTs>1:
    logging.critical("More than 1 PROJECT definition record found")
if n_rigs>n_surveys:
    logging.warning("More rigs than surveys found")
if n_wellbores>n_surveys:
    logging.warning("More wellbores than surveys found")
if n_wells>n_wellbores:
    logging.warning("More wells than wellbores found")
if n_structures>n_wells:
    logging.warning("More structures than wells found")



##################################################################################
### Second pass: fill SURVEY objects with details
### Now the references are read, fill each survey
### Try every possible record defined in p717 to identify any unrecognized record.
##################################################################################
inputfilestream.seek(0) # rewind file to beginning to read it again
logging.info("")
logging.info("Second pass over file to get details...")
row_count = 0

### Reset mandatory record counters [cnt,min,max]; they are counted in is_record() called above
reset_record_counters() # used in is_record() function below to count all records

### Read every line of the file and check the recordID vs. the document spec as giving in file p717records.py
### Note that each line is error checked for number of fields and type of float/integer
### That is why each record in p717 should be in below loop and cannot be optimized out
for row in reader:

    # print line to log in case an index of out range error follows but not for huge files
    row_count+=1
    if row_count<1000: logging.debug("ROW %s: %s", '{:3d}'.format(row_count), row)
    ###
    if is_record  (row, rec_IOGP_File_Identification_Record): True # Already dealt with during first pass to construct PROJECT object
    elif is_record(row, rec_Project_Name):
        Project.set_rec_Project_Name(row)
    elif is_record(row, rec_Structure_Definition):      True # Already dealt with in first pass to construct STRUCTURE object
    elif is_record(row, rec_Well_Definition): True # Already dealt with during first pass to construct WELL object
    elif is_record(row, rec_Wellbore_Definition): True     # Already dealt with in first pass to construct WELLBORE object
    elif is_record(row, rec_Rig_Definition): True          # Already dealt with in first pass to construct RIG object
    elif is_record(row, rec_Survey_Definition): True       # Already dealt with in first pass to construct SURVEY object

    elif is_record(row, rec_Operator_Survey_Contractor_Acqn):
        key = safe_cast_to_int(row,5)
        if key>=0: dictSURVEY[key].set_rec_Operator_Survey_Contractor_Acqn(row)
    elif is_record(row, rec_Operator_Survey_Contractor_Proc):
        key = safe_cast_to_int(row,5)
        if key>=0: dictSURVEY[key].set_rec_Operator_Survey_Contractor_Proc(row)
    elif is_record(row, rec_Positioning_Contractor):
        key = safe_cast_to_int(row,6)
        if key>=0: dictWELL[key].set_rec_Positioning_Contractor(row)

    ### Full implementation should deal with units but leave it for now as we don't expect users to define them
    elif is_record(row, rec_Unit_Of_Measure_Definition): True
    elif is_record(row, rec_Example_Unit_Conversion): True

    ### Geodetic definitions in Common Header
    ### CRS details
    elif is_record(row, rec_CRS_Implicit_Identification): True # already dealt with in first pass to create CRS objects
    elif is_record(row, rec_CRS_Details):
        key = safe_cast_to_int(row,5)
        if key>=0: dictCRS[key].set_rec_CRS_details(row)

    ### Compound CRS: assume components CRSs and their CSs have been defined (otherwise set this after parsing full file...)
    elif is_record(row, rec_Compound_CRS_Horizontal_Identification):
        key = safe_cast_to_int(row,5)
        if key>=0: dictCRS[key].set_rec_Compound_CRS_Horizontal_Identification(row,dictCRS)
    elif is_record(row, rec_Compound_CRS_Vertical_Identification):
        key = safe_cast_to_int(row,5)
        if key>=0: dictCRS[key].set_rec_Compound_CRS_Vertical_Identification(row,dictCRS)

    ### Ignore projection parameters etc. for this reader program for now.
    ### Proper implementation should read these.
    elif is_record(row, rec_Base_Geographic_CRS_Details): True
    elif is_record(row, rec_Geodetic_Datum_Details): True
    elif is_record(row, rec_Prime_Meridian_Details): True
    elif is_record(row, rec_Ellipsoid_Details): True
    elif is_record(row, rec_Vertical_Datum_Details): True
    elif is_record(row, rec_Engineering_Datum_Details): True
    elif is_record(row, rec_Map_Projection_Details): True
    elif is_record(row, rec_Projection_Method_Details): True
    elif is_record(row, rec_Projection_Parameter_Details): True

    ### Parse CS details
    elif is_record(row, rec_Coordinate_System_Details):
        key = safe_cast_to_int(row,5)
        if key>=0: dictCRS[key].set_rec_Coordinate_System_Details(row)
    ###
    elif is_record(row, rec_Coordinate_Axis_Details):
        key = safe_cast_to_int(row,5)
        if key>=0: dictCRS[key].set_rec_Coordinate_Axis_Details(row)

    ### Parse CT details
    elif is_record(row, rec_CT_Implicit_Identification): True # already dealt with in first pass to create CT objects
    elif is_record(row, rec_CT_Explicit_Definition):
        key = safe_cast_to_int(row,5)
        if key>=0: dictCT[key].set_rec_CT_Explicit_Definition(row)
    elif is_record(row, rec_CT_Details):
        key = safe_cast_to_int(row,5)
        if key>=0: dictCT[key].set_rec_CT_Details(row)
    elif is_record(row, rec_CT_Method_Details):
        key = safe_cast_to_int(row,5)
        if key>=0: dictCT[key].set_rec_CT_Method_Details(row)
    elif is_record(row, rec_Transformation_Parameter_File_Details):
        key = safe_cast_to_int(row,5)
        if key>=0: dictCT[key].set_rec_CT_Parameters(row)
    elif is_record(row, rec_Transformation_Parameter_Details):
        key = safe_cast_to_int(row,5)
        if key>=0: dictCT[key].set_rec_CT_Parameters(row)
    elif is_record(row, rec_Example_Point_Conversion):  True

    ### Comment records: allow commas in comments
    elif is_record(row, rec_Additional_Information):    True
    elif is_record(row, rec_Additional_Information_C7): True

    ### File Contents
    elif is_record(row, rec_File_Contents_Description): 
        Project.set_rec_File_Contents_Description(row)
    elif is_record(row, rec_File_Processing_Details):
        Project.set_rec_File_Processing_Details(row)
    elif is_record(row, rec_File_Contents_Attribute):   True # ignore for now.

    ### Structure Details
    elif is_record(row, rec_Structure_Details):
        key = safe_cast_to_int(row,5)
        logging.debug("Found Structure details for Structure:     %s", key)
        #if key>=0: dictSTRUCTURE[key].set_rec_Structure_Details(row)
        if key in dictSTRUCTURE: 
            dictSTRUCTURE[key].set_rec_Structure_Details(row)
        else:
            logging.error("STRUCTUREREF not found: %i", key)

    ### Well_Details
    elif is_record(row, rec_Well_Details):
        key = safe_cast_to_int(row,5)
        logging.debug("Found well details for well:               %s", key)
        #if key>=0: dictWELL[key].set_rec_Well_Details(row)
        if key in dictWELL: 
            dictWELL[key].set_rec_Well_Details(row)
        else:
            logging.error("WELLREF not found: %i", key)

    # ### Rig Details
    # elif is_record(row, rec_Rig_Details):
        # key = safe_cast_to_int(row,5)
        # logging.debug("Found ZDP Rig details for Rig:               %s", key)
        # #if key>=0: dictRIG[key].set_rec_Rig_Details(row)
        # if key in dictRIG: 
            # dictRIG[key].set_rec_Rig_Details(row)
        # else:
            # logging.error("ZDPREF not found: %i", key)

    ### Survey Details
    elif is_record(row, rec_Survey_Details):
        key = safe_cast_to_int(row,5)
        #if key>=0: dictSURVEY[key].set_rec_Survey_Details(row)
        if key in dictSURVEY: 
            dictSURVEY[key].set_rec_Survey_Details(row)
        else:
            logging.error("SURVEYREF not found: %i", key)
    
    ### Survey Tie Point    
    elif is_record(row, rec_Survey_Tie_Point_Details):
        key = safe_cast_to_int(row,5)
        #if key>=0: dictSURVEY[key].set_rec_Survey_Tie_Point_Details(row)
        if key in dictSURVEY: 
            dictSURVEY[key].set_rec_Survey_Tie_Point_Details(row)
        else:
            logging.error("SURVEYREF not found: %i", key)
            
    ### Measurement Tool
    elif is_record(row, rec_Measurement_Tool_Definition):   
        logging.debug("ignoring Measurement Tool for now")
    elif is_record(row, rec_Measurement_Tool_Attributes):    True
    
    ### Position Objects
    elif is_record(row, rec_Position_Object_Definition):     True # Already dealt with in first pass to construct WOBJ object
    elif is_record(row, rec_Well_Object_Attributes):         True
        
    ### Geomagnetic and Gravity Model
    elif is_record(row, rec_Geomagnetic_Model_Definition):   True # Deal with in first pass, associate with survey below.
    elif is_record(row, rec_Gravity_Model_Definition):       True # Deal with in first pass, associate with survey below.

    ### MWD Extension Field Definition
    elif is_record(row, rec_M7_Record_Extension_Definition): 
        key = safe_cast_to_int(row,5)
        dictSURVEY[key].set_rec_M7_Record_Extension_Definition(row)

    ### MWD Extension Field Definition
    elif is_record(row, rec_G7_Record_Extension_Definition): 
        key = safe_cast_to_int(row,5)
        dictSURVEY[key].set_rec_G7_Record_Extension_Definition(row)
        
    ### Position log (MDINCAZ observables and calculated values)
    elif is_record(row, rec_Position_Log_Type_Definition):   True # Already dealt with in first pass to construct POSLOGTYPE objects

    ### Survey Tool Error Model (STEM)
    elif is_record(row, rec_Survey_Tool_Error_Model_Definition): True
    elif is_record(row, rec_Survey_Tool_Error_Model_Metadata):   True
    elif is_record(row, rec_Survey_Tool_Error_Model_Terms):      True

    ### Data records (O7, P7, M7, G7)

    ### O7 Position Object
    elif is_record(row, rec_O7_Position_Record):
        key = safe_cast_to_int(row,2)  # WOBJREF
        if key in dictWOBJ: 
            dictWOBJ[key].set_rec_O7_Position_Record(row)
        else:
            logging.error("WOBJREF not found: %i", key)
            
    ### P7 Position Log
    elif is_record(row, rec_P7_Position_Log_Record):
        key = safe_cast_to_int(row,2) # SURVEYREF
        if key in dictPOSLOG: 
            dictPOSLOG[key].set_rec_P7_Position_Log_Record(row)
        else:
            logging.error("POSLOGREF not found: %i", key)
            
    ### M7 Raw MWD Sensor data
    elif is_record(row, rec_M7_MWD_Raw_Sensor_Data_Record):
        key = safe_cast_to_int(row,2) # SURVEYREF
        if key in dictSURVEY: 
            dictSURVEY[key].set_rec_M7_MWD_Raw_Sensor_Data_Record(row)
        else:
            logging.error("SURVEYREF not found: %i", key)

    ### G7 Raw Gyro Sensor data
    elif is_record(row, rec_G7_Gyro_Raw_Sensor_Data_Record):
        key = safe_cast_to_int(row,2) # SURVEYREF
        if key in dictSURVEY: 
            dictSURVEY[key].set_rec_G7_Gyro_Raw_Sensor_Data_Record(row)
        else:
            logging.error("SURVEYREF not found: %i", key)        

    ### Ignore empty lines, or lines starting with "#" or "//" or "/*"
    elif len(row)==0: True # empty line
    #elif row[0][0].upper()=="C": True # Do not allow rows starting with C to be ignored as obvious typo may be "CH," vs "HC,"
    elif row[0][:7].lower()=="comment" or row[0][:4].lower()=="info": True
    elif row[0][0]=="#" or row[0][:2]=="//" or row[0][:2]=="/*" or row[0][:2]=="*/":
        logging.debug("Assume this is a row intended as a comment, starting with # or //")

    ### Else we have a problem: record not recognized
    else:
        logging.warning("Unrecognized record: %s", row)


### Report the counters for the mandatory records and dependents
report_records_check()



##################################################################################
### Attach correct PROJECT, STRUCTURE, WELL, WELLBORE, RIG to each SURVEY
##################################################################################
logging.info("")
logging.info("Collecting entity objects for each survey...")

for SURVEYREF in dictSURVEY:

    logging.info("")
    logging.info("SURVEYREF: %s: \"%s\"", SURVEYREF, dictSURVEY[SURVEYREF].survey_name)

    ### (should use function like dictRIG[ZDPREF].getrig() perhaps seems pythonic to do direct referencing)
    rig_ref = dictSURVEY[SURVEYREF].ZDPREF
    dictSURVEY[SURVEYREF].set_rig(dictRIG[rig_ref])
    logging.info("  --> ZDPREF: %s: \"%s\"", rig_ref, dictSURVEY[SURVEYREF].Rig.rig_name)
    #
    wellbore_ref = dictSURVEY[SURVEYREF].WELLBOREREF
    dictSURVEY[SURVEYREF].set_wellbore(dictWELLBORE[wellbore_ref])
    logging.info("  --> WELLBOREREF: %s: \"%s\"", wellbore_ref, dictSURVEY[SURVEYREF].Wellbore.primary_wellbore_name)
    #
    well_ref = dictSURVEY[SURVEYREF].Wellbore.WELLREF
    dictSURVEY[SURVEYREF].set_well(dictWELL[well_ref])
    logging.info("    --> WELLREF: %s: \"%s\"", well_ref, dictSURVEY[SURVEYREF].Well.primary_well_name)
    #
    structure_ref = dictSURVEY[SURVEYREF].Well.STRUCTUREREF
    dictSURVEY[SURVEYREF].set_structure(dictSTRUCTURE[structure_ref])
    logging.info("      --> STRUCTUREREF: %s: \"%s\"", structure_ref, dictSURVEY[SURVEYREF].Structure.structure_name)
    #
    #PROJECT_ref = dictSURVEY[SURVEYREF].Structure.PROJECTREF
    #dictSURVEY[SURVEYREF].set_PROJECT(dictPROJECT[PROJECT_ref])
    #logging.info("        --> PROJECTREF: %s: \"%s\"", PROJECT_ref, dictSURVEY[SURVEYREF].PROJECT.project_name)

    ### Set MAGREF and GRAVREF (both optional)
    mag_ref = dictSURVEY[SURVEYREF].MAGREF
    if mag_ref > 0:
        row = dictMAGREF[mag_ref]
        dictSURVEY[SURVEYREF].set_rec_Geomagnetic_Model_Definition(row)
        logging.info("      --> MAGREF: %s: \"%s\"", mag_ref, dictSURVEY[SURVEYREF].geomag_model_name)
    #
    grav_ref = dictSURVEY[SURVEYREF].GRAVREF
    if grav_ref > 0:
        row = dictMAGREF[grav_ref]
        dictSURVEY[SURVEYREF].set_rec_Gravity_Model_Definition(row)
        logging.info("      --> GRAVREF: %s: \"%s\"", grav_ref, dictSURVEY[SURVEYREF].gravity_model_name)
    
    ### Cross check internal consistency and required records dependent on type
    dictSURVEY[SURVEYREF].do_survey_cross_checks()



###########################################################
### Creating human readable reports per survey
###   PROJECT
###   STRUCTURE
###   WELL
###   WELLBORE
###   RIG
###   SURVEY
###   POSLOG table
###########################################################
logging.info("")
logging.info("Creating a human readable report for each survey in the p717 file...")
logging.info("")

import datetime

logging.error("Need to change this to loop over POSLOG and link to Surveys associated...")
logging.error("Need to change this to loop over POSLOG and link to Surveys associated...")

#keys = 
Poslog = dictPOSLOG[1] # for quick fix, hope there is a one..
for SURVEYREF in dictSURVEY:

    ### Open output file
    console.setLevel(logging.INFO)
    Survey  = dictSURVEY[SURVEYREF]
    logging.info("SURVEYREF: %s: %s", SURVEYREF, Survey.survey_name)

    ### Create new outputfile
    date    = datetime.date.today()
    outname = "p717reader-survey" + str(SURVEYREF) + "_" + str(date) + ".txt"
    logging.info("  Creating output file: %s", outname)
    outfh   = open(outname, 'w') # create new file

    ####
    outfh.write("==================================================================\n")
    outfh.write("This is a human readable output report for an IOGP p717 file\n")
    outfh.write("Created by p717reader.py on {}\n".format(str(datetime.datetime.now())))
    outfh.write("input file: {} SURVEYREF: {}\n".format(inputfile, SURVEYREF))
    outfh.write("p717reader spec draft v0.8 2017-12-25 provided AS-IS for demonstration purposes\n")
    outfh.write("==================================================================\n")
    outfh.write("\n")

    ### Stuff like report date, company, well identification, etc.
    outfh.write("------------------------------------------------------------------\n")
    outfh.write("PROJECT/:\n")
    outfh.write("------------------------------------------------------------------\n")
    outfh.write("Company:                   {}\n".format("unknown"))
    outfh.write("Project Name:              {}\n".format(Project.project_name))
    outfh.write("Structure:                 {}\n".format(Survey.Structure.structure_name))
    outfh.write("Well:                      {:32}   UWI:  {}\n".format(Survey.Well.primary_well_name, Survey.Well.primary_UWI))
    outfh.write("Wellbore:                  {:32}   UWBI: {}\n".format(Survey.Wellbore.primary_wellbore_name, Survey.Wellbore.primary_UWBI))
    outfh.write("Survey name:               {}\n".format(Survey.survey_name))
    outfh.write("Survey type:               {}\n".format(Survey.MTTYPE_name))
    outfh.write("\n")

    md_unit   = dictUNITREF[Survey.MD_UNITREF]      #.unit_name
    #zdpe_unit = dictUNITREF[Survey.Rig.ZDP_UNITREF] #.unit_name # unit for the ZDP elevation relative to the permanent datum
    zdpe_unit = Project.projectCRS_vert_unit
    outfh.write("RIG/WORKOVER:              {}\n".format(Survey.Rig.rig_name))
    outfh.write("TVD Reference (ZDP):       {} {} ({}) above VRS\n".format(Survey.Rig.ZDP_type, Survey.Rig.ZDP_elevation, zdpe_unit)) # same point by definition in p717
    outfh.write("MD Reference (ZDP):        {} {} ({}) above VRS\n".format(Survey.Rig.ZDP_type, Survey.Rig.ZDP_elevation, zdpe_unit)) # same point by definition in p717
    outfh.write("North Reference:           {}\n".format(Survey.AZ_type_name))
    outfh.write("\n")

    ### PROJECT
    PROJECTCRS_name = "unknown"
    
    if Project.projectCRS_CRSREF!=None: #may be the case if no POSLOG!
        PROJECTCRS_name = dictCRS[Project.projectCRS_CRSREF].get_crs_name()

    outfh.write("PROJECT CRS:                    {}\n".format(PROJECTCRS_name))
    # For compound, list components
    if dictCRS[Project.projectCRS_CRSREF].CRS_name_hor!=None:
        outfh.write("  Horizontal:                 {}\n".format(dictCRS[Project.projectCRS_CRSREF].CRS_name_hor))
    if dictCRS[Project.projectCRS_CRSREF].CRS_name_vert!=None:
        outfh.write("  Vertical:                   {}\n".format(dictCRS[Project.projectCRS_CRSREF].CRS_name_vert))
    outfh.write("\n")
    outfh.write("\n")


    ### STRUCTURE/SITE
    outfh.write("------------------------------------------------------------------\n")
    outfh.write("STRUCTURE/SITE: {}\n".format(Survey.Structure.structure_name))
    outfh.write("------------------------------------------------------------------\n")

    outfh.write("Coordinates and Accuracy of SRP:\n")
    Survey.Structure.report_SRP(dictWOBJ, outfh)
    outfh.write("\n")
    outfh.write("\n")

    ### WELL/SLOT
    outfh.write("------------------------------------------------------------------\n")
    outfh.write("WELL/SLOT: {}\n".format(Survey.Well.primary_well_name))
    outfh.write("------------------------------------------------------------------\n")
    outfh.write("Coordinates and Accuracy of WRP:\n")
    Survey.Well.report_WRP(dictWOBJ, outfh)
    outfh.write("\n")
    outfh.write("\n")

    ### WELLBORE
    outfh.write("------------------------------------------------------------------\n")
    outfh.write("WELLBORE: {}\n".format(Survey.Wellbore.primary_wellbore_name))
    outfh.write("------------------------------------------------------------------\n")
    outfh.write("Sidetrack?                 {}\n".format( "TO DO ********************"))
    outfh.write("\n")
    outfh.write("GEOPHYSICAL REFERENCE VALUES:\n")
    outfh.write("-----------------------------\n")
    # Magnetic:
    if Survey.geomag_model_name==None:
        outfh.write("Magnetic model:          {}\n".format("not specified"))
    else:
        angular_unit       = "deg"
        fieldstrength_unit = "nT"
        outfh.write("Strategy:                     {}\n".format(Survey.geomag_strategy))
        outfh.write("  Magnetic model name:          {}\n".format(Survey.geomag_model_name))
        outfh.write("  Magnetic model year:          {}\n".format(Survey.geomag_model_year))
        outfh.write("  Reference date:               {}\n".format(Survey.geomag_parameters_date))
        outfh.write("  to do ... add declination, dip, btotal or so applied... \n")
        #for row in Survey.geomag_parameters:
        #    outfh.write("    Geomagnetic parameters applied: {}: {} {} {} = decl: {} {angleunit}; dip: {} {angleunit}; intensity: {} {fieldunit}\n".format(
        #                row[6].strip(), row[7].strip(), row[8].strip(), row[9].strip(), row[10].strip(), row[11].strip(), row[12].strip(), angleunit=angular_unit, fieldunit=fieldstrength_unit))
    
    # Gravity
    if Survey.gravity_model_name==None:
        outfh.write("Gravity model:          {}\n".format("not specified"))
    else:
        outfh.write("Gravity model:          {}\n".format(Survey.gravity_model_name))
        #grav_unit_name = "m/s2"
        outfh.write("\n")
    outfh.write("\n")

    ### SURVEY
    outfh.write("------------------------------------------------------------------\n")
    outfh.write("SURVEY: {}\n".format(Survey.survey_name))
    outfh.write("------------------------------------------------------------------\n")
    outfh.write("Survey date:               {}\n".format(Survey.survey_start_date))
    outfh.write("Survey MD start:           {}\n".format(Survey.MD_start))
    outfh.write("Survey MD end:             {}\n".format(Survey.MD_end))
    outfh.write("\n")
    
    ### POSLOG
    outfh.write("Survey Calculation Method: {}\n".format("looking for min. curvature somewhere..."))
    outfh.write("Survey Calculation Method: {}\n".format(Poslog.LOCAL2GLOBAL_name))
    outfh.write("\n")

    # Grid Convergence:
    # if Survey.gc_where_defined==None:
        # outfh.write("Grid Convergence:          {}\n".format("not applied"))
    # elif Survey.gc_where_defined==1:
        # for row in Survey.gc_applied:
            # outfh.write("Grid Convergence applied: {}: {} {} = {} (deg)\n".format(row[9], row[10], row[11], row[12]))
    # elif Survey.gc_where_defined==2:
        # outfh.write("Grid Convergence applied:     {}\n".format("defined in poslog"))
    # elif Survey.gc_where_defined==3:
        # outfh.write("Grid Convergence applied:     {}\n".format("defined in rawdata log"))
    # else:
        # logging.error("not possible")

    # Scale Factor:
    # if Survey.sf_where_defined==None:
        # outfh.write("Scale Factor:              {}\n".format("not applied"))
    # elif Survey.sf_where_defined==1:
        # for row in Survey.sf_applied:
            # outfh.write("Scale Factor(s) applied:  {}: {} {} {}: sf={} ef={}\n".format(row[9], row[10], row[11], row[12], row[13], row[14]))
    # elif Survey.sf_where_defined==2:
        # outfh.write("Scale Factor applied:         {}\n".format("defined in poslog"))
    # else:
        # logging.error("not possible")


    outfh.write("\n")
    outfh.write("-------------------\n")
    outfh.write("SURVEY PROGRAM + ERROR MODEL:\n")
    outfh.write("-------------------\n")
    outfh.write("to do: print error model fromMD to MD, or show/get it from the poslog.\n")
    outfh.write("\n")
    outfh.write("\n")

    ### Get the p7 records and print it (use a function?)
    outfh.write("-------------------\n")
    outfh.write("SURVEY POSITION LOG\n")
    outfh.write("-------------------\n")
    Poslog.report_poslog(outfh)
    outfh.write("\n")


    outfh.write("----------------------------------------------------------------------\n")
    outfh.write("Casing Points\n")
    outfh.write("   DESIGN - lookup casing points from point table in p717.  There is a record that allows writing this...\n")
    # check H7,4,0,0 Position Object for type CP
    outfh.write("\n")
    outfh.write("Formations\n")
    # check H7,4,0,0 Position Object for type FT
    outfh.write("   - Formations lookup from point table in p717\n")
    outfh.write("\n")
    outfh.write("----------------------------------------------------------------------\n")

    ### Get the raw data and print it; figure out if there is any MWD or Gyro.
    outfh.write("\n")
    outfh.write("SURVEY RAW DATA\n")
    outfh.write("\n")
    outfh.write("\n")

    outfh.close()



### EOF.
