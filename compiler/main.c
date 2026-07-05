#include <stdio.h>
#include "core/engine.h"

#ifdef _WIN32
    #define COMPILER_BIN "init-app-compiler.exe"
#else
    #define COMPILER_BIN "init-app-compiler"
#endif

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("==================================\n");
        printf(" TECHQUANTA INIT-APP C-ENGINE\n");
        printf("==================================\n");
        printf("Usage: %s <config_file>\n", COMPILER_BIN);
        return 1;
    }

    return run_engine(argv[1]);
}
