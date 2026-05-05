#ifndef UTILS_H
#define UTILS_H

#include <string.h>

#define SUCCESS 0
#define ERROR   1

static inline int starts_with(const char *str, const char *prefix) {
    return strncmp(str, prefix, strlen(prefix)) == 0;
}

static inline void trim_newline(char *str) {
    // Removes \n and \r for cross-platform compatibility
    str[strcspn(str, "\r\n")] = 0;
}

#endif