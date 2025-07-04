#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <termios.h>
#include <unistd.h>

struct termios orig_termios;

void disableRawMode(void)  {
        tcsetattr( STDIN_FILENO, TCSAFLUSH, &orig_termios);
}

void enableRawMode(void) {
    tcgetattr(STDERR_FILENO, &orig_termios);
    atexit(disableRawMode);

    struct termios raw = orig_termios;
    raw.c_lflag &= ~(IXON);
    raw.c_lflag &= ~(ECHO | ICANON | ISIG);

    tcsetattr(STDERR_FILENO, TCSAFLUSH, &raw);
}

int main(void) {
    enableRawMode();

    char c;
    while (read(STDIN_FILENO, &c, 1) == 1 && c != 'q'){
        if (iscntrl(c)) {
            printf("%d\n", c);
        } else {
            printf("%d ('%c') \n", c, c);
        }
    }
    return 0;
}
