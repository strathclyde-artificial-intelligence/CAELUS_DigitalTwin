#ifndef __PRETTYPRINTABLE_H__
#define __PRETTYPRINTABLE_H__

#include <string>

class PrettyPrintable {
public:
    virtual std::string str() { return std::string("<UNKNOWN_REPRESENTATION>"); };
};

#endif // __PRETTYPRINTABLE_H__