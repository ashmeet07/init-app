#include <stdio.h>
#include "core/engine.h"

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("==================================\n");
        printf(" TECHQUANTA INIT-APP C-ENGINE\n");
        printf("==================================\n");
        printf("Usage: compiler.exe <config_file>\n");
        return 1;
    }

    return run_engine(argv[1]);
}