#ifndef ACTIONS_H
#define ACTIONS_H

int run_command(const char *cmd);
int generate_file(const char *filename, const char *content);
int check_python();
void get_curr_dir(char *buf, int size);

#endif