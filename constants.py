
import struct

GADGET_MESSAGE_INT_ID_MIN                             =   0
GADGET_MESSAGE_CONFIG_FILE                            =   1
GADGET_MESSAGE_CONFIG_SCRIPT                          =   2
GADGET_MESSAGE_PARAMETER_SCRIPT                       =   3
GADGET_MESSAGE_CLOSE                                  =   4
GADGET_MESSAGE_INT_ID_MAX                             = 999
GADGET_MESSAGE_EXT_ID_MIN                             = 1000
GADGET_MESSAGE_ACQUISITION                            = 1001 # DEPRECATED
GADGET_MESSAGE_NEW_MEASUREMENT                        = 1002 # DEPRECATED
GADGET_MESSAGE_END_OF_SCAN                            = 1003 # DEPRECATED
GADGET_MESSAGE_IMAGE_CPLX_FLOAT                       = 1004 # DEPRECATED
GADGET_MESSAGE_IMAGE_REAL_FLOAT                       = 1005 # DEPRECATED
GADGET_MESSAGE_IMAGE_REAL_USHORT                      = 1006 # DEPRECATED
GADGET_MESSAGE_EMPTY                                  = 1007 # DEPRECATED
GADGET_MESSAGE_ISMRMRD_ACQUISITION                    = 1008
GADGET_MESSAGE_ISMRMRD_IMAGE_CPLX_FLOAT               = 1009
GADGET_MESSAGE_ISMRMRD_IMAGE_REAL_FLOAT               = 1010
GADGET_MESSAGE_ISMRMRD_IMAGE_REAL_USHORT              = 1011
GADGET_MESSAGE_DICOM                                  = 1012
GADGET_MESSAGE_CLOUD_JOB                              = 1013
GADGET_MESSAGE_GADGETCLOUD_JOB                        = 1014
GADGET_MESSAGE_ISMRMRD_IMAGEWITHATTRIB_CPLX_FLOAT     = 1015
GADGET_MESSAGE_ISMRMRD_IMAGEWITHATTRIB_REAL_FLOAT     = 1016
GADGET_MESSAGE_ISMRMRD_IMAGEWITHATTRIB_REAL_USHORT    = 1017
GADGET_MESSAGE_DICOM_WITHNAME                         = 1018
GADGET_MESSAGE_DEPENDENCY_QUERY                       = 1019
GADGET_MESSAGE_EXT_ID_MAX                             = 4096

MAX_BLOBS_LOG_10 = 6

ISMRMRDDataType = struct.Struct('<2f')
SIZEOF_ISMRMRD_DATA_TYPE = len(ISMRMRDDataType.pack(0.0, 0.0))
ISMRMRDTrajectoryType = struct.Struct('<f')
SIZEOF_ISMRMRD_TRAJECTORY_TYPE = len(ISMRMRDTrajectoryType.pack(0.0))

GadgetMessageLength = struct.Struct('<I')
SIZEOF_GADGET_MESSAGE_LENGTH = len(GadgetMessageLength.pack(0))

GadgetMessageIdentifier = struct.Struct('<H')
SIZEOF_GADGET_MESSAGE_IDENTIFIER = len(GadgetMessageIdentifier.pack(0))

GadgetMessageConfigurationFile = struct.Struct('<1024s')
SIZEOF_GADGET_MESSAGE_CONFIGURATION_FILE = len(GadgetMessageConfigurationFile.pack(bytes("","ascii")))

GadgetMessageAttribLength = struct.Struct('<Q')
SIZEOF_GADGET_MESSAGE_ATTRIB_LENGTH = len(GadgetMessageAttribLength.pack(0))

GadgetMessageBlobSize = struct.Struct('<I')
SIZEOF_GADGET_MESSAGE_BLOB_SIZE = len(GadgetMessageBlobSize.pack(0))

GadgetMessageBlobFilename = struct.Struct('<Q')
SIZEOF_GADGET_MESSAGE_BLOB_FILENAME = len(GadgetMessageBlobFilename.pack(0))
