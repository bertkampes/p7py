#########################################################################################
### p717records.py
###
### To be included in p717checker program as: from p717records import *
###
### File contains
###   1) Dicts with constants REF and ID lookup
###   2) tuples with record ID definitions (tuples are unmutable and hashable, so can be used in dicts, also to make case statement to execute functions)
###   3) Dict of all Records length and format (type)
###   4) Helper functions for reading, writing, comparing (parsing is done in class)
###
### v1: draft based on v0.99c of IOGP p717 wellbore data exchange format specification
### This code is sample code, provided AS-IS.  Do with it whatever you want, but make sure to check.
###
### Bert Kampes, 2019-06-23
#########################################################################################

import logging  # Used in helper functions.  Logger needs to be initialized in caller


###########################################################
### REF and ID from p717 format
### See format specification document tables and Appendix A
###########################################################

### table 7: Format-defined UNITREF (use abbreviations here but may want to include full names and definitions later for reporting and calculations)
dictUNITREF       = {1: 'm',      2: 'rad',        3: 'deg',      4: '-',        5: 'ft',     6: 'ftUS', 7: 'mm',  8: 'in',     9: 'ftSe', 10: 'ftCla', 
                    11: 'lkCla', 12: 'sec',       13: 'gr',      14: 'ppm',     15: 's',     16: 's',   17: 's',  18: 'ms',    19: 'm/s',  20: 'm/s2',
                    21: 'rad/m', 22: 'deg/30m',   23: 'deg/100ft', 24: 'T',   25: 'nT', 26: 'rad/s', 27: 'deg/h', 
                    28: 'sqm',   29: 'sqft',      30: 'sqftUS',   31: 'mxft', 32: 'mxftUS',
                    }

### table 8: CRSTYPEREF 
dictCRSTYPEREF    = {1: 'Projected', 2: 'Geographic 2D', 3: 'Geographic 3D', 4: 'Geocentric', 5: 'Vertical', 6: 'Engineering', 7: 'Compound', }

### table 9: CSTYPEREF
dictCSTYPEREF     = {1: 'Affine',    2: 'Cartesian',     3: 'Ellipsoidal',   4: 'Polar',      5: 'Vertical', }

### table 10: ZDPTYPES
dictZDPTYPES      = {'BR' : 'RIG BRACING', 
					'CV' : 'CROWN VALVE',
					'DF' : 'DERRICK FLOOR',
					'GL' : 'GROUND LEVEL',
					'KB' : 'KELLY BUSHING',
					'LAT' : 'LOWEST ASTRONOMIC TIDE',
					'MLLW' : 'MEAN LOWER LOW WATER',
					'MT' : 'DRILLING FLOOR MAT',
					'PT' : 'PIPE TOP',
					'RF' : 'RIG FLOOR',
					'RT' : 'ROTARY TABLE',
					'SF' : 'SEA FLOOR',
					'TBF' : '	TOP BOTTOM FLANGE',
					'TC' : 'TOP CELLAR',
					'UN' : 'unknown',
					}

### table 11: WOBSID Name and Type (MDINCAZ types)
### dictWOBSID[t][0]    is the Type Name (n=1:10)
### dictWOBSID[t][1][f] is the Type Flag (f=0:4)
dictWOBSID        = {1: ['MD-Drillpipe', {0: 'Planned', 1: 'Indicated Depth', 2: 'Calibrated Depth', 3: 'Corrected Depth', 4: 'True Along-hole Depth', }],
                     2: ['MD-Wireline',  {0: 'Planned', 1: 'Indicated Depth', 2: 'Calibrated Depth', 3: 'Corrected Depth', 4: 'True Along-hole Depth', }],
                     3: ['MD-tubing',    {0: 'Planned', 1: 'Indicated Depth', 2: 'Calibrated Depth', 3: 'Corrected Depth', 4: 'True Along-hole Depth', }],
                     4: ['MD-Other',     {0: 'Planned', 1: 'Indicated Depth', 2: 'Calibrated Depth', 3: 'Corrected Depth', 4: 'True Along-hole Depth', }],
                     5: ['INCL',         {0: 'Planned', 1: 'Surveyed',        2: 'Back-calculated', }],
                     6: ['AZIM_MAGN',    {0: 'Planned', 1: 'Surveyed',        2: 'Back-calculated', }],
                     7: ['AZIM_TRUE',    {0: 'Planned', 1: 'Surveyed',        2: 'Back-calculated', 3: 'Calculated from AZ_MAGN', }],
                     8: ['AZIM_GRID',    {0: 'Planned',                       2: 'Back-calculated', 3: 'Calculated from AZ_MAGN', 4: 'Calculated from AZ_TRUE', }],
                     9: ['AZIM_UNKN',    {5: 'Unknown AZ reference', }],
                    10: ['AZIM_NONE',    {0: 'Not surveyed', }],
                    }

### table 12: MTTYPEID: Measurement Tool Type 
dictMTTYPEID      = {1: 'Magnetic',    2: 'Gyro',     3: 'Inertial',   4: 'Inclination only',      5: 'Utility', }

### Attributes table 13 (dict can be extended by user)
#dictATTID         = {1: 'Original File Name',  2: 'Superseded File Name',   3: 'Legacy File Name', }

### Measurement Type Attributes  # table 15
#dictMTATTID       = {
#                 1: 'Data Retrieval',               
#                 2: 'Measurement Trigger',            
#                 3: 'Collar RPM Low Trigger Threshold',
#                 4: 'Flow Trigger Threshold',       
#                 5: 'Trigger Measurement Time Delay', 
#                 6: 'Measurement Time Duration',
#                 7: 'Tool Distance Reference Name', 
#                 8: 'Time Reference',                 
#                 9: 'Battery Powered',
#                10: 'Offset from bit',
#                11: 'Non-magnetic spacing above the magnetic sensor', 
#                12: 'Non-magnetic spacing below the magnetic sensor',
#                13: 'Magnetic field intensity at top of steel below the non-magnetic spacing',
#                14: 'Magnetic field intensity at bottom of steel above the non-magnetic spacing',
#                }

### table 13: WELL Postion Objects
### shortname = dictWOBJTYPEID[2][0] # returns "WRP"
### fullname  = dictWOBJTYPEID[2][1] # returns "Well Reference Point"
dictWOBJTYPEID    = {
                 1: ['SRP', 'Structure Reference Point'],
                 2: ['WRP', 'Well Reference Point'],
                 3: ['ZDP', 'Zero-Depth Point'],
                 4: ['PC',  'Platform Centre'],
                 5: ['DFC', 'Drill Floor Centre'],
                 #6: ['SL',  'Slot'], # same as WRP, user defined name SLOT Y = WRP
                 6: ['GL',  'Ground Level'],
                 7: ['SF',  'Sea Floor'],
                 8: ['D',   'Surveyed Data Point'],  # as used in p7/2000
                 9: ['CP',  'Casing Point'],
                10: ['TP',  'Tie-in Point'],
                11: ['KOP', 'Kick Off Point'],
                12: ['FT',  'Formation Top'],
                13: ['PP',  'Reservoir Penetration Point'],
                14: ['PERF','Perforation Point'],
                15: ['BHL', 'Bottom Hole Location'],
                }

### table 14: Well Position Object Attributes. Can be user extended starting from 100 onward.
dictWOBJATTID     = {
                 1: 'Land Positioning Method',
                 2: 'Marine Positioning Method',
                 3: 'Date Positioned',
                 4: 'Coordinate QC Status', 
                }

### table 18: Wellbore Observables (MDINCAZ) status.  Can be user extended starting from 100 onward.				
dictWOBSSTATUS    = {
                 0: ['Surveyed'],
                 1: ['Surveyed'],
                 2: ['Planned'],
                 3: ['INC Interpolated'],
                 4: ['AZ Interpolated'],
                 5: ['INC and AZ Interpolated'],
                 6: ['Projected'],
                 7: ['Trended'],
                 8: ['INC and AZ back-calculated'],
                 9: ['Other'],
                } # table 21

### table 15: O7 and P7 standard Extension Field Identifiers; essentially column headers.
### dictP7ExtensionFieldID[i][0] is the data field column header
### dictP7ExtensionFieldID[i][1] is the additional parameter
### dictP7ExtensionFieldID[i][2] is the data field column unit (for now as string, could change this to use a key to dictUNIT)
dictP7ExtensionFieldID   = {
                 1: ['var_N',         0,   'unit_to_be_set'],  # square of unit of N in projected CRS
                 2: ['var_E',         0,   'unit_to_be_set'],  # square of unit N
                 3: ['var_D',         0,   'unit_to_be_set'],  # square of unit D
                 4: ['cov_NE',        0,   'unit_to_be_set'],  # square of unit N
                 5: ['cov_ND',        0,   'unit_to_be_set'],  # unit N * unit D
                 6: ['cov_ED',        0,   'unit_to_be_set'],  # unit N * unit D
                 7: ['AZ_MAGN',       0,   'deg'],
                 8: ['AZ_TRUE',       0,   'deg'],
                 9: ['AZ_GRID',       0,   'deg'],
                10: ['Conv.',         0,   '-'],
                11: ['sf',            0,   '-'],
                12: ['ef',            0,   '-'],
                13: ['csf',           0,   '-'],
                14: ['Decl.',         0,   'deg'],
                15: ['Dip',           0,   'deg'],
                16: ['Btot',          0,   'nT'],
                17: ['magn date',     0,   'YYYY:MM:DD'],
                18: ['dogleg',        0,   'unit_to_be_set'],
                19: ['build rate',    0,   'unit_to_be_set'],
                20: ['turn rate',     0,   'unit_to_be_set'],
                21: ['tangent',       0,   'deg'],
                22: ['course length', 0,   'unit_to_be_set'],
                23: ['tortuisity',    0,   'unit_to_be_set'],
                24: ['closure dist',  0,   'unit_to_be_set'],
                25: ['vert section',  0,   'unit_to_be_set'], # additional parameter has the azimuth 
                26: ['comment',       0,   ''],
                27: ['UTC',           0,   'YYYY:MM:DD:HH:MM:SS.ss'],
                }

                



#####################################################################
### Common Header
#####################################################################

### RecordID                                 #  Identifier                                           # Asterisks indicates object constructor row
### --------------------------------------------------------------------------------------------------------------------------
rec_IOGP_File_Identification_Record          = ('IOGP',)                                             #  mandatory first line (NB: comma at end makes it a tuple)

### Units of Measure (do not expect these to be in the file. Unless user-defined or full explicit definition copy from mandatory order.
rec_Unit_Of_Measure_Definition               = ('HC','1','1','0', 'Unit of Measure')                 # *UNITREF
rec_Example_Unit_Conversion                  = ('HC','1','1','1', 'Example Unit Conversion')

### Coordinate Reference System
rec_CRS_Implicit_Identification              = ('HC','1','3','0', 'CRS Number/EPSG Code/Name/Source')# *CRSREF (implicit def)
rec_CRS_Details                              = ('HC','1','4','0', 'CRS Number/EPSG Code/Type/Name')  #  explicit definition
#rec_Compound_CRS_Horizontal_Identification   = ('HC','1','4','1', 'Compound Horizontal CRS')         #
#rec_Compound_CRS_Vertical_Identification     = ('HC','1','4','2', 'Compound Vertical CRS')           #
rec_Base_Geographic_CRS_Details              = ('HC','1','4','3', 'Base Geographic CRS')             #
rec_Geodetic_Datum_Details                   = ('HC','1','4','4', 'Geodetic Datum')                  #
rec_Prime_Meridian_Details                   = ('HC','1','4','5', 'Prime Meridian')                  #
rec_Ellipsoid_Details                        = ('HC','1','4','6', 'Ellipsoid')                       #
rec_Vertical_Datum_Details                   = ('HC','1','4','7', 'Vertical Datum')                  #
#rec_Engineering_Datum_Details                = ('HC','1','4','8', 'Engineering Datum')               #

rec_Map_Projection_Details                   = ('HC','1','5','0', 'Map Projection')                  #
rec_Projection_Method_Details                = ('HC','1','5','1', 'Projection Method')               #  
rec_Projection_Parameter_Details             = ('HC','1','5','2', '{ProjectionParameterName}')       #  <-- replace with EPSG name

rec_Coordinate_System_Details                = ('HC','1','6','0', 'Coordinate System')               #
rec_Coordinate_Axis_Details                  = ('HC','1','6','1', 'Coordinate System Axis {AxisNumber}') # rec(4).format(AxisNumber=int(row(6))) using field 7
rec_Coordinate_Axis_Conversion_Applied       = ('HC','1','6','2', 'Coordinate Axis Conversion Applied')  # new CH record for P7/17 format

### Coordinate Transformation
rec_CT_Implicit_Identification               = ('HC','1','7','0', 'Transformation Number/EPSG Code/Name/Source')  # *COTRANSREF
rec_CT_Explicit_Definition                   = ('HC','1','8','0', 'Transformation Number/EPSG Code/Name')  #
rec_CT_Details                               = ('HC','1','8','1', 'Source CRS/Target CRS/Version')   #
rec_CT_Method_Details                        = ('HC','1','8','2', 'Transformation Method')           #
rec_Transformation_Parameter_File_Details    = ('HC','1','8','3', '{CTParameterName}')               #  <-- replace with EPSG name
rec_Transformation_Parameter_Details         = ('HC','1','8','4', '{CTParameterName}')               #  <-- replace with EPSG name

rec_Example_Point_Conversion                 = ('HC','1','9','0', 'Example Point Conversion')        #


#####################################################################
### Comment records
#####################################################################
rec_Additional_Information                   = ('CC','0','0','0')                                    #  Comment record
rec_Additional_Information_C7                = ('C7',)                                               #  <-- Context comment. Must be followed by "i,j,k, text"


#####################################################################
### P7 Specific Header
#####################################################################
rec_Project_Information                      = ('H7','1','0','0', 'Project Information')             #  mandatory
rec_Structure_Definition                     = ('H7','1','1','0', 'Structure Definition')            # *STRUCTUREREF
rec_Structure_Details                        = ('H7','1','1','1', 'Structure Details')               #  mandatory
rec_Well_Definition                          = ('H7','1','2','0', 'Well Definition')                 # *WELLREF
rec_Well_Details                             = ('H7','1','2','1', 'Well Details')                    #  mandatory
rec_Positioning_Contractor                   = ('H7','1','2','2', 'Land/Marine Positioning Contractor') #  optional
rec_Wellbore_Definition                      = ('H7','1','3','0', 'Wellbore Definition')             # *WELLBOREREF
rec_Rig_Definition                           = ('H7','1','4','0', 'ZDP Rig/Workover Definition')     # *ZDPREF
rec_Survey_Definition                        = ('H7','1','5','0', 'Survey Definition')               # *SURVEYREF
rec_Survey_Details                           = ('H7','1','5','1', 'Survey Details')                  #  mandatory
rec_Operator_Survey_Contractor               = ('H7','1','5','2', 'Operator/Survey Contractor')      #  optional

rec_Measurement_Tool_Definition              = ('H7','2','0','0', 'Measurement Tool Definition')     #
rec_Geomagnetic_Model_Definition             = ('H7','3','0','0', 'Geomagnetic Model Definition')    #  mandatory for MWD
rec_Gravity_Model_Definition                 = ('H7','3','1','0', 'Gravity Model Definition')        #  mandatory if raw data is included in the file
rec_Position_Object_Definition               = ('H7','4','0','0', 'Position Object Definition')      # *WOBJREF; WOBJTYPEREF: full name of point, e.g. 'Well Reference Point';
rec_Position_Object_Attribute                = ('H7','4','1','0', '{WobjAttRefName}')                #  See table WOBJATTREF lookup;

### P7 Table
rec_P7_Table_Definition                      = ('H7','5','0','0', 'P7 Table Definition')                # *P7TABLEREF

### P7 Specific Header: Error Model
rec_Survey_Tool_Error_Model_Definition       = ('H7','6','0','0', 'Survey Tool Error Model Definition') # *STEMREF
rec_Survey_Tool_Error_Model_Metadata         = ('H7','6','1','0', 'Survey Tool Error Model Metadata')   #  
rec_Survey_Tool_Error_Model_Terms            = ('H7','6','2','0', 'Survey Tool Error Model Terms')      #  

### Raw Sensor Data (extended fields)
rec_M7_Record_Extension_Definition           = ('H7','7','0','0', 'M7 Record Extension Field Definition') #  mandatory if M7 records contain additional data
rec_G7_Record_Extension_Definition           = ('H7','7','1','0', 'G7 Record Extension Field Definition') #  mandatory if G7 records contain additional data


#####################################################################
### P7 Data Records (note: comma after string to ensure it is defined as a tuple)
#####################################################################
rec_O7_Position_Record                       = ('O7',)                                            #  details to be appended for WOBJ
rec_P7_Data_Record                           = ('P7',)                                            #  refers to a SURVEYREF and P7TABLEREF
rec_M7_MWD_Raw_Sensor_Data_Record            = ('M7',)                                            #  refers to a SURVEYREF
rec_G7_Gyro_Raw_Sensor_Data_Record           = ('G7',)                                            #  refers to a SURVEYREF



#####################################################################
### dict_record_spec {}
### Store information in this dict to use later.
### Bert Kampes, 2018-08-10
#####################################################################
#
# intended usage: fill the values; then iterate over keys and check if values are >0
# Also used to check presence of mandatory records, and correct record lengths
# Also used to format output
#
#   cnt: Number of found records in the file.  Caller function updates the counter.  Note this should be initialized to 0 before calling the function.
#   tuple(min,max,fmt, requires): i.e., an unmutable containing
#     min_required: if min_required>0 then this is a mandatory record
#     max_expected: number of max. records expected in the p717
#     rec_fmt:      e.g., '{},{},{},{},{:<40},{:d},{:d},{},{:d},{},{:d}'  # use standard python3 format modifiers
#                                             {BLANK:d},{BLANK:f}         # use "BLANK" to indicate field may be blank (e.g., EPSG code)
#     requires:     a list of recordsIDs that are required if this record is defined in the p717 (dependents)
#
### Example how to use this dict:
#>>> rec_Coordinate_System_Details = ('HC','1','6','0', 'Coordinate System')
#>>> dict_record_spec[rec_Coordinate_System_Details][0] = counter #update record counter
#>>> min_required = dict_record_spec[rec_Coordinate_System_Details][1][0]
#>>> max_expected = dict_record_spec[rec_Coordinate_System_Details][1][1]
#>>> rec_fmt      = dict_record_spec[rec_Coordinate_System_Details][1][2]
#>>> num_fields   = len(rec_fmt.split(","))
#>>> list_dependents = dict_record_spec[rec_Coordinate_System_Details][1][3] # if record was given, then check if these are also there with cnt>0
#>>> for dependency in list_dependents: print (dependency)
#
### Note: following does not work if variables are string! Python does not seem to format a str as %d, has to be int or explicit cast to int.
#>>> rec_fmt        = '{},{},{},{},{:<40},{:d},{:d},{},{:d},{},{:d}'
#>>> f1,f2,f3,f4,f5 = rec_Coordinate_System_Details
#>>> f6 = 1
#>>> f7=6422
#>>> f8="Ellipsoidal 2D CS"
#>>> f9=3
#>>> f10="Ellipsoidal"
#>>> f11=2
#>>> outrec = rec_fmt.format(f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11)
#>>> print(outrec)
#HC,1,6,0,Coordinate System                       ,1,6422,Ellipsoidal 2D CS,3,Ellipsoidal,2
###
#------------------------------------------------------------------------------------------------------------------------------
#                                                   cnt, min_req,max_expexted,  format,       list_of_dependent_records (if this then also)
#------------------------------------------------------------------------------------------------------------------------------
dict_record_spec = {
    rec_IOGP_File_Identification_Record:             [0, (1,    1,'{},{},{},{:f},{:d},{},{},{},{}', () )],

    ### Units of Measure (should not be there as it is implicit in the p7/17)
    rec_Unit_Of_Measure_Definition:                  [0, (0,   50,'{},{},{},{},{:<50},{:d},{},{},{:d},{BLANK:d},{BLANK:f},{BLANK:f},{BLANK:f},{BLANK:f},{},{BLANK:d},{},{},{}', 
        (rec_Example_Unit_Conversion, ) )],
    rec_Example_Unit_Conversion:                     [0, (0,   50,'{},{},{},{},{:<50},{:d},{:d},{}', () )],

    ### Coordinate Reference System: assume at least projCRS, geogCRS, vertCRS, and probably WGS 84
    ### Tests of dependencies should be done in more detail when objects are constructed.
    rec_CRS_Implicit_Identification:                 [0, (4,   9,'{},{},{},{},{:<50},{:d},{BLANK:d},{},{},{},{},{}',  () )],
    rec_CRS_Details:                                 [0, (0,   50,'{},{},{},{},{:<50},{:d},{BLANK:d},{:d},{},{}', () )],
    #rec_Compound_CRS_Horizontal_Identification:      [0, (0,   10,'{},{},{},{},{:<50},{:d},{:d},{BLANK:d},{}', () )],
    #rec_Compound_CRS_Vertical_Identification:        [0, (0,   10,'{},{},{},{},{:<50},{:d},{:d},{BLANK:d},{}', () )],
    rec_Base_Geographic_CRS_Details:                 [0, (0,   10,'{},{},{},{},{:<50},{:d},{:d},{:d},{}',               # required for projected; and projected is required
        (rec_Geodetic_Datum_Details, ) )], 
    rec_Geodetic_Datum_Details:                      [0, (0,   10,'{},{},{},{},{:<50},{:d},{:d},{},{}', 
        (rec_Prime_Meridian_Details, rec_Ellipsoid_Details, ) )],
    rec_Prime_Meridian_Details:                      [0, (0,   10,'{},{},{},{},{:<50},{:d},{:d},{},{},{:d},{}', () )],  # very unlikely to be more than 1, but repeated for each CRS...
    rec_Ellipsoid_Details:                           [0, (0,   10,'{},{},{},{},{:<50},{:d},{:d},{},{:f},{:d},{},{:f}', () )],
    rec_Vertical_Datum_Details:                      [0, (0,   10,'{},{},{},{},{:<50},{:d},{:d},{}', () )],
    #rec_Engineering_Datum_Details:                   [0, (0,   10,'{},{},{},{},{:<50},{:d},{BLANK:d},{}', () )],

    rec_Map_Projection_Details:                      [0, (0,   10,'{},{},{},{},{:<50},{:d},{:d},{}', () )],
    rec_Projection_Method_Details:                   [0, (0,   10,'{},{},{},{},{:<50},{:d},{:d},{},{:d}', () )],
    rec_Projection_Parameter_Details:                [0, (0,   50,'{},{},{},{},{:<50},{:d},{:d},{},{:d},{}', () )],     #CRSREF, EPSG, UNITREF

    rec_Coordinate_System_Details:                   [0, (0,   50,'{},{},{},{},{:<50},{:d},{BLANK:d},{},{:d},{},{:d}',       #CRSREF, EPSG, CRSTYPEREF, dim
        (rec_Coordinate_Axis_Details, ) )],
    rec_Coordinate_Axis_Details:                     [0, (0,   50,'{},{},{},{},{:<50},{:d},{:d},{BLANK:d},{},{},{},{:d},{}', () )],
    rec_Coordinate_Axis_Conversion_Applied:          [0, (0,   50,'{},{},{},{},{:<50},{:d},{:d},{},{:d},{}', () )],	
	
    ### Coordinate Transformation (not mandatory, e.g., if data are in WGS 84)
    rec_CT_Implicit_Identification:                  [0, (0,   10,'{},{},{},{},{:<50},{:d},{BLANK:d},{},{},{},{},{}', () )],
    rec_CT_Explicit_Definition:                      [0, (0,   10,'{},{},{},{},{:<50},{:d},{BLANK:d},{},{}', 
        (rec_CT_Implicit_Identification, rec_CT_Details, rec_CT_Method_Details, ) )], #
    rec_CT_Details:                                  [0, (0,   10,'{},{},{},{},{:<50},{:d},{:d},{BLANK:d},{},{:d},{BLANK:d},{},{}', 
        (rec_CT_Implicit_Identification, rec_CT_Explicit_Definition, rec_CT_Method_Details, ) )], #
    rec_CT_Method_Details:                           [0, (0,   10,'{},{},{},{},{:<50},{:d},{:d},{},{:d},{:d}',
        (rec_CT_Implicit_Identification, rec_CT_Explicit_Definition, rec_CT_Details, ) )], #
    rec_Transformation_Parameter_File_Details:       [0, (0,   20,'{},{},{},{},{:<50},{:d},{:d},{},{:d}', 
        (rec_CT_Implicit_Identification, rec_CT_Explicit_Definition, rec_CT_Details, rec_CT_Method_Details, ) )],
    rec_Transformation_Parameter_Details:            [0, (0,  100,'{},{},{},{},{:<50},{:d},{:d},{},{:d},{},{:d}', 
        (rec_CT_Implicit_Identification, rec_CT_Explicit_Definition, rec_CT_Details, rec_CT_Method_Details, ) )],
    rec_Example_Point_Conversion:                    [0, (0,   10,'{},{},{},{},{:<50},{:d},{},{:d},{},{},{}', 
        (rec_CT_Implicit_Identification, ) )], # recommended

    ### Comment records: no need to check/format variable fields
    rec_Additional_Information:                      [0, (0,90000,'{},{},{},{},{}', () )], # 5 fields, ignore comma's in comments 
    rec_Additional_Information_C7:                   [0, (0,90000,'{},{},{},{},{}', () )], # 5 fields, ignore comma's in comments 

    ### P7 Specific Header
    rec_Project_Information:                         [0, (1,    1,'{},{},{},{},{:<50},{},{},{},{},{}', () )],
    rec_Structure_Definition:                        [0, (1,10000,'{},{},{},{},{:<50},{:d},{},{},{:d},{},{}', 
        (rec_Project_Information, rec_Structure_Details, ) )],
    rec_Structure_Details:                           [0, (1,10000,'{},{},{},{},{:<50},{:d},{},{BLANK:.2f},{BLANK:.2f},{},{BLANK:d},{},{BLANK:.3f}', () )],
    rec_Well_Definition:                             [0, (1,10000,'{},{},{},{},{:<50},{:d},{:d},{},{:d},{},{},{},{},{},{},{},{},{}', 
        (rec_Structure_Definition, rec_Well_Details, ) )],
    rec_Well_Details:                                [0, (1,10000,'{},{},{},{},{:<50},{:d},{},{},{},{BLANK:f},{BLANK:d}, {BLANK:.2f},{BLANK:.2f}', 
        (rec_Position_Object_Definition, rec_O7_Position_Record, ) )], #WRP dependency
    rec_Positioning_Contractor:                      [0, (0,   50,'{},{},{},{},{:<50},{:d},{},{}', () )],
    rec_Wellbore_Definition:                         [0, (1,50000,'{},{},{},{},{:<50},{:d},{:d},{},{},{},{},{},{},{},{},{}', 
        (rec_Well_Definition, ) )],
    rec_Rig_Definition:                              [0, (1,10000,'{},{},{},{},{:<50},{:d},{},{},{:.1f},{BLANK:.1f},{BLANK:.1f},{},{BLANK:d},{BLANK:d}', 
        (rec_Structure_Definition, ) )],
    # field 11 may be a list of integers (e.g., for survey with Gyro&MWD); here error check done only for single 
    rec_Survey_Definition:                           [0, (1,50000,'{},{},{},{},{:<50},{:d},{:d},{:d},{},{},{BLANK:d},{},{},{},{:.2f},{:.2f},{},{},{}, ' +
																	'{},{BLANK:d},{BLANK:.2f},{BLANK:d}', 
        (rec_Rig_Definition, rec_Survey_Details, ) )],
    rec_Survey_Details:                              [0, (1,50000,'{},{},{},{},{:<50},{:d}, {:d},{:d},{},{:d},{}, {:d}, {:d},{},{:d},{}, ' +
                                                                    '{:d},{BLANK:.3f}, ' +
                                                                    '{:d},{BLANK:.3f},{}, {BLANK:d},{BLANK:d}', () )],
    rec_Operator_Survey_Contractor:                  [0, (0,   50,'{},{},{},{},{:<50},{:d},{},{},{}', () )],
   
    
    ### Measurement Tool
    rec_Measurement_Tool_Definition:                 [0, (0,10000,'{},{},{},{},{:<50},{:d},{},{:d},{},{},{},{BLANK:.2f}', () )],

    ### Reference models
    rec_Geomagnetic_Model_Definition:                [0, (0,   10,'{},{},{},{},{:<50},{:d},{},{},{},{}', () )],
    rec_Gravity_Model_Definition:                    [0, (0,10000,'{},{},{},{},{:<50},{:d},{}', () )],

    ### Position Object
    rec_Position_Object_Definition:                  [0, (1,10000,'{},{},{},{},{:<50},{:d},{},{:d},{},{},{BLANK:d},{BLANK:.2f}, ' +
																	'{BLANK:.2f},{BLANK:.2f},{BLANK:.2f},{BLANK:.2f},{BLANK:.2f}', () )], #added 6/23/2019 TBD
    rec_Position_Object_Attribute:                   [0, (0,50000,'{},{},{},{},{:<50},{:d},{:d},{},{BLANK:d},{}', () )],

    ### P7 Table.  Note record may contain additional fields at end if there are extension fields defined.
    rec_P7_Table_Definition:                         [0, (1,   50,'{},{},{},{},{:<50},{:d},{},{:d},{},{:d},{},{:d},{BLANK:.5f},{:d},{:d},{}', () )],

    ### Error Model (if OWSG model then implicit definition by next, otherwise all explicit)
    rec_Survey_Tool_Error_Model_Definition:          [0, (0,   50,'{},{},{},{},{:<50},{:d},{},{},{}', () )],
    rec_Survey_Tool_Error_Model_Metadata:            [0, (0,   50,'{},{},{},{},{:d},{:d},{},{}',
        (rec_Survey_Tool_Error_Model_Definition, rec_Survey_Tool_Error_Model_Terms, ) )],
    rec_Survey_Tool_Error_Model_Terms:               [0, (0,   50,'{},{},{},{},{:<50},{:d},{:d},{},{},{},{},{},{:f},{},{},{},{},{},{},{},{},{},{},{},{}',
        (rec_Survey_Tool_Error_Model_Definition, rec_Survey_Tool_Error_Model_Metadata, ) )],

    ### Raw Measurements (mandatory if field extension used)
    rec_M7_Record_Extension_Definition:              [0, (0,   50,'{},{},{},{},{:<50}{:d},{:d},{}', () )],
    rec_G7_Record_Extension_Definition:              [0, (0,   50,'{},{},{},{},{:<50}{:d},{:d},{}', () )],
        
    ### Data Records (note: the last field may be empty, filled, or separated with semi-columns for more than 1 extension field)
    ### O7 does not have extension fields
    rec_O7_Position_Record:                          [0, (1,  50000,'{},{:d},{:d},{},{},{BLANK:.2f},{BLANK:.2f},{BLANK:.2f}, {BLANK:.7f},{BLANK:.7f}, ' +
                                                                    '{BLANK:.7f},{BLANK:.7f}, {BLANK:.2f},{BLANK:.2f}', () )],
    rec_P7_Data_Record:                              [0, (2,5000000,'{},{:d},{:d},{:d},{:d},{},{:d},{},{:d},{}, {:.2f},{:.2f},{:.2f}, ' + 
                                                                    '{BLANK:.2f},{BLANK:.2f},{BLANK:.2f}, {BLANK:.2f},{BLANK:.2f},{BLANK:.2f}, ' +
                                                                    '{BLANK:.7f},{BLANK:.7f},{}', () )],
    rec_M7_MWD_Raw_Sensor_Data_Record:               [0, (0,5000000,'{},{:d},{:d},{:d},{},{:d},{:d}, {:f},{:f},{:f}, {:f},{:f},{:f}, ' +
                                                                    '{:f},{:f},{:f}, {:f},{:f},{:f},' + 
                                                                    '{:f},{:f}, {:f},{:f},{:f}, {:f},{:f},{:f}, {:f},{:f}, {}',
                                                                    (rec_P7_Data_Record, ) )],
    rec_G7_Gyro_Raw_Sensor_Data_Record:              [0, (0,5000000,'{},{:d},{:d},{:d},{},{:d}, {:f},{:f},{:f}, {:f},{:f},{:f}, {:d},' +
                                                                    '{:f},{:f},{:f}, {:f},{:f},{:f},' +
                                                                    '{:f},{:f},{:f}, {:f},{:f}, {:f},{:f},{:f}, {:f}, {}', 
                                                                    (rec_P7_Data_Record, ) )],
    }



#####################################################################
### Helper functions to check, read, write data records.
### Also see p717classes for constructors using rows of data indicated with asterisk
#####################################################################


###########################################################
### i =  safe_cast_to_int(row,index)
###
### Save cast to integer, to avoid crash if file not even has REF.  
### Prefer to completely parse p717 file once and report all issues then just the first error.
###
### Intended to rewrite code like:
###   key = int(row[5])
###   logging.debug("Found UoM UNITREF:                         %s", key) 
###   dictUNIT[key]=UNITOFMEASURE(row) #create object with constructor
### to
###   key = get_ref(row,field)
###   if key>0: dictUNIT[key]=UNITOFMEASURE(row)
### where row is read by csv reader from p717 file, e.g.,
###   row   = ['HC', '1', '7', '0', 'Transform Implicit Identification', '[6]', '[7]', '[8]', '[9]', '[10]', '[11]', '[12]']
###   index = 5 (starting at 0, i.e., record field #6 has index 5)
### Return integer key or -999 if failed to cast string to integer.  In above example with '[6]' as input it returns -1.
###
### Bert Kampes, 2018-01-17
###########################################################
def safe_cast_to_int(row, index):
    val = -999 #(needs a value to write cannot write "None" as :d)
    try:
        val = int(row[index]) # try to cast to an integer.  Note this can also fail if index is too large.
    except: 
        if index>=len(row):
            logging.error("Issue with record: %s", row)
            logging.error("Field %s: but row has only %s fields", index+1, len(row))
        else:
            if row[index].strip()!='':
                logging.error("Field %s: I found \"%s\", but expected an Integer", index+1, row[index].strip())
    return val

    

#####################################################################
### Safe cast to float
### For a field read in as ascii string
### Bert Kampes, 2018-08-10
#####################################################################
def safe_cast_to_float(row, index):
    val = -99999. #(needs a value to write cannot write "None" as :f).
    try:
        val = float(row[index]) # try to cast to an float.  Note this can also fail if index is too large.
    except: 
        if index>=len(row):
            logging.error("Issue with record: %s", row)
            logging.error("Field %s: but row has only %s fields", index+1, len(row))
        else:
            if row[index].strip()!='':
                logging.error("Field %s: I found \"%s\", but expected a Float", index+1, row[index].strip())
    return val


    
#####################################################################
### Reset counter of mandatory records
### Bert Kampes, 2018-08-10
#####################################################################
def reset_record_counters():
    logging.info("")
    logging.info("Checking existence of mandatory records in p717 file")
    logging.info("Following list may not be complete:")
    for key in dict_record_spec:
        dict_record_spec[key][0] = 0 # set record counter to zero
        min_required = dict_record_spec[key][1][0]
        if min_required>0:
            logging.info("  %s", key)
    logging.info("")



#####################################################################
### report_records_check
### Check existence of mandatory records and dependent records.
### Requires logging to be defined in caller.
### Bert Kampes, 2018-08-10
#####################################################################
def report_records_check():
    for key in dict_record_spec:
        count        = dict_record_spec[key][0]
        min_required = dict_record_spec[key][1][0]
        max_allowed  = dict_record_spec[key][1][1]
                
        ### Report out if issue found.  Mandatory records have a min_required>0 in the dict_record_spec:
        if count<min_required:
            logging.error("Issue with mandatory record: %s", key)
            logging.error("  Number of records found: %s", count)
            logging.error("  Minimum number expected: %s", min_required)
            logging.error("")
        if count>max_allowed:
            logging.warning("Issue with record: %s", key)
            logging.warning("  Number of records found: %s", count)
            logging.warning("  Maximum number expected: %s", max_allowed)
            logging.warning("")
            
        ### Check dependents
        if count>0:
            dependents_list = dict_record_spec[key][1][3]
            for dependency in dependents_list:
                dependency_count = dict_record_spec[dependency][0]
                if dependency_count<1:
                    logging.error("For found record: %s", key)
                    logging.error("  Issue with dependent record: %s", dependency)
                    logging.error("  Number of dependent records found: %s", dependency_count)
                    logging.error("")

                    
                    
#####################################################################
### result = is_record(row, p17record)
###
### p7recordID is a tuple with the record identification fields, e.g., ['P7','1','0','0']
###   possibly followed by a record description (e.g., "Field Name"), except if single ID (e.g., C7, P7, etc.)
### row is a list of strings read with csv.reader().
###
### Returns True if row contains the p7recordID, False otherwise.
###
### Bert Kampes 2017-12-23
#####################################################################
def is_record(row, p7recordID):
    
    ### coding check: make sure comparison between list and tuple works.  This function assumes a list and tuple as input.
    if type(p7recordID)!=tuple: #type(tuple('dummy')):
        logging.error("Something wrong with expected input. p7recordID \"%s\" should be a tuple", p7recordID)
        logging.error("This cannot happen...")
        exit()
    if type(row)!=list: #type(list('dummy')):
        logging.error("row: %s", row)
        logging.error("Something wrong with expected input. Row should be a list. This should never happen...")
        exit()

    ### Check if comparison record has only 1 element
    match = False
    n     = len(p7recordID)
    if n==1:
        if tuple(row[:1])==p7recordID: # note, the syntax [:1] also deals with empty rows containing no elements
            match = True
            logging.debug("Found record %s", p7recordID)
    ### Else deal with case of 4 or 5 elements in p7recordID
    elif n>=4:
        if tuple(row[:4])==p7recordID[:4]:
            match = True
            logging.debug("Found record %s", p7recordID)
            ### Cross-check field5 record descriptor if it is given as mandatory string in the format spec.
            check_record_descriptor(row, p7recordID)
    else:
        logging.error("unexpected situation - please check file p717records.py for %s", p7recordID)
        exit()

    ### Increase record counter and verify number of fields on this row
    if match==True:
        ### Update record counter
        dict_record_spec[p7recordID][0] += 1
        ### Check number of fields in the record and their format (Integer/Float)
        check_record_vs_spec(row, p7recordID)
    
    ### Return True or False
    return match



#####################################################################
### check_record_descriptor.  Called in is_record()
###
### Cross-check field descriptor (field 5) if it is given as mandatory string in the format spec.
### Deal with special cases (not all, e.g., EPSG names)
###
### Bert Kampes 2017-12-25
#####################################################################
def check_record_descriptor(row, p7recordID):
    ### Do the check, e.g., if row in p717 file contains "Wellbore Definition"
    if len(p7recordID)==5:
        expected_field5 = p7recordID[4]
        # Special case: string substitute axis number
        if p7recordID==rec_Coordinate_Axis_Details:
            expected_field5 = p7recordID[4].format(AxisNumber=safe_cast_to_int(row,6))               # put the axis number in the string
        # Special case: string substitute ATTREF (lookup name in dict using field 5)
        #elif p7recordID==rec_File_Contents_Attribute:
        #    try:    expected_field5 = p7recordID[4].format(AttRefName=ATTREF[int(row[5])])           # substitute string using ATTREF dict
        #    except: expected_field5 = p7recordID[4].format(AttRefName=row[4])                        # in case user defined: not in lookup table
        # Special case: string substitute ATTREF (lookup name in dict using field 5)
        #elif p7recordID==rec_Measurement_Tool_Attributes:
        #    try:    expected_field5 = p7recordID[4].format(MtAttRefName=MTATTREF[int(row[5])])       # substitute string using MTATTREF dict
        #    except: expected_field5 = p7recordID[4].format(MtAttRefName=row[4])                      # in case user defined: not in lookup table
        # Special case: string substitute WOBJATTREF (lookup name in dict).  Use field 8 for lookup.  Could also use field 9 for text.
        elif p7recordID==rec_Position_Object_Attribute:
            try:    expected_field5 = p7recordID[4].format(WobjAttRefName=WOBJATTREF[int(row[7])])   # substitute string using WOBJATTREF dict
            except: expected_field5 = p7recordID[4].format(WobjAttRefName=row[4])                    # in case user defined: not in lookup table
        ### Compare text from file with expected_field5 description
        if row[4].strip().lower()!=expected_field5.strip().lower():
            try:    logging.warning("Record: %s", row[:8]) # incl. the TYPEREF typically at field 8
            except: logging.warning("Record: %s", row[:5])
            logging.warning("I expected to see in field 5 the descriptor: \"%s\"", expected_field5)
            logging.warning("")
        else:
            logging.debug("Descriptor OK: \"%s\"", expected_field5)

                    
                    
#####################################################################
### Check number of fields in a record.  Called in is_record()
###
### Bert Kampes 2017-12-23
#####################################################################
def check_record_vs_spec(row, p7recordID):
    
    logging.debug("check_record_vs_spec: %s", row)
    ### Make sure comment records have 5 fields in case they had commas
    #if p7recordID in [rec_Additional_Information, rec_Additional_Information_C7]:
    #    row = row[:4]+','.join(list(row[4:])
    
    ### Get expected and actual number of fields
    this_record_format  = dict_record_spec[p7recordID][1][2] # e.g., '{},{},{},{:f},{:d},{},{},{},{}'
    num_fields_expected = len(this_record_format.split(","))
    num_fields_in_row   = len(row)
    
    ### Deal with special case for example conversions which can have more fields and extension record definitions!
    # Example Unit conversion
    if p7recordID==rec_Example_Unit_Conversion:
        logging.debug("Example unit conversion has variable fields, could be 10,12,14,.. (no time now to implement)")
        if num_fields_in_row==10: num_fields_expected=10
        if num_fields_in_row==12: num_fields_expected=12
    # Example Point Conversion
    if p7recordID==rec_Example_Point_Conversion:
        logging.debug("Example point conversion has variable fields, could be 15,19,23,.. (no time now to implement)")
        if num_fields_in_row==19: num_fields_expected=19 
        if num_fields_in_row==23: num_fields_expected=23 
        if num_fields_in_row==27: num_fields_expected=27

    # MWD raw data extension definition
    if p7recordID==rec_M7_Record_Extension_Definition:
        logging.debug("rec_M7G7_Record_Extension_Definition may have extension fields")
        num_extension_fields = safe_cast_to_int(row, 6)
        if num_extension_fields>0:
            num_fields_expected += (num_extension_fields-1) # NB. one extension field is there - silly definition
    # Gyro raw data extension definition
    if p7recordID==rec_G7_Record_Extension_Definition:
        logging.debug("rec_M7G7_Record_Extension_Definition may have extension fields")
        num_extension_fields = safe_cast_to_int(row, 6)
        if num_extension_fields>0:
            num_fields_expected += (num_extension_fields-1) # NB. one extension field is there - silly definition

    # P7 def extension fields
    if p7recordID==rec_P7_Table_Definition:
        logging.debug("rec_P7_Table_Definition may have extension fields")
        num_extension_fields = safe_cast_to_int(row, 15)
        if num_extension_fields>0:
            num_fields_expected += (num_extension_fields-1) # NB. one extension field is there - silly definition
    
    ### Debug info
    logging.debug("Record fmt: %s", this_record_format)
    logging.debug("Expected vs. Actual number of fields: %i <> %i", num_fields_expected, num_fields_in_row)


    ### Check found number of fields against expected number
    if num_fields_in_row<num_fields_expected:
        logging.error("Issue with record: %s", row)
        logging.error("Not enough fields in record. Found %s, expected %s", num_fields_in_row, num_fields_expected)
        logging.error("")
    if num_fields_in_row>num_fields_expected:
        if p7recordID not in [rec_Additional_Information, rec_Additional_Information_C7]: # ignore comment records, could do: row=CC[:4]+','.join(CC[4:]
            logging.error("Issue with record: %s", row)
            logging.error("Too many fields in record. Found %s, expected %s", num_fields_in_row, num_fields_expected)
            logging.error("")

    ### Try to check format of the variable fields by formatting the fields as given
    ### hmmm... that does not work for record read from csv file because they are read as strings, so explicitly trying to cast...
    field_counter = 0
    for this_field_format in this_record_format.split(","):
        field_counter += 1
        do_test = True
        if 'd' in this_field_format:
            # Check for empty field (e.g., EPSG code not defined, may be blank). This is specified in given format on top of this file
            if field_counter<=num_fields_in_row: #  avoid error if a row would not have enough fields for some reason
                if row[field_counter-1].strip()=="":
                    if "BLANK" in this_field_format:
                        do_test=False
                    # additional exceptions can be added here, e.g.,
                    #if p7recordID==rec_Unit_Of_Measure_Definition:        do_test=False # too flexible to test
            if do_test==True:
                dummy = safe_cast_to_int(row,field_counter-1) # this function does the error logging.

        elif 'f' in this_field_format:
            if field_counter<=num_fields_in_row: # special case if row would not have enough fields
                if row[field_counter-1].strip()=="" or row[field_counter-1].strip()=="N/A":
                    if "BLANK" in this_field_format:
                        do_test=False
                    #if p7recordID==rec_Unit_Of_Measure_Definition:   do_test=False # too flexible to test
            if do_test==True:
                dummy = safe_cast_to_float(row,field_counter-1) # this function does the error logging.

        ### Report debug to logfile if blank found but ignored.
        if do_test==False:
            logging.debug("Found blank for field %s in record %s", field_counter, p7recordID)
            logging.debug("This is possible, e.g., if EPSG code is not available")

 
### EOF.



