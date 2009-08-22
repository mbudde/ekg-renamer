
#include "fx.h"

int main(int argc, char *argv[]) {
  FXApp application("Hello", "FoxTest");
  application.init(argc, argv);
  FXMainWindow *main=new FXMainWindow(&application, "Hello", NULL, NULL, DECOR_ALL);
  new FXButton(main, "&Hello, World!", NULL, &application, FXApp::ID_QUIT);
  application.create();
  main->show(PLACEMENT_SCREEN);
  return application.run();
}

