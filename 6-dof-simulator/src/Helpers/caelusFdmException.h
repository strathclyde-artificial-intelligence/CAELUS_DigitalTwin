/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */
/*
------ Copyright (C) 2017 University of Strathclyde and Authors ------
-------------------- e-mail: c.greco@strath.ac.uk --------------------
----------------------- Author: Cristian Greco -----------------------
*/

#ifndef CAELUSFDM_EXCEPTION_H
#define CAELUSFDM_EXCEPTION_H

#include <exception>
#include <cassert>
#include <iostream>
#include <string>

#define _CAELUSFDM_EXCEPTION_QUOTEME(x) #x
#define CAELUSFDM_EXCEPTION_QUOTEME(x) _CAELUSFDM_EXCEPTION_QUOTEME(x)
#define CAELUSFDM_EXCEPTION_EXCTOR(s) ((std::string(__FILE__ "," CAELUSFDM_EXCEPTION_QUOTEME(__LINE__) ": ") + s) + ".")
#define CAELUSFDM_EX_THROW(s) (throw CAELUSFDM_EXCEPTION(CAELUSFDM_EXCEPTION_EXCTOR(s)))

#define caelusfdm_throw(s) CAELUSFDM_EX_THROW(s)

namespace caelus_fdm{
    class CAELUSFDM_EXCEPTION: public std::exception {
    public:
        CAELUSFDM_EXCEPTION(const std::string &s):m_what(s) {}
        virtual const char *what() const throw() {
            return m_what.c_str();
        }
        virtual ~CAELUSFDM_EXCEPTION() throw() {}
    protected:
        std::string m_what;
    };
} // namespace caelusfdm

#endif //CAELUSFDM_EXCEPTION_H
