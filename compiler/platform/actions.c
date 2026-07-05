#include <stdio.h>
#include <stdlib.h>
#include "actions.h"
#include "../utils.h"

#ifdef _WIN32
    #include <direct.h>
    #define GETCWD _getcwd
#else
    #include <unistd.h>
    #define GETCWD getcwd
#endif

int run_command(const char *cmd) {
    return system(cmd);
}

int generate_file(const char *filename, const char *content) {
    FILE *f = fopen(filename, "w");
    if (!f) {
        perror("File Error");
        return ERROR;
    }
    fputs(content, f);
    fclose(f);
    return SUCCESS;
}

int check_python() {
    const char* cmd = 
#ifdef _WIN32
        "python --version >nul 2>&1 || py --version >nul 2>&1";
#else
        "python3 --version >/dev/null 2>&1 || python --version >/dev/null 2>&1";
#endif
    return (system(cmd) == 0) ? SUCCESS : ERROR;
}

void get_curr_dir(char *buf, int size) {
    if (buf && size > 0) {
        GETCWD(buf, size);
    }
}
