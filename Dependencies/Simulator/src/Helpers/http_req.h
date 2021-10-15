#ifndef __HTTP_REQ_H__
#define __HTTP_REQ_H__

#include <iostream>
#include <sstream>
#include <string>
#include <curl/curl.h>

using std::cerr;
using std::cout;
using std::endl;
using std::string;
using std::stringstream;

// Ripped from https://troels.arvin.dk/code/examples/curl/curl-example.cpp
class URL {
 private:
    CURL* curl;
    std::string url;

    static size_t curl_callback(void* source_p,size_t size, size_t nmemb, void* dest_p) {
        int realsize=size*nmemb;
        string chunk((char*)source_p,realsize);
        *((stringstream*)dest_p) << chunk;
        return realsize;
    }

    void init_curl() {
        curl = curl_easy_init();
        if (0==curl) {
            cerr << "Couldn't initialize curl" << endl;
            exit(1);
        }
        curl_easy_setopt(curl,CURLOPT_WRITEFUNCTION, curl_callback);
    }

 public:
    URL(std::string arg) {
        init_curl();
        set_url(arg);
    }
    
    ~URL() { curl_easy_cleanup(curl); }
    
    void set_url(std::string arg) {
        url=arg;
        curl_easy_setopt(curl, CURLOPT_URL, arg.c_str());
    }

    std::string get_url() const {
        return url;
    }

    std::string get_body() {
        stringstream ss;
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void *)&ss);
        int err = curl_easy_perform(curl);
        if (err) {
            fprintf(stderr, "Something went wrong while fetching %s\n", this->get_url().c_str());
            return "";
        } else {
            return ss.str();
        }
    }
};

#endif // __HTTP_REQ_H__