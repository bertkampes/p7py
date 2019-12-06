#########################################################################################
### p717classes.py
###
### Defines classes for main entities (REFs) in p717 file format.
###    CRS          : Coordinate Reference System
###    CT           : Coordinate Transformation
###    WOBJ         : Well Position Object
###    PROJECT      : Metadata about the project
###    STRUCTURE    : The site or structure the well is on
###    WELL         : The point where the wellbore enters the earth.
###    WELLBORE     : Starting at Well, into the earth.
###    RIG          : ZDP definition for the Rig used to drill.
###    SURVEY       : The borehole survey info and observables.  Contains most information.
###    P7TABLE      : The survey(s) and calculated values. Considered the main object but requires above entities.
###
### Additionally, it would be logically to define classes for
###    MTREF
###    GRAVREF
###    MAGREF
###    STEMREF counters.  These are currently simply put in a dict in the reader.
###
### This file is to be included in main program such as p717 reader/writer.
### It requires a logger to be initialized in the calling program before using the program (see sample reader program).
###
### v1: Based on draft v1 2019-11-05 of IOGP p717 format specification.
### See spec and user guide on www.iogp.org.
###
### This code is sample code, provided AS-IS with no warranty or guarantee for fitness or purpose whatsoever.
### Do with it whatever you want, but do not assume it to be correct.
###
### Bert Kampes, 2019-11-05
#########################################################################################

import datetime  # for IOGP record current time
import logging
### Get p717 record definitions from an include file by using import * (no namespace)
#from p717records import dict_record_spec, dictCRSTYPEREF, dictUNITREF, dictWOBSID, dictWOBJTYPEID, safe_cast_to_int, safe_cast_to_float
from p717records import *


# TO DO try if the following works (i.e., can I call a class function in the constructor - may have to put it first in the class?)
# * in each class, make a constructor that optionally takes a row=None as input
 # (I know there are more pythonic ways).
 # The row constructor is useful as it is used in reader program
 # * add all variables in the init list on top
 # * create a function that parses the constructor (definition) row (set_rec_something, e.g., set_rec_Project_Information)
 # * Call that function if a row is input; else only construct empty object and return
 # * create a new function in each class for "demo_fill" which will call the "set_rec_xxx()" functions to fill the class variables.
   # this uses a row hardcoded that is then used with the set function for that record.
 # * create a new function "Project.demo_write(CRS,CT,WELL,..)" which will call all set_xxx() functions and
   # then writes an output file (opens a file handler with fixed file name) by calling the "class write_xxx()" functions in right order
# BK 8/13/2018 - the above are quick notes as I have no time to try this...


################################################################################
### Reference system records
###   * Time systems not in p717
###   * Units are fixed in format spec (UNITREF) and can be included and user-defined (not recommended)
###   * So this is about geodetic definitions.  We use implicit definitions (EPSG codes) - careful with axes orientation and order!
################################################################################

#none

####################################################################
### COORDINATE REFERENCE SYSTEM
### for simplicity, include CS in the CRS here rather than modeling as separate class
### Note that in P7/17 the order of axes is always Northing, Easting, Depth - even quoting EPSG codes.
###
### Bert Kampes, 2018-08-17
####################################################################
class CRS:
    def __init__ (self, row): # constructor using row=rec_CRS_Implicit_Identification
        logging.debug("CRS CONSTRUCTOR: %s", row[:5])
        ### Initialize
        self.row             = row.copy()
        self.CS_dimension    = 0
        self.CS_axes_codes   = {}
        self.CS_axes_names   = {} #[1,2]     # dict axes name, e.g., key=1, value="Easting" (otherwise it starts with [0] in a list)
        self.CS_axes_orientations  = {}
        self.CS_axes_abbreviations = {}
        self.CS_axes_unitREFs      = {}
        self.CS_axes_units         = {} #1         # dict axes unit, e.g., key=1, value="metre"
        self.CS_axis_conversion_applied = None
        #
        self.CRS_type_code   = -1            # CRSTYPE[] -> e.g., geographic2D, projected, compound, etc.
        self.CRS_type        = None          # CRSTYPE[] -> e.g., geographic2D, projected, compound, etc.
        #
        self.CRSREF_hor      = None          # if compound, then set ref.
        self.CRS_epsg_hor    = None          # if compound
        self.CRS_name_hor    = None          # if compound
        self.CRSREF_vert     = None          # if compound, then set ref.
        self.CRS_epsg_vert   = None          # if compound
        self.CRS_name_vert   = None          # if compound

        ### Parse row
        self.CRSREF       = safe_cast_to_int(row,5)       # e.g., 1
        self.CRS_epsg     = safe_cast_to_int(row,6)
        self.CRS_name     = row[7].strip()   # remove leading and trailing spaces; e.g., 'NAD27 / UTM 15N'
        self.EPSG_version = row[8].strip()
        self.EPSG_date    = row[9].strip()
        self.EPSG_source  = row[10].strip()
        self.description  = row[11].strip()


    ### Set details
    def set_rec_CRS_details(self, row):
        logging.debug("CRS set details: %s", row[:5])
        key = safe_cast_to_int(row,5)
        if key != self.CRSREF:
            logging.critical("something went wrong that should never have gone wrong")
        #
        if row[6].strip().isdigit():         # EPSG code
            tmp_epsg = safe_cast_to_int(row,6)           # e.g., 26715
            if self.CRS_epsg>0:
                if self.CRS_epsg!=tmp_epsg:
                    logging.warning("CRSREF %s: EPSG code in CRS details: %s does not appear to be equal to implicit %s", self.CRSREF, tmp_epsg, self.CRS_epsg)
        self.CRS_type_code = safe_cast_to_int(row,7)
        self.CRS_type      = row[8].strip()
        if self.CRS_type.lower()!=dictCRSTYPEREF[int(row[7])].lower():
            logging.warning("ROW: %s", row)
            logging.warning("CRSREF %s: type text and lookup do not agree: \"%s\" vs. \"%s\"", self.CRSREF, self.CRS_type, dictCRSTYPEREF[int(row[7])])
        if self.CRS_name==None:
            self.CRS_name = row[9].strip()

    # ### Set compound horizontal CRS; assume already defined
    # def set_rec_Compound_CRS_Horizontal_Identification(self, row, dictCRS):
        # logging.debug("Compound CRS horizontal set details: %s", row[:5])
        # key = safe_cast_to_int(row,5)
        # if key != self.CRSREF:
            # logging.critical("something went wrong that should never have gone wrong")
        # # Assume horizontal component is 2d, which is probably mandatory anyway
        # self.CRSREF_hor   = safe_cast_to_int(row,6)
        # CRS               = dictCRS[self.CRSREF_hor] #link to object: assume it was already defined earlier in the file
        # self.CRS_epsg_hor = CRS.CRS_epsg # hope this is a copy and not a link...
        # self.CRS_name_hor = CRS.CRS_name
        # #self.CRS_name_hor = CRS.get_crs_name()
        # self.CS_dimension = CRS.CS_dimension  # later +1 one for vertical
        # # Careful! either make a .copy() of the list, or copy the elements, otherwise you change the original CRS!
        # for key in CRS.CS_axes_names:
            # self.CS_axes_names[key] = CRS.CS_axes_names[key] # axis=1,2
        # for key in CRS.CS_axes_units:
            # self.CS_axes_units[key] = CRS.CS_axes_units[key]
        # #self.CS_axes_names = CRS.CS_axes_names.copy() # later add vertical
        # #self.CS_axes_units = CRS.CS_axes_units.copy() # later add vertical

    # ### Set compound vertical CRS; assume already defined.  Issue is this cannot use a key as "axis=1", must be
    # def set_rec_Compound_CRS_Vertical_Identification(self, row, dictCRS):
        # logging.debug("Compound CRS vertical set details: %s", row[:5])
        # key = safe_cast_to_int(row,5)
        # if key != self.CRSREF:
            # logging.critical("something went wrong that should never have gone wrong")
        # #
        # self.CRSREF_vert   = safe_cast_to_int(row,6)
        # CRS                = dictCRS[self.CRSREF_vert] #link object: assume it was already defined earlier in the file
        # self.CRS_epsg_vert = CRS.CRS_epsg
        # self.CRS_name_vert = CRS.CRS_name
        # self.CS_dimension += 1
        # self.CS_axes_names[self.CS_dimension] = CRS.CS_axes_names[1] # by definition dim=1 for vertical
        # self.CS_axes_units[self.CS_dimension] = CRS.CS_axes_units[1] # by definition dim=1 for vertical


    ### Coordinate System details
    def set_rec_Coordinate_System_Details(self, row):
        logging.debug("CS set details for CRSREF: %s", row[:5])
        key = safe_cast_to_int(row,5)
        if key != self.CRSREF:
            logging.critical("something went wrong that should never have gone wrong")
        self.CS_dimension = safe_cast_to_int(row,10)

    ### Coordinate Axis Details
    def set_rec_Coordinate_Axis_Details(self, row):
        logging.debug("CS set axis details: %s", row[:5])
        key = safe_cast_to_int(row,5)
        if key != self.CRSREF:
            logging.critical("something went wrong that should never have gone wrong")
        n = safe_cast_to_int(row,6) # field 7 has the coordinate number (order)
        self.CS_axes_codes[n]         = safe_cast_to_int(row,7)
        self.CS_axes_names[n]         = row[8].strip()
        self.CS_axes_orientations[n]  = row[9].strip()
        self.CS_axes_abbreviations[n] = row[10].strip()
        self.CS_axes_unitREFs[n]      = safe_cast_to_int(row,11)
        self.CS_axes_units[n]         = row[12].strip()


    ### Coordinate Axis Conversion Applied
    def set_rec_Coordinate_Axis_Conversion_Applied(self, row):
        logging.debug("CS axis conversion applied: %s", row[:5])
        key = safe_cast_to_int(row,5)
        if key != self.CRSREF:
            logging.critical("something went wrong that should never have gone wrong")
        self.CS_axis_conversion_applied = row[9].strip()

    ### Return string with CRS name and EPSG code
    def get_crs_name(self):
        name = self.CRS_name
        if self.CRS_type:
            name = self.CRS_type + ' CRS: ' + self.CRS_name
        if self.CRS_epsg==-1:
            name = name + ' [unkn EPSG]' # parser error
        elif self.CRS_epsg==0:
            name = name + ' [no EPSG]'   # blank EPSG code
        else:
            name = name + ' [' + str(self.CRS_epsg) + ']'
        return name

    ### Call this function from main in a loop at some point for each CRS to do some checks
    def check_mandatory_records(self):
        logging.debug('check_crs_def: make sure CRS has a name, code, and axes names and units')
        if self.CRS_epsg>0 and self.CRS_epsg<999:
            logging.warning("CRSREF %s: %s: EPSG code<999 not supported in EPSG Dataset.", self.CRSREF, get_crs_name())
        if self.CRS_epsg>99999:
            logging.warning("CRSREF %s: %s: EPSG code>99999 not supported in EPSG Dataset.", self.CRSREF, get_crs_name())

    ### Record writers - requires a file handler to an open ascii file
    def write_rec_CRS_Implicit_Identification(self, outfh):
        rec_fmt = dict_record_spec[rec_CRS_Implicit_Identification][1][2].replace("BLANK",'')
        f1,f2,f3,f4,f5 = rec_CRS_Implicit_Identification
        f6  = self.CRSREF
        f7  = self.CRS_epsg
        f8  = self.CRS_name
        f9  = self.EPSG_version
        f10 = self.EPSG_date
        f11 = self.EPSG_source
        f12 = self.description
        outfh.write(rec_fmt.format(f1,f2,f3,f4,f5, f6,f7,f8,f9,f10,f11,f12))
        outfh.write("\n")

    #### for CRS without EPSG code
    def write_rec_CRS_Details(self, outfh):
        rec_fmt = dict_record_spec[rec_CRS_Details][1][2].replace("BLANK",'')
        f1,f2,f3,f4,f5 = rec_CRS_Details
        f6  = self.CRSREF
        f7  = self.CRS_epsg
        #if f7<0: f7=''
        f8  = self.CRS_type_code
        f9  = self.CRS_type
        f10 = self.CRS_name
        outfh.write(rec_fmt.format(f1,f2,f3,f4,f5, f6,f7,f8,f9,f10))
        outfh.write("\n")

    #rec_Coordinate_Axis_Details = ('HC','1','6','1', 'Coordinate System Axis {AxisNumber}') # rec(4).format(AxisNumber=int(row(6))) using field 7
    #expected_field5 = p7recordID[4].format(AxisNumber=safe_cast_to_int(row,6))
    ### Write all axes details in the CS of the CRS
    def write_rec_Coordinate_Axis_Details(self, outfh):
        rec_fmt = dict_record_spec[rec_Coordinate_Axis_Details][1][2].replace("BLANK",'')
        f1,f2,f3,f4 = rec_Coordinate_Axis_Details[0:4]
        for i in range(1,len(self.CS_axes_names)+1):
            f5  = rec_Coordinate_Axis_Details[4].format(AxisNumber=i)
            f6  = self.CRSREF
            f7  = i
            f8  = self.CS_axes_codes[i]
            f9  = self.CS_axes_names[i]
            f10 = self.CS_axes_orientations[i]
            f11 = self.CS_axes_abbreviations[i]
            f12 = self.CS_axes_unitREFs[i]
            f13 = self.CS_axes_units[i]
            outfh.write(rec_fmt.format(f1,f2,f3,f4,f5, f6,f7,f8,f9,f10,f11,f12,f13))
            outfh.write("\n")

    #### For compound CRS without EPSG code
    def write_rec_Compound_CRS_Horizontal_Identification(self, outfh):
        rec_fmt = dict_record_spec[rec_Compound_CRS_Horizontal_Identification][1][2].replace("BLANK",'')
        f1,f2,f3,f4,f5 = rec_Compound_CRS_Horizontal_Identification
        f6  = self.CRSREF
        f7  = self.CRSREF_hor
        f8  = self.CRS_type_code
        f9  = self.CRS_name_hor
        outfh.write(rec_fmt.format(f1,f2,f3,f4,f5, f6,f7,f8,f9))
        outfh.write("\n")

    #### For compound CRS without EPSG code
    def write_rec_Compound_CRS_Vertical_Identification(self, outfh):
        rec_fmt = dict_record_spec[rec_Compound_CRS_Vertical_Identification][1][2].replace("BLANK",'')
        f1,f2,f3,f4,f5 = rec_Compound_CRS_Vertical_Identification
        f6  = self.CRSREF
        f7  = self.CRSREF_vert
        f8  = self.CRS_type_code
        f9  = self.CRS_name_vert
        outfh.write(rec_fmt.format(f1,f2,f3,f4,f5, f6,f7,f8,f9))
        outfh.write("\n")



####################################################################
### COORDINATE TRANSFORMATION
###
### Bert Kampes, 2018-08-10
####################################################################
class CT:
    def __init__ (self, row): # constructor using row rec_CT_Implicit_Identification
        logging.debug("CT CONSTRUCTOR: %s", row[:5])
        ### Initialize
        self.row             = row.copy()
        self.source_CRS_epsg = None
        self.source_CRS_name = None
        self.source_CRSREF   = None
        self.target_CRS_epsg = None
        self.target_CRS_name = None
        self.target_CRSREF   = None
        self.CT_method_name      = None
        self.CT_method_num_param = 0
        self.CT_method_params    = [] # list of read rows for now

        ### Parse row
        self.COTRANSREF   = safe_cast_to_int(row,5)         # e.g., 1
        self.CT_epsg      = safe_cast_to_int(row,6)       # e.g., 26715
        self.CT_name      = row[7].strip()                # e.g., "NAD27 to WGS 84 (79)"
        self.EPSG_version = row[8].strip()
        self.EPSG_date    = row[9].strip()
        self.EPSG_source  = row[10].strip()
        self.description  = row[11].strip()

    ### Coordinate Transformation
    def set_rec_CT_Explicit_Definition(self, row):
        logging.debug("CT set details for COTRANSREF: %s", row[:5])
        key = safe_cast_to_int(row,5)
        if key != self.COTRANSREF:
            logging.critical("something went wrong that should never have gone wrong")
        if self.CT_epsg==-1:
            self.CT_epsg = safe_cast_to_int(row,6)
        if self.CT_name==None:
            self.CT_name = row[7].strip()

    ###
    def set_rec_CT_Details(self, row):
        logging.debug("CT set details for COTRANSREF: %s", row[:5])
        key = safe_cast_to_int(row,5)
        if key != self.COTRANSREF:
            logging.critical("something went wrong that should never have gone wrong")

        self.source_CRSREF  = safe_cast_to_int(row,6)
        try:    self.source_CRS_epsg = safe_cast_to_int(row,7)
        except: logging.debug("No EPSG code for source CRS %s", row[8])
        self.source_CRS_name = row[8].strip()

        self.target_CRSREF  =   safe_cast_to_int(row,9)
        try:    self.target_CRS_epsg = safe_cast_to_int(row,10)
        except: logging.debug("No EPSG code for source CRS %s", row[11])
        self.target_CRS_name = row[11].strip()

    ###
    def set_rec_CT_Method_Details(self, row):
        key = safe_cast_to_int(row,5)
        if key != self.COTRANSREF:
            logging.critical("something went wrong that should never have gone wrong")
        self.CT_method_name      = row[7].strip() # e.g., Position vector, etc.
        self.CT_method_num_param = safe_cast_to_int(row,9) # e.g., 7

    ###
    def set_rec_CT_Parameters(self, row):
        key = safe_cast_to_int(row,5)
        if key != self.COTRANSREF:
            logging.critical("something went wrong that should never have gone wrong")
        self.CT_method_params.append(row) # deal with this later; can use like len(self.CT_method_params) and self.CT_method_params[0][field]

    ### more functions to be defined to read method and parameters explicit definitions...
    ### ...

    ### Record writers - requires a file handler to an open ascii file
    def write_rec_CT_Implicit_Identification(self, outfh):
        rec_fmt = dict_record_spec[rec_CT_Implicit_Identification][1][2].replace("BLANK",'')
        f1,f2,f3,f4,f5 = rec_CT_Implicit_Identification
        f6  = self.COTRANSREF
        f7  = self.CT_epsg
        f8  = self.CT_name
        f9  = self.EPSG_version
        f10 = self.EPSG_date
        f11 = self.EPSG_source
        f12 = self.description
        outfh.write(rec_fmt.format(f1,f2,f3,f4,f5, f6,f7,f8,f9,f10,f11,f12))
        outfh.write("\n")


####################################################################
### WELL POSITION OBJECT (e.g., WRP, SRP, etc.)
###
### Bert Kampes, 2018-08-10
####################################################################
class WOBJ:

    ### Constructor based on H7,4,0,0 Position Object Definition
    def __init__ (self, row):
        logging.debug("WOBJ CONSTRUCTOR: %s", row[:5])
        ### Initialize
        self.O7_row                 = None   # copy of O7 row with all details
        self.CRS_A_coords           = ()     # tuple 3
        self.CRS_B_coords           = ()     # tuple 2
        self.CRS_C_coords           = ()     # tuple 2
        self.hor_radial_uncertainty = 0.0 # 1-sigma; assumed slot_uncertainty stored in WRP with WELL object, and site_uncertainty in SRP with STRUCTURE object
        self.vert_uncertainty       = 0.0 # 1-sigma
        self.record_version         = None # 0
        # self.CRS_A_name           = None
        # self.CRS_A_axes           = {}
        # self.CRS_A_units          = {}
        # self.CRS_B_name           = None
        # self.CRS_B_axes           = {}
        # self.CRS_B_units          = {}
        # self.CRS_C_name           = None
        # self.CRS_C_axes           = {}
        # self.CRS_C_units          = {}

        ### Parse row
        self.row              = row.copy()                   # copy of Position Object Definition row
        self.WOBJREF          = safe_cast_to_int(row,5)
        self.wobj_short_name  = row[6].strip()               # user defined
        self.wobj_type_id     = safe_cast_to_int(row,7)      # key into dictWOBJTYPEID
        self.wobj_type_name   = row[8].strip()
        if dictWOBJTYPEID[self.wobj_type_id][1]!=self.wobj_type_name:
            logging.warning("WOBJ type %d: I expected WOBJ type: %s but found %s",
                self.wobj_type_id, dictWOBJTYPEID[self.wobj_type_id][1], self.wobj_type_name)
        self.wobj_description = row[9].strip()
        self.P7TABLEREF        = safe_cast_to_int(row,10)     # may be blank, e.g., for SRP but generally should be there.  Make mandatory?
        self.wobj_MD          = safe_cast_to_float(row,11)   # may be blank, but e.g., for WRP expect it.  Can add error checking
        #self.wobj_TVD         = safe_cast_to_float(row,12)   # may be blank, but e.g., for WRP expect it.  Can add error checking

    ### Add O7 record coordinates
    def set_rec_O7_Position_Record (self, row):
        logging.debug("O7 ROW: %s", row[:5])
        self.O7row            = row.copy()                # copy of Well Object summary row

        ### parse row
        self.record_version    = safe_cast_to_int(row,1)
        self.WOBJREF           = safe_cast_to_int(row,2)
        self.wobj_type_abbreviation = row[3].strip()            # format-mandated abbreviations, e.g., WRP
        self.wobj_short_nameQC = row[4].strip()            # user-defined; should match exactly what was given in H7,4,0,0 object constructor
        # Cross-check short_name
        if self.wobj_short_nameQC!=self.wobj_short_name:
             logging.error("WOBJ Short Name not identical in H7,4,0,0 \"%s\" vs. O7 \"%s\"", self.wobj_short_name,self.wobj_short_nameQC)

		# Coordinates stored internally as str.  Cast to float if required for p717 record writer (not for screen).
        # CRS A is projected, ordered Northing, Easting, Depth
        # CRS B is the geographic, ordered Latitude, Longitude
        # CRS C is CRSREF=1 geographic global 2D, ordered Latitude, Longitude
        self.CRS_A_coords = (row[ 5].strip(), row[ 6].strip(), row[ 7].strip())
        self.CRS_B_coords = (row[ 8].strip(), row[ 9].strip())
        self.CRS_C_coords = (row[10].strip(), row[11].strip())

		# Uncertainty
        self.hor_radial_uncertainty = safe_cast_to_float(row,12)
        self.vert_uncertainty       = safe_cast_to_float(row,13)

        ### Check uncertainties (empty fields could be allowed e.g. if no vertical)
        if self.hor_radial_uncertainty<0:
            self.hor_radial_uncertainty=0.0
            logging.debug("Setting horizontal radial uncertainty to 0.0")
        if self.vert_uncertainty<0:
            self.vert_uncertainty=0.0
            logging.debug("Setting vertical uncertainty to 0.0")

        # ### Add details on Fixed Object

        # ### Create pointers to CRSs. (note: this is not a .copy() or .deepcopy() but assume won't be modified
        # tmpP7TYPE = dictP7TYPE[self.P7TYPEREF]
        # self.CRSREF_CRS_A =  tmpP7TYPE.CRSREF_CRS_A
        # self.CRSREF_CRS_B =  tmpP7TYPE.CRSREF_CRS_B
        # self.CRSREF_CRS_C =  tmpP7TYPE.CRSREF_CRS_C
        # # Assume CRSs by now were populated in second pass
        # #tmpCRS = dictCRS[self.CRSREF_CRS_A].deepcopy()
        # self.CRS_A_name   = dictCRS[self.CRSREF_CRS_A].get_crs_name()
        # self.CRS_A_axes   = dictCRS[self.CRSREF_CRS_A].CS_axes_names  # dict with [1], [2], or [3] entries
        # self.CRS_A_units  = dictCRS[self.CRSREF_CRS_A].CS_axes_units #
        # #
        # self.CRS_B_name   = dictCRS[self.CRSREF_CRS_B].get_crs_name()
        # self.CRS_B_axes   = dictCRS[self.CRSREF_CRS_B].CS_axes_names  # dict with [1], [2], or [3] entries
        # self.CRS_B_units  = dictCRS[self.CRSREF_CRS_B].CS_axes_units #
        # #
        # self.CRS_C_name   = dictCRS[self.CRSREF_CRS_C].get_crs_name()
        # self.CRS_C_axes   = dictCRS[self.CRSREF_CRS_C].CS_axes_names  # dict with [1], [2], or [3] entries
        # self.CRS_C_units  = dictCRS[self.CRSREF_CRS_C].CS_axes_units #

    ### Record writers - requires a file handler to an open ascii file
    def write_rec_Position_Object_Definition(self, outfh):
        rec_fmt = dict_record_spec[rec_Position_Object_Definition][1][2].replace("BLANK",'')
        f1,f2,f3,f4,f5 = rec_Position_Object_Definition
        f6  = self.WOBJREF
        f7  = self.wobj_short_name
        f8  = self.wobj_type_id
        f9  = self.wobj_type_name
        f10 = self.wobj_description
        f11 = self.P7TABLEREF
        f12 = self.wobj_MD
        #f13 = self.wobj_TVD
        outfh.write(rec_fmt.format(f1,f2,f3,f4,f5, f6,f7,f8,f9,f10,f11,f12))
        outfh.write("\n")


    ### Current record version = 0 (int)
    def write_rec_O7_Position_Record(self, outfh):
        rec_fmt = dict_record_spec[rec_O7_Position_Record][1][2].replace("BLANK",'')
        f1  = rec_O7_Position_Record[0]
        f2  = self.record_version
        f2  = 0
        f3  = self.WOBJREF
        f4  = self.wobj_type_abbreviation
        f5  = self.wobj_short_name
        # cast to float to use format %.2f
        f6  = safe_cast_to_float(self.CRS_A_coords,0)
        f7  = safe_cast_to_float(self.CRS_A_coords,1)
        f8  = safe_cast_to_float(self.CRS_A_coords,2)
        f9  = safe_cast_to_float(self.CRS_B_coords,0)
        f10 = safe_cast_to_float(self.CRS_B_coords,1)
        f11 = safe_cast_to_float(self.CRS_C_coords,0)
        f12 = safe_cast_to_float(self.CRS_C_coords,1)
		# uncertainties
        f13 = self.hor_radial_uncertainty
        f14 = self.vert_uncertainty

        #print(f1,f2,f3,f4,f5, f6,f7,f8,f9,f10,f11,f12,f13,f14)
        outfh.write(rec_fmt.format(f1,f2,f3,f4,f5, f6,f7,f8,f9,f10,f11,f12,f13,f14))
        outfh.write("\n")


    ### Simple debug printer.  Requires CRSs to be set already by calling first
    ### Wobj.setCRS(Project) - where Project holds the CRS
    ### then Wobj.report_wobj()
    def report_wobj(self, outfh):
        logging.debug("printing variables of fixed object")
        outfh.write("\n")
        outfh.write("WOBJ {}: {} {}\n".format(self.WOBJREF, self.wobj_type_abbreviation, self.wobj_description))
        outfh.write("----------------------------------------\n")
        #outfh.write("  CRSREF A:      {}\n".format(self.CRSREF_CRS_A))
        #outfh.write("  CRS A name:    {}\n".format(self.CRS_A_name))
        outfh.write("  CRS A name:    {}\n".format("unknown CRS A"))
        outfh.write("  CRS_A_coords:  {}\n".format(self.CRS_A_coords))
        #outfh.write("  CRS_A_axes:    {}\n".format(self.CRS_A_axes))
        #outfh.write("  CRS_A_units:   {}\n".format(self.CRS_A_units))
        #outfh.write("  CRSREF B:      {}\n".format(self.CRSREF_CRS_B))
        #outfh.write("  CRS B name:    {}\n".format(self.CRS_B_name))
        outfh.write("  CRS B name:    {}\n".format("self.CRS_B_name"))
        outfh.write("  CRS_B_coords:  {}\n".format(self.CRS_B_coords))
        #outfh.write("  CRS_B_axes:    {}\n".format(self.CRS_B_axes))
        #outfh.write("  CRS_B_units:   {}\n".format(self.CRS_B_units))
        #outfh.write("  CRSREF C:      {}\n".format(self.CRSREF_CRS_C))
        #outfh.write("  CRS C name:    {}\n".format(self.CRS_C_name))
        outfh.write("  CRS C name:    {}\n".format("unknown CRS C"))
        outfh.write("  CRS_C_coords:  {}\n".format(self.CRS_C_coords))
        #outfh.write("  CRS_C_axes:    {}\n".format(self.CRS_C_axes))
        #outfh.write("  CRS_C_units:   {}\n".format(self.CRS_C_units))
        outfh.write("  hor_radial_uncertainty: {} ({})\n".format(self.hor_radial_uncertainty, "self.hor_uncertainty_unit"))
        outfh.write("  hor_radial_confidence:  {}\n".format("1-sigma"))




####################################################################
### MEASUREMENT TOOL
###
### Bert Kampes, 2019-06-22
####################################################################
class MT:
    def __init__ (self, row): # constructor using row rec_Measurement_Tool_Definition
        ### Create a dummy row if None is passed to construct object and fill with values
        if row is None:
            row   = "H7,2,0,0,Measurement Tool Definition…,1,MWD,MWD,1,,,".split(",")
        logging.debug("MT CONSTRUCTOR: %s", row[:5])
        ### Initialize
        self.row             = row.copy()

        # Measurement Tool Definition (mandatory if raw data)
        ### Parse row
        self.MTREF                   = safe_cast_to_int(row,5)
        self.MT_user_name            = row[6].strip()
        self.MTTYPEID                = safe_cast_to_int(row,7) # fixed table; ID first, then name
        self.MT_type_name            = row[8].strip()
        self.MT_manufacturer         = row[9].strip()
        self.MT_serial_number        = row[10].strip()
        self.MT_dist_above_bha       = safe_cast_to_float(row,11)
        # Cross-check MTTYPE_name given in Survey Definition
        if dictMTTYPEID[self.MTTYPEID]!=self.MT_type_name:
            logging.error("MTYPEREF %d, type %s.  Expected %s", self.MTTYPEID, self.MT_type_name, dictMTTYPEID[self.MTTYPEID])


    ### Record writers - requires a file handler to an open ascii file
    def write_rec_Measurement_Tool_Definition(self, outfh):
        logging.debug("write_rec_Measurement_Tool_Definition")
        rec_fmt = dict_record_spec[rec_Measurement_Tool_Definition][1][2].replace("BLANK",'')
        f1,f2,f3,f4,f5 = rec_Measurement_Tool_Definition
        f6  = self.MTREF
        f7  = self.MT_user_name
        f8  = self.MTTYPEID
        f9  = self.MT_type_name
        f10 = self.MT_manufacturer
        f11 = self.MT_serial_number
        f12 = self.dist_above_bha
        outfh.write(rec_fmt.format(f1,f2,f3,f4,f5, f6,f7,f8,f9,f10,f11,f12))
        outfh.write("\n")



####################################################################
### PROJECT
###   Read IOGP p7 record identifier and Project Name, Project CRS
###   Stores also File information (processing details)
### Bert Kampes, 2018-08-10
####################################################################
class PROJECT:

    ### Constructor based on IOGP_File_Identification_Record
    def __init__ (self, row=None):

        ### Create a dummy row if None is passed to construct object and fill with values
        if row is None:
            row   = "IOGP,IOGP P7,7,1.0,1,2017:03:25,17:40:01,Example.P717,".split(",")
            #row11 = "HC,0,1,1,Project Name,Pegasus,Pegasus Field,Texas,United States,USA".split(",")
            #self.set_rec_Project_Information(row11)
        logging.debug("PROJECT CONSTRUCTOR: %s", row[:5])
        self.row                   = row.copy()

        ### Initialize
        self.project_name          = None
        self.field_name            = None
        self.region                = None
        self.country_name          = None
        self.country_text          = None
        self.projectCRS_name       = None
        self.projectCRS_CRSREF     = None
        self.projectCRS_hor_unit      = None
        self.projectCRS_vert_unit     = None
        self.file_content_description = None
        self.file_additional_content  = None
        self.processing_details       = None

        ### Parse row
        logging.debug("IOGP File ID ROW: %s", row[:5])
        self.contents_description = row[1].strip()
        self.format_code          = safe_cast_to_int(row,2)
        if self.format_code != 7:
            logging.critical("incorrect IOGP File Identification Record (I expected code 7 in field 3), read \"%s\"", row[2])
        self.format_version       = safe_cast_to_float(row,3)
        self.file_issue           = safe_cast_to_int(row,4)
        self.date_file_written    = row[5].strip()
        self.time_file_written    = row[6].strip()
        self.name_of_file         = row[7].strip()
        self.prepared_by          = row[8].strip()

    ### Add information from rec_Project_Information
    def set_rec_Project_Information (self, row):
        logging.debug("set_rec_Project_Information ROW: %s", row[:5])
        self.project_name          = row[5].strip()
        self.field_name            = row[6].strip()
        self.region                = row[7].strip()
        self.country_name          = row[8].strip()
        self.country_text          = row[9].strip()
        #self.projectCRS_name       = row[10].strip()
        #self.projectCRS_CRSREF     = safe_cast_to_int(row,11)
        #self.projectCRS_hor_unit   = row[12].strip()
        #self.projectCRS_vert_unit  = row[13].strip()


    # ### +++ add CRS details here after reading


    ### Record writers - requires a file handler to an open ascii file
    def write_rec_IOGP_File_Identification_Record(self, outfh):
        #IOGP,User Guide Example A,7,1.0,1,2017:08:06,17:40:01,Example.p717,IOGP Geomatics
        rec_fmt = dict_record_spec[rec_Project_Information][1][2].replace("BLANK",'')
        f1 = rec_IOGP_File_Identification_Record[0]
        f2 = self.contents_description
        #f3 = self.format_code      # must be 7
        #f4 = self.format_version   # must be 1.0
        #f5 = self.file_issue       # must be 1 (here, original writing first time)
        #f6 = self.date_file_written
        #f7 = self.time_file_written
        #f8 = self.name_of_file
        #f9 = self.prepared_by
        f8 = None
        f9 = None
        # check
        if not f2: f2="IOGP P7"
        if not f8: f8=outfh.name             # f8 = os.path.basename(outfh.name)
        if not f9: f9="p717 sample writer"

        # write
        #outfh.write(rec_fmt.format(f1,f2,f3,f4,f5, f6,f7,f8,f9))
        q = datetime.datetime.now()
        outfh.write("{f1},{f2},7,1.0,1,{DATE},{TIME},{f8},{f9}".format(f1=f1,f2=f2,DATE=q.strftime("%Y:%m:%d"),TIME=q.strftime("%H:%M:%S"),f8=f8,f9=f9))
        outfh.write("\n")

    ###
    def write_rec_Project_Information(self, outfh):
        #HC,0,1,0,Project Name,Pegasus,Pegasus Field,Texas,United States,USA,NAD27 / Texas Central + NGVD29 depth (ftUS),4,ftUS,ftUS
        #rec_Project_Information   = ('HC','0','1','1', 'Project Name')                    #  mandatory
        #rec_Project_Information:  [0, (1,    1,'{},{},{},{},{:<32},{},{},{},{},{},{},{:d},{},{}', () )],
        rec_fmt = dict_record_spec[rec_Project_Information][1][2].replace("BLANK",'')
        #num_fields   = len(rec_fmt.split(","))

        f1,f2,f3,f4,f5 = rec_Project_Information
        f6  = self.project_name
        f7  = self.field_name
        f8  = self.region
        f9  = self.country_name
        f10 = self.country_text
        #f11 = self.projectCRS_name
        #f12 = self.projectCRS_CRSREF
        #f13 = self.projectCRS_hor_unit
        #f14 = self.projectCRS_vert_unit
        outfh.write(rec_fmt.format(f1,f2,f3,f4,f5, f6,f7,f8,f9,f10))
        outfh.write("\n")




####################################################################
### STRUCTURE
### Pointer to SRP contains coordinates and uncertainty
###
### Bert Kampes, 2018-08-10
####################################################################
class STRUCTURE:

    ### Constructor based on H7,1,0,0,Structure Definition,...
    def __init__ (self, row=None):

        ### Create a dummy row if none is passed to fill/construct
        if row is None:
            row  = "H7,1,0,0,Structure Definition,1,Pad A,SRP,1,Centre Slot A1,Onshore".split(",")

        logging.debug("STRUCTURE CONSTRUCTOR: %s", row[:5])
        self.row                          = row.copy()

        ### Initialize
        self.StructureDetail_row          = []
        self.structure_level_name         = None
        self.structure_water_depth        = 0.0 # above VRS (should be part of wellbore?)
        self.structure_height_date     = None
        self.structure_north_reference_ID = None
        self.structure_north_reference    = None
        self.structure_north_heading      = None
        # structure offset units are same as for projected CRS

        ### Parse row
        self.STRUCTUREREF    = safe_cast_to_int(row,5)
        self.structure_name  = row[6].strip()
        self.SRP_shortname   = row[7].strip()
        self.SRP_WOBJREF     = safe_cast_to_int(row,8) # mandatory
        self.SRP_description = row[9].strip()
        self.environment     = row[10].strip()

    ### Add information from Structure Detail record
    def set_rec_Structure_Details (self, row):
        logging.debug("Structure Details ROW: %s", row[:5])
        self.StructureDetail_row  = row.copy()
        ### Check consistency of STRUCTUREREF
        if self.STRUCTUREREF!= safe_cast_to_int(row,5):
            logging.error("Inconsistent references to STRUCTUREREF in Detail")
        self.structure_level_name         = row[6].strip()                 # e.g., "Ground Level"
        self.structure_height             = safe_cast_to_float(row,7) # in units of vertical CRS
        self.structure_water_depth        = safe_cast_to_float(row,8)     # may be blank
        self.structure_height_date        = row[9].strip()
        self.structure_north_reference_ID = safe_cast_to_int(row,10)
        self.structure_north_reference    = row[11].strip()
        self.structure_north_heading      = safe_cast_to_float(row,12)  # degrees


    ### Record writers - requires a file handler to an open ascii file
    def write_rec_Structure_Definition(self, outfh):
        rec_fmt = dict_record_spec[rec_Structure_Definition][1][2].replace("BLANK",'')
        f1,f2,f3,f4,f5 = rec_Structure_Definition
        f6  = self.STRUCTUREREF
        f7  = self.structure_name
        f8  = self.SRP_shortname
        f9  = self.SRP_WOBJREF
        f10 = self.SRP_description
        f11 = self.environment
        outfh.write(rec_fmt.format(f1,f2,f3,f4,f5, f6,f7,f8,f9,f10,f11))
        outfh.write("\n")

    # P7 specific header
    def write_rec_Structure_Details(self, outfh):
        rec_fmt = dict_record_spec[rec_Structure_Details][1][2].replace("BLANK",'')
        f1,f2,f3,f4,f5 = rec_Structure_Details
        f6  = self.STRUCTUREREF
        f7  = self.structure_level_name
        f8  = self.structure_height
        f9  = self.structure_water_depth
        f10 = self.structure_height_date
        f11 = self.structure_north_reference_ID
        f12 = self.structure_north_reference
        f13 = self.structure_north_heading
        outfh.write(rec_fmt.format(f1,f2,f3,f4,f5, f6,f7,f8,f9,f10,f11,f12,f13))
        outfh.write("\n")



    ### Return something or set something that WRP is clear (coordinates, CRS, etc.)
    #Call this function after everything is set.
    def report_SRP(self, dictWOBJ, outfh):
        logging.debug("getSRP")
        if self.SRP_WOBJREF==None:
            print("no SRP defined for this structure")
        else:
            SRP = dictWOBJ[self.SRP_WOBJREF]
            SRP.report_wobj(outfh)



####################################################################
### WELL
### Requires well definition record and well details
### Contains pointer to WRP(E,N); which also contains uncertainty
###
### Bert Kampes, 2018-08-10
####################################################################
class WELL:

    ### Constructor based on H7,1,2,0,Well Definition
    def __init__ (self, row=None):

        ### Create a dummy row if none is passed to fill/construct
        if row is None:
            row = "H7,1,2,0,Well Definition,1,1,WRP,2,207/29-A6,207/29-A6,DTI,,,,As-drilled,UKCS Block 207/29,2012:05:15".split(",")

        logging.debug("WELL CONSTRUCTOR: %s", row[:5])
        self.row                    = row.copy()

        ### Initialize
        self.WellDetail_row         = []     #
        self.WRP_description        = None   #WRP
        self.WRP_document           = None   #WRP
        self.slot_name              = None
        self.slot_diameter          = None
        self.slot_diameter_unit     = None
        self.positioning_company    = None
        self.platform_east_offset   = None
        self.platform_north_offset  = None

        ### Parse row
        self.WELLREF                = safe_cast_to_int(row,5)
        self.STRUCTUREREF           = safe_cast_to_int(row,6)
        self.WRP_short_name         = row[7].strip()
        self.WRP_WOBJREF            = safe_cast_to_int(row,8)    #WRP
        self.primary_UWI            = row[9].strip()
        self.primary_well_name      = row[10].strip()
        self.primary_authority      = row[11].strip()
        self.alt_UWI_list           = row[12].strip()  # delimited by &
        self.alt_well_name_list     = row[13].strip()  # delimited by &
        self.alt_authorithy_list    = row[14].strip()  # delimited by &
        self.well_status            = row[15].strip()
        self.licence_name           = row[16].strip()
        self.spud_date              = row[17].strip()

    ### Add information from Well Detail record
    def set_rec_Well_Details (self, row):  # from H7,1,1,0 Well Details
        logging.debug("WELL SET WELL DETAILS ROW: %s", row[:5])
        self.WellDetail_row  = row.copy()
        ### Check consistency of WELLREF
        if self.WELLREF!= safe_cast_to_int(row,5):
            logging.error("Inconsistent references to WELLREF in Detail")
        self.WRP_description       = row[6].strip() #WRP
        self.WRP_document          = row[7].strip() #WRP
        self.slot_name             = row[8].strip()
        self.slot_diameter         = safe_cast_to_float(row,9)
        self.slot_diameter_unit    = safe_cast_to_int(row,10)
        self.platform_east_offset  = safe_cast_to_float(row,11)
        self.platform_north_offset = safe_cast_to_float(row,12)


    ### Record writers - requires a file handler to an open ascii file
    def write_rec_Well_Definition(self, outfh):
        rec_fmt = dict_record_spec[rec_Well_Definition][1][2].replace("BLANK",'')
        f1,f2,f3,f4,f5 = rec_Well_Definition
        f6  = self.WELLREF
        f7  = self.STRUCTUREREF
        f8  = self.WRP_short_name
        f9  = self.WRP_WOBJREF
        f10 = self.primary_UWI
        f11 = self.primary_well_name
        f12 = self.primary_authority
        f13 = self.alt_UWI_list
        f14 = self.alt_well_name_list
        f15 = self.alt_authorithy_list
        f16 = self.well_status
        f17 = self.licence_name
        f18 = self.spud_date
        outfh.write(rec_fmt.format(f1,f2,f3,f4,f5, f6,f7,f8,f9,f10,f11,f12,f13,f14,f15,f16,f17,f18))
        outfh.write("\n")

    ### P7 specific header
    def write_rec_Well_Details(self, outfh):
        rec_fmt = dict_record_spec[rec_Well_Details][1][2].replace("BLANK",'')
        f1,f2,f3,f4,f5 = rec_Well_Details
        f6  = self.WELLREF
        f7  = self.WRP_description
        f8  = self.WRP_document
        f9  = self.slot_name
        f10 = self.slot_diameter
        f11 = self.slot_diameter_unit
        f12 = self.platform_east_offset
        f13 = self.platform_north_offset
        outfh.write(rec_fmt.format(f1,f2,f3,f4,f5, f6,f7,f8,f9,f10,f11,f12,f13))
        outfh.write("\n")


    ### Return something or set something that WRP is clear (coordinates, CRS, etc.)
    #Call this function after everything is set.
    def report_WRP(self, dictWOBJ, outfh):
        logging.debug("getWRP")
        WRP = dictWOBJ[self.WRP_WOBJREF]
        WRP.report_wobj(outfh)


####################################################################
### WELLBORE
###
### Bert Kampes, 2018-08-10
####################################################################
class WELLBORE:

    ### Constructor based on H7,1,3,0,Wellbore Definition
    def __init__ (self, row=None):
        ### Create a dummy row if none is passed to fill/construct
        if row is None:
            row = "H7,1,3,0,Wellbore Definition,1,1,207/29-2Z,207/29-2Z,OGA,,,,Existing,207/29,ST00BP00".split(",")

        logging.debug("WELLBORE CONSTRUCTOR: %s", row[:5])
        self.row                    = row.copy()

        ### Parse row
        self.WELLBOREREF            = safe_cast_to_int(row,5)
        self.WELLREF                = safe_cast_to_int(row,6)
        self.primary_UWBI           = row[7].strip()
        self.primary_wellbore_name  = row[8].strip()
        self.primary_authority      = row[9].strip()
        self.alt_UWBI_list          = row[10].strip()  # delimited by &
        self.alt_wellbore_name_list = row[11].strip()  # delimited by &
        self.alt_authorithy_list    = row[12].strip()  # delimited by &
        self.wellbore_status        = row[13].strip()
        self.bhl_lease_number       = row[14].strip()
        self.wellbore_suffix        = row[15].strip()
        #self.sidetrack              = row[16].strip()
        #self.kickoff_depth          = safe_cast_to_float(row,17)
        #self.ko_SURVEYREF           = safe_cast_to_int(row,18) # can be blank
        #self.kickoff_date           = row[19].strip()

    ### Record writers - requires a file handler to an open ascii file
    def write_rec_Wellbore_Definition(self, outfh):
        rec_fmt = dict_record_spec[rec_Wellbore_Definition][1][2].replace("BLANK",'')
        f1,f2,f3,f4,f5 = rec_Wellbore_Definition
        f6  = self.WELLBOREREF
        f7  = self.WELLREF
        f8  = self.primary_UWBI
        f9  = self.primary_wellbore_name
        f10 = self.primary_authority
        f11 = self.alt_UWBI_list
        f12 = self.alt_wellbore_name_list
        f13 = self.alt_authorithy_list
        f14 = self.wellbore_status
        f15 = self.bhl_lease_number
        f16 = self.wellbore_suffix
        #f17 = self.sidetrack
        #f18 = self.kickoff_depth
        #f19 = self.ko_SURVEYREF
        #f20 = self.kickoff_date
        outfh.write(rec_fmt.format(f1,f2,f3,f4,f5, f6,f7,f8,f9,f10,f11,f12,f13,f14,f15,f16))
        outfh.write("\n")


####################################################################
### RIG - part of SURVEY and connected to STRUCTURE
### contains ZDP
###
### Bert Kampes, 2018-08-10
####################################################################
class RIG:

    ### Constructor based on H7,1,4,0,ZDP Rig/Workover Details
    def __init__ (self, row=None):

        ### Create a dummy row if none is passed to fill/construct
        if row is None:
            row  = "H7,1,4,0,Rig/Workover ZDP Definition,,1,Rig A,ZDP,3,1,Derrick Floor,1,1".split(",")

        logging.debug("RIG CONSTRUCTOR: %s", row[:5])
        self.row               = row.copy()
        #self.RigDetail_row     = []

        # ### Initialize
        # self.tvd_structure_level = None # optional field? If given, do cross check GLE+offset=ZDPE
        # self.md_structure_level  = None # optional field? not same as above if slanted.  (seems better case "slanted rig" Y/N

        ### Parse row
        self.RIGREF                    = safe_cast_to_int(row,5)
        self.rig_name                  = row[6].strip()
        self.ZDPabbreviation           = row[7].strip() # must be 'ZDP'
        self.ZDPREF                    = safe_cast_to_int(row,8)
        self.ZDP_typecode              = safe_cast_to_int(row,9) # e.g., code for 'KB'
        self.ZDP_type                  = row[10].strip() # e.g., 'KB'
        #self.ZDP_elevation             = safe_cast_to_float(row,8) # e.g., 102.1m above MSL - critical field!
        #self.ZDP_elevation_uncertainty = safe_cast_to_float(row,9) # e.g., 102.1m above MSL - critical field!
        #self.tvd_structure_level       = safe_cast_to_float(row,10) # above platform or GL
        #self.ZDP_date                  = row[11].strip()
        self.rig_type                  = row[11].strip()
        self.rig_slant_type            = row[12].strip()


    ### Record writers - requires a file handler to an open ascii file
    def write_rec_Rig_Definition(self, outfh):
        rec_fmt = dict_record_spec[rec_Rig_Definition][1][2].replace("BLANK",'')
        f1,f2,f3,f4,f5 = rec_Rig_Definition
        f6  = self.RIGREF
        f7  = self.rig_name
        f8  = 'ZDP' #mandatory abbreviation
        f9  = self.ZDPREF
        f10  = self.ZDP_typecode
        f11  = self.ZDP_type
        #f9  = self.ZDP_elevation
        #f10 = self.ZDP_elevation_uncertainty
        #f11 = self.tvd_structure_level          # "rig height"
        #f12 = self.ZDP_date
        f12 = self.rig_type
        f13 = self.rig_slant_type
        outfh.write(rec_fmt.format(f1,f2,f3,f4,f5, f6,f7,f8,f9,f10,f11,f12,f13))
        outfh.write("\n")




####################################################################
### SURVEY - MDINCAZ observables
### Class to hold survey definition object and variables
###
### Bert Kampes, 2018-08-10
####################################################################
class SURVEY:

    ### Constructor based on H7,1,5,0,Survey Definition
    def __init__ (self, row=None):

        ### Create a dummy row if none is passed to fill/construct
        if row is None:
            row  = "H7,1,5,0,Survey Definition,1,1,1,MWD Final Run,Magnetic,1,Open Hole,7-5/8, In,1100.0,2150.0,ft,2012:07:01,2012:07:02,ST=N,,,".split(",")

        logging.debug("SURVEY CONSTRUCTOR: %s", row[:5])

        ### Initialize variables
        self.row                = row.copy()
        self.SurveyDetail_row   = []
        self.Structure          = None #STRUCTURE object - to be added to each survey in reader program
        self.Well               = None #WELL object
        self.Wellbore           = None #WELLBORE object
        self.Rig                = None #RIG object

        # Operator/Survey contractor
        self.well_operator                = None
        self.survey_contractor            = None
        self.survey_contractor_job_number = None

        # Survey Details
        self.MD_UNITREF                = None
        self.MD_type_ID                = None
        self.MD_type_name              = None
        self.MD_type_flag              = None
        self.MD_type_flag_name         = None
        self.INC_type_flag             = None
        self.AZ_type_ID                = None
        self.AZ_type_name              = None
        self.AZ_type_flag              = None
        self.AZ_type_flag_name         = None
        self.convergence_applied_flag  = None
        self.convergence_applied_value = None
        self.declination_applied_flag  = None
        self.declination_applied_value = None
        self.geomag_parameters_date    = None
        self.MAGREF                    = None
        self.GRAVREF                   = None

#        # Tie Point (for sidetrack survey)
#        self.TP_P7TABLEREF             = None
#        self.TP_MD                     = None
#        self.TP_n                      = None
#        self.TP_e                      = None
#        self.TP_TVDZDP                 = None

        # Measurement Tool Definition (mandatory if raw data)
        self.MTREF                   = None # can be a list of integers

        ### Geomagnetic model (could collect multiple models in a dict, but assume only 1 in P7 file for now)
        self.geomag_strategy        = None
        self.geomag_model_name      = None
        self.geomag_model_year      = None
        self.geomag_ifr_source      = None

        ### Gravity model (could collect multiple models in a dict, but assume only 1 in P7 file for now)
        self.gravity_model_name     = None


        ### Associated CRSs
        self.fieldCRS_CRSREF       = None
        self.fieldCRS_name         = None
        self.fieldCRS_axes         = None
        self.fieldCRS_units        = None
        self.fieldCRSgeog_CRSREF   = None
        self.fieldCRSgeog_axes     = None
        self.fieldCRSgeog_units    = None
        self.CRSREF_hor_local      = None
        self.CRSREF_vert_local     = None

        ### Raw MWD data associated with survey; extend header and units if H7,6,0,0 is given
        self.rawmwd_data                  = [] #append when read
        self.rawmwd_num_extension_fields  = None
        self.rawmwd_extension_fields      = None
        self.rawmwd_headers               = ['pnt','time','flag','MD', 'INC', 'AZ', 'n', 'e', 'd',
          'Tool #', 'Gx', 'Gy', 'Gz', 'Bx', 'By', 'Bz', 'Gtot', 'Btot', 'ToolDip', 'MagTF', 'GravTF', 'refG', 'refB','refDIP', 'decl', 'conv']
        self.rawmwd_units                 = ['-', 'UTC', '-', 'MDunit', 'deg', 'deg', 'MDunit', 'MDunit', 'MDunit',
          '-', 'm/s2', 'm/s2', 'm/s2', 'nT', 'nT', 'nT', 'm/s2', 'nT', 'deg', 'deg', 'deg', 'm/s2', ',nT', 'deg', 'deg', 'deg']

        ### Raw Gyro data associated with survey; extend header and units if H7,6,0,0 is given
        self.rawgyro_data                 = [] #append when read
        self.rawgyro_num_extension_fields = None
        self.rawgyro_extension_fields     = None
        self.rawgyro_headers              = ['pnt','time','flag','MD', 'INC', 'AZ', 'n', 'e', 'd',
          'Tool #', 'Gx', 'Gy', 'Gz', 'Wx', 'Wy', 'Wz', 'Gtot', 'Lat', 'TotalER', 'GyroTF', 'GravTF', 'refG', 'refLat','refER', 'conv']
        self.rawgyro_units                = ['-', 'UTC', '-', 'MDunit', 'deg', 'deg', 'MDunit', 'MDunit', 'MDunit',
          '-', 'm/s2', 'm/s2', 'm/s2', 'deg/hr', 'deg/hr', 'deg/hr', 'm/s2', 'deg', 'deg/hr', 'deg', 'deg', 'm/s2', 'deg', 'deg/hr', 'deg']


        ### Parse row (constructor)
        self.SURVEYREF           = safe_cast_to_int(row,5)
        self.WELLBOREREF         = safe_cast_to_int(row,6)
        self.ZDPREF              = safe_cast_to_int(row,7)
        self.survey_name         = row[8].strip()
        self.MTTYPE_name         = row[9].strip() # e.g., 'Gyro'
        self.MTREF               = safe_cast_to_int(row,10) # counter
        self.hole_type           = row[11].strip() #
        self.hole_diameter_list  = row[12].strip() # list, delimited by &
        self.run_direction       = row[13].strip()
        self.MD_start            = safe_cast_to_float(row,14)
        self.MD_end              = safe_cast_to_float(row,15)
        self.MD_unit_abbrev      = row[16].strip()
        self.survey_start_date   = row[17].strip()
        self.survey_end_date     = row[18].strip()
        self.sidetrack           = row[19].strip()
        self.TP_WOBJREF          = safe_cast_to_int(row,20)
        self.kickoff_depth       = safe_cast_to_float(row,21)
        self.parent_SURVEYREF    = safe_cast_to_int(row,22)


    ### Add information from Survey Detail record
    def set_rec_Survey_Details (self, row):  # from H7,1,4,0 Survey Details
        logging.debug("SET SURVEY DETAILS ROW: %s", row[:5])
        self.SurveyDetail_row  = row.copy()
        ### Check consistency of SURVEYREF
        if self.SURVEYREF!=safe_cast_to_int(row,5):
            logging.error("Inconsistent references to SURVEYREF in Detail")
        self.MD_UNITREF                = safe_cast_to_int(row,6)
        self.MD_type_ID                = safe_cast_to_int(row,7)
        self.MD_type_name              = row[8].strip()
        self.MD_type_flag              = safe_cast_to_int(row,9)
        self.MD_type_flag_name         = row[10].strip()
        self.INC_type_flag             = safe_cast_to_int(row,11)
        self.AZ_type_ID                = safe_cast_to_int(row,12)
        self.AZ_type_name              = row[13].strip()
        self.AZ_type_flag              = safe_cast_to_int(row,14)
        self.AZ_type_flag_name         = row[15].strip()
        self.convergence_applied_flag  = safe_cast_to_int(row,16)
        self.convergence_applied_value = safe_cast_to_float(row,17)
        self.declination_applied_flag  = safe_cast_to_int(row,18)
        self.declination_applied_value = safe_cast_to_float(row,19)
        self.geomag_parameters_date    = row[20].strip()
        self.MAGREF                    = safe_cast_to_int(row,21)
        self.GRAVREF                   = safe_cast_to_int(row,22)


    ### Parse other records related to survey
	### Operator/Contractor
    def set_rec_Operator_Survey_Contractor(self, row):
        self.well_operator                = row[6].strip()
        self.survey_contractor            = row[7].strip()
        self.survey_contractor_job_number = row[8].strip()


# TP info must come from referenced self.TP_WOBJREF
#    ### Add information from Survey Tie Point Detail record
#    def set_rec_Survey_Tie_Point_Details (self, row):  # from H7,1,4,1 Survey Tie Point Details
#        logging.debug("SET Tie-Point DETAILS ROW: %s", row[:5])
#        self.SurveyTPDetail_row  = row.copy()
#
#        logging.error("NEED TO CHANGE THIS TO P7TABLEREF and get the SURVEY perhaps or somehow...")
#        self.TP_P7TABLEREF      = safe_cast_to_int(row,5)
#
#        ### Check consistency of SURVEYREF
#        if self.SURVEYREF!=safe_cast_to_int(row,5):
#            logging.error("Inconsistent references to SURVEYREF in TP Detail")
#        self.TP_MD             = safe_cast_to_float(row,6)
#        self.TP_n              = safe_cast_to_float(row,7)
#        self.TP_e              = safe_cast_to_float(row,8)
#        self.TP_TVDZDP         = safe_cast_to_float(row,9)  ### BOEMRE MMS publication indicates TVD below Reference point (ZDP)


    ### Geomagnetic and Gravity Model:
	### One first pass of the file create a dict associating the REF with the row.
	### Then later use this function to parse the row for each survey and assign the attributes.
    def set_rec_Geomagnetic_Model_Definition(self, row):
        logging.debug("SET geomagnetic model ROW: %s", row[:5])
        self.MAGREF            = safe_cast_to_int(row,5)
        self.geomag_strategy   = row[6].strip()
        self.geomag_model_name = row[7].strip()
        self.geomag_model_year = row[8].strip()
        self.geomag_ifr_source = row[9].strip()

    def set_rec_Gravity_Model_Definition(self, row):
        logging.debug("SET gravimetric model ROW: %s", row[:5])
        self.GRAVREF                    = safe_cast_to_int(row,5)
        self.gravity_model_name         = row[6].strip()

    ### Handle optional Raw MWD extension records: only required if additional columns in M7
    def set_rec_M7_Record_Extension_Definition(self, row):
        logging.debug("Set M7 extension field ROW: %s", row[:5])
        ### Check row
        key = safe_cast_to_int(row,5)
        if key != self.SURVEYREF:
            logging.critical("something went wrong that should never have gone wrong")
        self.rawmwd_num_extension_fields = safe_cast_to_int(row,6)
        # assume: "f1,f2,f3,f4,f5,f6, 3, 1;;var_N;1, 2;;var_E;1, 3;;var_D;1" where first "3" is rawmwd_num_extension_fields
        if self.rawmwd_num_extension_fields<0:
            log.warning("Blank found.  It is mandatory to specify \">0\" for the number of extension fields")
            self.rawmwd_num_extension_fields=0
        if self.rawmwd_num_extension_fields==0:
            log.error("there is no point in defining MWD Raw extension field record without extension fields")
        for i in range(self.rawmwd_num_extension_fields):
            tmp = row[7+i].strip().split(';') # 4 subfields of extension
            header = tmp[2]
            u_ref  = safe_cast_to_int(tmp[3])
            u_name = dictUNITREF[u_ref]
            self.rawmwd_headers.append(header)
            self.rawmwd_units.append(u_name)

    ### Handle optional Raw Gyro extension records: only required if additional columns in G7
    def set_rec_G7_Record_Extension_Definition(self, row):
        logging.debug("Set G7 extension field ROW: %s", row[:5])
        ### Check row
        key = safe_cast_to_int(row,5)
        if key != self.SURVEYREF:
            logging.critical("something went wrong that should never have gone wrong")
        self.rawgyro_num_extension_fields = safe_cast_to_int(row,6)
        # assume: "f1,f2,f3,f4,f5,f6, 3, 1;;var_N;1, 2;;var_E;1, 3;;var_D;1" where first "3" is rawgyro_num_extension_fields
        if self.rawgyro_num_extension_fields<0:
            log.warning("Blank found.  It is mandatory to specify \">0\" for the number of extension fields")
            self.rawgyro_num_extension_fields=0
        if self.rawgyro_num_extension_fields==0:
            log.error("there is no point in defining MWD Raw extension field record without extension fields")
        for i in range(self.rawgyro_num_extension_fields):
            tmp = row[7+i].strip().split(';') # 4 subfields of extension
            header = tmp[2]
            u_ref  = safe_cast_to_int(tmp[3])
            u_name = dictUNITREF[u_ref]
            self.rawgyro_headers.append(header)
            self.rawgyro_units.append(u_name)

    ### Handle optional M7 records (append data to rawmwd_data table)
    def set_rec_M7_MWD_Raw_Sensor_Data_Record(self, row):
        logging.debug("set_rec_M7_MWD_Raw_Sensor_Data_Record ROW: %s", row[:5])
        ### Check row
        key = safe_cast_to_int(row,2)
        if key != self.SURVEYREF:
            logging.critical("something went wrong that should never have gone wrong.")
        ### Append row
        self.rawmwd_data.append(row)
        ### Check consistent type.  Compare first line with current row
        if self.rawmwd_data[0][0]!=row[0]: # e.g., "M7" or "G7"
            logging.error('inconsistent types M7 and G7 referenced to same survey.  That is not possible.')

    ### Handle optional G7 records (append data to rawgyro_data table)
    def set_rec_G7_Gyro_Raw_Sensor_Data_Record(self, row):
        logging.debug("set_rec_G7_Gyro_Raw_Sensor_Data_Record ROW: %s", row[:5])
        ### Check row
        key = safe_cast_to_int(row,2)
        if key != self.SURVEYREF:
            logging.critical("something went wrong that should never have gone wrong.")
        ### Append row
        self.rawgyro_data.append(row)
        ### Check consistent type.  Compare first line with current row
        if self.rawgyro_data[0][0]!=row[0]: # e.g., "M7" or "G7"
            logging.error('inconsistent types M7 and G7 referenced to same survey.  That is not possible.')

    ### Record writers - requires a file handler to an open ascii file
    def write_rec_Survey_Definition(self, outfh):
        logging.debug("write_rec_Survey_Definition")
        rec_fmt = dict_record_spec[rec_Survey_Definition][1][2].replace("BLANK",'')
        f1,f2,f3,f4,f5 = rec_Survey_Definition
        f6  = self.SURVEYREF
        f7  = self.WELLBOREREF
        f8  = self.ZDPREF
        f9  = self.survey_name
        f10 = self.MTTYPE_name
        f11 = self.MTREF
        f12 = self.hole_type
        f13 = self.hole_diameter_list
        f14 = self.run_direction
        f15 = self.MD_start
        f16 = self.MD_end
        f17 = self.MD_unit_abbrev
        f18 = self.survey_start_date
        f19 = self.survey_end_date
        f20 = self.sidetrack
        f21 = self.TP_WOBJREF
        f22 = self.kickoff_depth
        f23 = self.parent_SURVEYREF
        outfh.write(rec_fmt.format(f1,f2,f3,f4,f5, f6,f7,f8,f9,f10,f11,f12,f13,f14,f15,f16,f17,f18,f19,f20,f21,f22,f23))
        outfh.write("\n")


    ### P7 Specific Header records
    def write_rec_Survey_Details(self, outfh):
        logging.debug("write_rec_Survey_Details")
        rec_fmt = dict_record_spec[rec_Survey_Details][1][2].replace("BLANK",'')
        f1,f2,f3,f4,f5 = rec_Survey_Details
        f6  = self.SURVEYREF
        f7  = self.MD_UNITREF
        f8  = self.MD_type_ID
        f9  = self.MD_type_name
        f10 = self.MD_type_flag
        f11 = self.MD_type_flag_name
        f12 = self.INC_type_flag
        f13 = self.AZ_type_ID
        f14 = self.AZ_type_name
        f15 = self.AZ_type_flag
        f16 = self.AZ_type_flag_name
        f17 = self.convergence_applied_flag
        f18 = self.convergence_applied_value
        f19 = self.declination_applied_flag
        f20 = self.declination_applied_value
        f21 = self.geomag_parameters_date
        f22 = self.MAGREF
        f23 = self.GRAVREF
#        f24 = self.gravity_value
#        ### there must be an easier way... to replace BLANK with '' string if there is no valid float or int...
#        if self.gravity_value<0:
#            f24        = ''
#            q          = rec_fmt.split(',')
#            q[23]      = '{}'
#            rec_fmt    = ','.join(q)
        outfh.write(rec_fmt.format(f1,f2,f3,f4,f5, f6,f7,f8,f9,f10,f11,f12,f13,f14,f15,f16,f17,f18,f19,f20,f21,f22,f23))
        outfh.write("\n")

	###
    def write_rec_Operator_Survey_Contractor(self, outfh):
        logging.debug("write_rec_Operator_Survey_Contractor")
        rec_fmt = dict_record_spec[rec_Operator_Survey_Contractor][1][2].replace("BLANK",'')
        f1,f2,f3,f4,f5 = rec_Operator_Survey_Contractor
        f6  = self.SURVEYREF
        f7  = self.well_operator
        f8  = self.survey_contractor
        f9  = self.survey_contractor_job_number
        outfh.write(rec_fmt.format(f1,f2,f3,f4,f5, f6,f7,f8,f9))
        outfh.write("\n")


    ###
    def write_rec_Geomagnetic_Model_Definition(self, outfh):
        logging.debug("write_rec_Geomagnetic_Model_Definition")
        rec_fmt = dict_record_spec[rec_Geomagnetic_Model_Definition][1][2].replace("BLANK",'')
        f1,f2,f3,f4,f5 = rec_Geomagnetic_Model_Definition
        f6  = self.MAGREF
        f7  = self.geomag_strategy
        f8  = self.geomag_model_name
        f9 = self.geomag_model_year
        f10 = self.geomag_ifr_source
        outfh.write(rec_fmt.format(f1,f2,f3,f4,f5, f6,f7,f8,f9,f10))
        outfh.write("\n")

    ### this requires some work - may well be optional/not required if not raw sensor data
    def write_rec_Gravity_Model_Definition(self, outfh):
        logging.debug("write_rec_Gravity_Model_Definition")
        rec_fmt = dict_record_spec[rec_Gravity_Model_Definition][1][2].replace("BLANK",'')
        f1,f2,f3,f4,f5 = rec_Gravity_Model_Definition
        f6  = self.GRAVREF
        f7  = self.gravity_model_name
        outfh.write(rec_fmt.format(f1,f2,f3,f4,f5, f6,f7))
        outfh.write("\n")

    ### M7 Data records
    def write_rec_M7_MWD_Raw_Sensor_Data_Record(self, outfh):
        logging.debug("write_rec_M7_MWD_Raw_Sensor_Data_Record")
        rec_fmt = dict_record_spec[rec_M7_MWD_Raw_Sensor_Data_Record][1][2].replace("BLANK",'')
        f1  = rec_M7_MWD_Raw_Sensor_Data_Record[0]
        for row in self.rawmwd_data:
            f2  = safe_cast_to_int(row,1)    #record version
            f3  = safe_cast_to_int(row,2)    #SURVEYREF
            f4  = safe_cast_to_int(row,3)    #data rec number
            f5  = row[4].strip()             #datetime
            f6  = safe_cast_to_int(row,5)    #transmission flag
            f7  = safe_cast_to_int(row,6)    #used flag
            f8  = safe_cast_to_float(row,7)  #MD
            f9  = safe_cast_to_float(row,8)  #INC
            f10 = safe_cast_to_float(row,9)  #AZ
            f11 = safe_cast_to_float(row,10) #n
            f12 = safe_cast_to_float(row,11) #e
            f13 = safe_cast_to_float(row,12) #d
            f14 = safe_cast_to_float(row,13) #Gx
            f15 = safe_cast_to_float(row,14) #Gy
            f16 = safe_cast_to_float(row,15) #Gz
            f17 = safe_cast_to_float(row,16) #Bx
            f18 = safe_cast_to_float(row,17) #By
            f19 = safe_cast_to_float(row,18) #Bz
            f20 = safe_cast_to_float(row,19) #GravTF
            f21 = safe_cast_to_float(row,20) #MagTF
            f22 = safe_cast_to_float(row,21) #Gtot
            f23 = safe_cast_to_float(row,22) #Btot
            f24 = safe_cast_to_float(row,23) #Tooldip
            f25 = safe_cast_to_float(row,24) #refGtot
            f26 = safe_cast_to_float(row,25) #refBtot
            f27 = safe_cast_to_float(row,26) #refDip
            f28 = safe_cast_to_float(row,27) #decl
            f29 = safe_cast_to_float(row,28) #conv
            f30 = '' # write last mandatory comma

            outfh.write(rec_fmt.format(f1,f2,f3,f4,f5, f6,f7,f8,f9,f10,f11,f12,f13,f14,f15,f16,f17,f18,f19,f20,f21,f22,f23,f24,f25,f26,f27,f28,f29,f30))

            ### format: "M7,...,427764.51,3214.00, 59.7555558,1.7144222, 97; 98; 99" (where last field is the extension field)
            for v in row[29:]:
                outfh.write(v)
                if v!=row[-1]: outfh.write(";")   # use semi-column but don't put it after last value
            outfh.write("\n")


    ### G7 Data records
    def write_rec_G7_Gyro_Raw_Sensor_Data_Record(self, outfh):
        logging.debug("write_rec_G7_Gyro_Raw_Sensor_Data_Record")
        rec_fmt = dict_record_spec[rec_G7_Gyro_Raw_Sensor_Data_Record][1][2].replace("BLANK",'')
        f1  = rec_G7_Gyro_Raw_Sensor_Data_Record[0]
        for row in self.rawgyro_data:
            f2  = safe_cast_to_int(row,1)    #record version
            f3  = safe_cast_to_int(row,2)    #SURVEYREF
            f4  = safe_cast_to_int(row,3)    #data rec number
            f5  = row[4].strip()             #datetime
            f6  = safe_cast_to_int(row,5)    #used flag
            f7  = safe_cast_to_float(row,6)  #MD
            f8  = safe_cast_to_float(row,7)  #INC
            f9  = safe_cast_to_float(row,8)  #AZ
            f10 = safe_cast_to_float(row,9)  #n
            f11 = safe_cast_to_float(row,10) #e
            f12 = safe_cast_to_float(row,11) #d
            f13 = safe_cast_to_float(row,12) #Gx
            f14 = safe_cast_to_float(row,13) #Gy
            f15 = safe_cast_to_float(row,14) #Gz
            f16 = safe_cast_to_float(row,15) #Wx
            f17 = safe_cast_to_float(row,16) #Wy
            f18 = safe_cast_to_float(row,17) #Wz
            f19 = safe_cast_to_float(row,18) #GravTF
            f20 = safe_cast_to_float(row,19) #GyroTF
            f21 = safe_cast_to_float(row,20) #Gtot
            f22 = safe_cast_to_float(row,21) #Lat
            f23 = safe_cast_to_float(row,22) #TotER
            f24 = safe_cast_to_float(row,23) #refGtot
            f25 = safe_cast_to_float(row,24) #refLat
            f26 = safe_cast_to_float(row,25) #refER
            f27 = safe_cast_to_float(row,26) #conv
            f28 = '' # write last mandatory comma

            outfh.write(rec_fmt.format(f1,f2,f3,f4,f5, f6,f7,f8,f9,f10,f11,f12,f13,f14,f15,f16,f17,f18,f19,f20,f21,f22,f23,f24,f25,f26,f27,f28))

            ### format: "G7,...,427764.51,3214.00, 59.7555558,1.7144222, 97; 98; 99" (where last field is the extension field)
            for v in row[27:]:
                outfh.write(v)
                if v!=row[-1]: outfh.write(";")   # use semi-column but don't put it after last value
            outfh.write("\n")



    #####################################################################################
    ### Not very pythonic...  remove?
    ### Assign a Structure object to this survey
    def set_structure(self, STRUCTURE):
        logging.debug("SURVEY set_structure")
        self.Structure = STRUCTURE
    ### Assign a well object to this survey
    def set_well(self, WELL):
        logging.debug("SURVEY set_well")
        self.Well = WELL
    ### Assign a wellbore object to this survey
    def set_wellbore(self, WELLBORE):
        logging.debug("SURVEY set_wellbore")
        self.Wellbore = WELLBORE
    ### Assign a well object to this survey
    def set_rig(self, RIG):
        logging.debug("SURVEY set_rig")
        self.Rig = RIG

    ### Do some internal consistency checks on the format, after all records are parsed
    def do_survey_cross_checks(self):
        #logging.debug("do some checks here like same reference to same objects; fields filled out; etc.")
        logging.warning("dont forget... implement some cross-checks here like same reference to same objects; fields filled out; etc.")
        # zdp md units from rig and survey
        #if self.MD_UNITREF!=self.Rig.ZDP_UNITREF:
        #    logging.error("Survey MD units are not the same as Rig ZDP units") # I guess, it could be different...?
        # height from GL TO KB?

        # same structure referenced from rig as from well
        #if self.Rig.STRUCTUREREF!=self.Structure.STRUCTUREREF:
        #    logging.error("Survey points to different structure than Rig")
        #if self.Rig.STRUCTUREREF!=self.Well.STRUCTUREREF:
        #    logging.error("Well points to different structure than Rig")





####################################################################
### P7TABLE: metadata and format for calculated coordinates in the P7 records
###
### Bert Kampes, 2018-08-10
####################################################################
class P7TABLE:

    ### Constructor based on H7,5,0,0 P7 Table Definition
    def __init__ (self, row=None):

        ### Create a dummy row if none is passed to fill/construct
		### Note in this case the row contains two more fields due to the three additional record extension fields defined.
        if row is None:
            row = "H7,5,0,0,P7 Table Definition,1,Definitive Composite,1,Minimum Curvature,1076,LMP,0,,0, 3, 1;;var_N;1, 2;;var_E;1, 3;;var_D;1".split(",")

        logging.debug("P7TABLE CONSTRUCTOR: %s", row[:5])
        self.row                  = row.copy()
        self.extension_fields     = []

        ### Initialize Header (note geogCRS can be grad, append extension fields; and units still to be set.
        self.p7table_headers = ['MD',     'INC', 'AZ',   'n',   'e',     'd',    'Northing', 'Easting', 'Depth', 'Latitude', 'Longitude']
        self.p7table_units   = ['MDunit', 'deg', 'deg',  'MDunit', 'MDunit', 'MDunit', 'projCRSunit', 'projCRSunit', 'vertCRSunit', 'deg', 'deg']
        self.p7table_data    = []

        ### Parse constructor row
        self.P7TABLEREF           = safe_cast_to_int(row,5)
        self.p7table_description  = row[6].strip()
        self.MDINCAZ2LOCAL_code   = safe_cast_to_int(row,7)
        self.MDINCAZ2LOCAL_name   = row[8].strip()
        self.LOCAL2GLOBAL_code    = safe_cast_to_int(row,9)
        self.LOCAL2GLOBAL_name    = row[10].strip()
        self.sf_correction_code   = safe_cast_to_int(row,11)
        self.sf_correction_value  = safe_cast_to_float(row,12)
        self.ef_correction_code   = safe_cast_to_int(row,13)
        self.num_extension_fields = safe_cast_to_int(row,14)
        #print("f16", self.extension_fields, row[15:]) #debug
        self.extension_fields     = row[15:] # format: "1;;var_N;1,  2;;var_E;1,  3;;var_D;1"   store f17,f18,..

        # create column header and unit header and deal with extension field
        # each extension field is "ID#; cond; description; UNITREF"
        # i.e., it can be "split(";") in 4 fields
        if self.num_extension_fields<0:
            log.warning("Blank found.  It is mandatory to specify \"0\" for the number of extension fields if there are none")
            self.num_extension_fields=0

        # example: "f1,f2,...,f14, 3, 1;;var_N;1, 2;;var_E;1, 3;;var_D;1" where first "3" is num_extension_fields
        for i in range(self.num_extension_fields):
            logging.debug("row[15+i]: %s", row[15+i])
            tmp    = row[15+i].strip().split(';') # 4 subfields of extension separated by semi-column
            header = tmp[2]
            u_ref  = safe_cast_to_int(tmp,3)
            u_name = dictUNITREF[u_ref]
            self.p7table_headers.append(header)
            self.p7table_units.append(u_name)


    ### Handle P7 records
    def set_rec_P7_Data_Record(self, row):
        logging.debug("set_rec_P7_Data_Record")
        ### Parse row of a P7 Table
        #self.record_version   = safe_cast_to_int(row,1)
        key = safe_cast_to_int(row,2)
        if key != self.P7TABLEREF:
            logging.critical("something went wrong that should never have gone wrong")
        self.p7table_data.append(row)

        # pnt_SURVEYREF    = safe_cast_to_int(row,3)
        # pnt_STEMREF      = safe_cast_to_int(row,4)
        # pnt_STEMREF_name = row[5].strip()
        # #pnt_WOBJREF      = row[6].strip()
        # pnt_name         = row[7].strip()
        # pnt_status_id    = row[8].strip()
        # pnt_status       = row[9].strip()
        # #
        # MDINCAZ_obs  = [row[10].strip(), row[11].strip(), row[12].strip()]
        # error_model  = [row[13].strip(), row[14].strip()] #14 can be blank, else woudl be STEMREF integer
        # localNED     = [row[15].strip(), row[16].strip(), row[17].strip()]
        # CRS_A_coords = [row[18].strip(), row[19].strip(), row[20].strip()]
        # CRS_B_coords = [row[21].strip(), row[22].strip()]
        # ### Additional columns...
        # #if additional fields ..
            # #append.

        # relevant_fields = MDINCAZ_obs + localNED + CRS_A_coords + CRS_B_coords + [pnt_name, pnt_status]
        # self.p7table_data.append(relevant_fields) # data table (appended row by row for this survey)

    ### call this function once for each P7 Table to fix MDunit etc. after first pass
    def set_column_headers(self, Project):
        self.p7table_headers = ['MD',     'INC', 'AZ',   'n',   'e',     'd',    'Northing', 'Easting', 'Depth', 'Latitude', 'Longitude']
        self.p7table_units   = ['MDunit', 'deg', 'deg',  'MDunit', 'MDunit', 'MDunit', 'projCRSunit', 'projCRSunit', 'vertCRSunit', 'deg', 'deg']
        log.warning("to do more")

    ### Writer for p717 records
    def write_rec_P7_Table_Definition(self, outfh):
        logging.debug("write_rec_P7_Table_Definition")
        rec_fmt = dict_record_spec[rec_P7_Table_Definition][1][2].replace("BLANK",'')
        f1,f2,f3,f4,f5 = rec_P7_Table_Definition
        f6  = self.P7TABLEREF
        f7  = self.p7table_description
        f8  = self.MDINCAZ2LOCAL_code
        f9  = self.MDINCAZ2LOCAL_name
        f10 = self.LOCAL2GLOBAL_code
        f11 = self.LOCAL2GLOBAL_name
        f12 = self.sf_correction_code
        f13 = self.sf_correction_value
        f14 = self.ef_correction_code
        f15 = self.num_extension_fields
        f16 = ''
        outfh.write(rec_fmt.format(f1,f2,f3,f4,f5, f6,f7,f8,f9,f10,f11,f12,f13,f14,f15,f16))
        #this writes a last comma, but not yet the possible extension fields
        #there is a mandatory last comma in front of f17 extension field which internally is semi-column separated.
        #format: "f1,f2,...,f15, 3, 1;;var_N;1, 2;;var_E;1, 3;;var_D;1" where first "3" is num_extension_fields
        for extension_field in self.extension_fields:
            outfh.write(extension_field)
            if extension_field!=self.extension_fields[-1]: outfh.write(",")  # dont write a comma at very end
        outfh.write("\n")

    ### P7 Data records
    def write_rec_P7_Data_Record(self, outfh):
        logging.debug("write_rec_P7_Data_Record")
        rec_fmt = dict_record_spec[rec_P7_Data_Record][1][2].replace("BLANK",'')
        f1  = rec_P7_Data_Record[0]
        for row in self.p7table_data:
            f2  = safe_cast_to_int(row,1)
            f3  = safe_cast_to_int(row,2) #P7TABLEREF
            f4  = safe_cast_to_int(row,3) #SURVEYREF
            f5  = safe_cast_to_int(row,4) #STEMREF
            f6  = row[5].strip()
            f7  = safe_cast_to_int(row,6) #WOBJREF
            f8  = row[7].strip()          #WOBJTYPE
            f9  = safe_cast_to_int(row,8) #WOBJSTATUS
            f10 = row[9].strip()
            f11 = safe_cast_to_float(row,10) #MD
            f12 = safe_cast_to_float(row,11) #INC
            f13 = safe_cast_to_float(row,12) #AZ
            f14 = safe_cast_to_float(row,13) #n
            f15 = safe_cast_to_float(row,14) #e
            f16 = safe_cast_to_float(row,15) #d
            f17 = safe_cast_to_float(row,16) #coord1
            f18 = safe_cast_to_float(row,17) #coord2
            f19 = safe_cast_to_float(row,18) #coord3
            f20 = safe_cast_to_float(row,19) #coord1
            f21 = safe_cast_to_float(row,20) #coord2
            f22 = '' # write last mandatory comma

            outfh.write(rec_fmt.format(f1,f2,f3,f4,f5, f6,f7,f8,f9,f10,f11,f12,f13,f14,f15,f16,f17,f18,f19,f20,f21,f22))

            ### Add optional extension fields, semi-column separated
            ### format: "P7,...,427764.51,3214.00, 59.7555558,1.7144222, 97; 98; 99" (where last field is the extension field)
            for v in row[21:]:
                outfh.write(v)
                if v!=row[-1]: outfh.write(";")   # use semi-column but don't put it after last value
            outfh.write("\n")

###
# +++ set the data_header_columns and data_unit_columns
            # self.ProjectCRS_CRSREF     = tmpPOSLOGTYPE.CRSREF_PROJECTED_A
            # self.ProjectCRS_name       = dictCRS[self.ProjectCRS_CRSREF].get_crs_name()
            # self.ProjectCRS_axes       = dictCRS[self.ProjectCRS_CRSREF].CS_axes_names  # dict 1,2,3
            # self.ProjectCRS_units      = dictCRS[self.ProjectCRS_CRSREF].CS_axes_units # dict 1,2,3
            # self.ProjectCRSgeog_CRSREF = tmpPOSLOGTYPE.CRSREF_GEODETIC_B
            # self.ProjectCRSgeog_axes   = dictCRS[self.ProjectCRSgeog_CRSREF].CS_axes_names  # dict 1,2
            # self.ProjectCRSgeog_units  = dictCRS[self.ProjectCRSgeog_CRSREF].CS_axes_units # dict 1,2
            # self.CRSREF_hor_local    = tmpPOSLOGTYPE.CRSREF_hor_local
            # self.CRSREF_vert_local   = tmpPOSLOGTYPE.CRSREF_vert_local # ZDP down in m or ft - really needed so complicated?

    ### debug print to screen
    def print_p7table(self):
        print("Project CRS: ", self.ProjectCRS_CRSREF)
        print("")
        for row in self.p7table_headers:
            print(row)
        print("------------------------------------------------------------------------")
        for row in self.p7table_data:
            print(row)
        print("")

    ### Write P7 Table to report file
    def report_p7table(self, outfh):
        #outfh.write("Project CRS: {} {}\n".format(self.ProjectCRS_CRSREF, self.ProjectCRS_name))
        outfh.write("Project CRS: {} {}\n".format("unkn", "unkn"))
        outfh.write("\n")
        #self.p7table_headers = ['MD',     'INC', 'AZ',   'n',   'e',     'd',    'Northing', 'Easting', 'Depth', 'Latitude', 'Longitude']
        #self.p7table_units   = ['MDunit', 'deg', 'deg',  'MDunit', 'MDunit', 'MDunit', 'projCRSunit', 'projCRSunit', 'vertCRSunit', 'deg', 'deg']
        #for row in self.p7table_headers:
        row = self.p7table_headers
        outfh.write("{:8} {:5} {:6} {:7} {:7} {:8} {:10} {:10} {:7} {:11} {:12}\n".format(
                         row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10]))
        row = self.p7table_units
        outfh.write("{:8} {:5} {:6} {:7} {:7} {:8} {:10} {:10} {:7} {:11} {:12}\n".format(
                         row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10]))
        outfh.write("------------------------------------------------------------------------\n")
        for row in self.p7table_data:
            outfh.write("{:8.2f} {:5.2f} {:6.2f} {:7.2f} {:7.2f} {:8.2f} {:10.2f} {:10.2f} {:7.2f} {:11.7f} {:12.7f} {} {}\n".format(
                          safe_cast_to_float(row,10),  safe_cast_to_float(row,11),  safe_cast_to_float(row,12),
                          safe_cast_to_float(row,13),  safe_cast_to_float(row,14),  safe_cast_to_float(row,15),
                          safe_cast_to_float(row,16),  safe_cast_to_float(row,17),  safe_cast_to_float(row,18),
                          safe_cast_to_float(row,19),  safe_cast_to_float(row,20),
                         row[7], row[9]))
        outfh.write("\n")



### EOF.