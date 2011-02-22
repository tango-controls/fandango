/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#ifndef _YAT_PLUGINTYPES_H_
#define _YAT_PLUGINTYPES_H_

#include <map>
#include <string>
#include <vector>
#include <yat/CommonHeader.h>
#include <yat/Callback.h>
#include <yat/GenericContainer.h>
#include <yat/Any.h>

namespace yat
{

YAT_DEFINE_CALLBACK ( SetAttrCB, const yat::Any&  );
YAT_DEFINE_CALLBACK ( GetAttrCB, yat::Any& );

struct PlugInDataType
{ 
  enum
  {
    BOOLEAN,
    UCHAR,
    SHORT,
    USHORT,
    LONG,
    FLOAT,
    DOUBLE,
    STRING
  };
};

struct PlugInAttrWriteType
{ 
  enum
  {
  READ,
    WRITE,
    READ_WRITE
  };
};

class PlugInAttrInfo
{
public:
  std::string name;
  int data_type;
  int write_type;

  std::string label;
  std::string desc;
  std::string unit;
  std::string display_format;

  SetAttrCB set_cb;
  GetAttrCB get_cb;
};

typedef std::vector<PlugInAttrInfo> PlugInAttrInfoList;

struct PlugInPropType
{
  enum
  {
    _UNDEFINED = -1,
    BOOLEAN,
    SHORT,
    UCHAR,
    USHORT,
    LONG,
    ULONG,
    FLOAT,
    DOUBLE,
    STRING,
    STRING_VECTOR,
    SHORT_VECTOR,
    USHORT_VECTOR,
    LONG_VECTOR,
    ULONG_VECTOR,
    FLOAT_VECTOR,
    DOUBLE_VECTOR
  };
};

typedef std::map<std::string , int> PlugInPropInfos;
typedef std::map<std::string , yat::Any> PlugInPropValues;

} // namespace

#include <yat/plugin/PlugInTypes.tpp>

#endif
