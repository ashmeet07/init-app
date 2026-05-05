#include <stdio.h>
#include <string.h>
#include "engine.h"
#include "../platform/actions.h"
#include "../utils.h"

int run_engine(const char *config_path) {
    if (check_python() != SUCCESS) {
        printf("[!] Critical: Python environment not detected.\n");
        return ERROR;
    }

    FILE *f = fopen(config_path, "r");
    if (!f) {
        printf("[!] Error: Could not open config file: %s\n", config_path);
        return ERROR;
    }

    char line[1024];
    while (fgets(line, sizeof(line), f)) {
        trim_newline(line);
        
        // Skip empty lines or comments
        if (line[0] == '\0' || line[0] == '#') continue;

        if (starts_with(line, "COMMAND=")) {
            char *cmd = line + 8;
            printf("[Action] Executing: %s\n", cmd);
            run_command(cmd);
        } 
        else if (starts_with(line, "FILE=")) {
            char *data = line + 5;
            char *sep = strchr(data, '|');
            if (sep) {
                *sep = '\0';
                char *filename = data;
                char *content = sep + 1;
                printf("[Action] Creating: %s\n", filename);
                generate_file(filename, content);
            }
        }
    }

    fclose(f);
    return SUCCESS;
}