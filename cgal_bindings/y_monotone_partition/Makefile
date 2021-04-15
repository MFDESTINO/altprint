# standard compile options for the c++ executable
FLAGS = -fPIC

# the python interface through swig
PYTHONI = -I/usr/include/python3.9
PYTHONL = -Xlinker -export-dynamic

TARGET = y_monotone_partition

# default super-target
all:
	g++ -fPIC -c $(TARGET).cc -o $(TARGET).o
	swig -c++ -python -o $(TARGET)_wrap.cxx $(TARGET).i
	g++ $(FLAGS) $(PYTHONI) -c $(TARGET)_wrap.cxx -o $(TARGET)_wrap.o
	g++ $(PYTHONL) $(LIBFLAGS) -lgmp -shared $(TARGET).o $(TARGET)_wrap.o -o _$(TARGET).so

clean:
	rm $(TARGET)_wrap.cxx
	rm $(TARGET)_wrap.o
	rm $(TARGET).o
	rm _$(TARGET).so
	rm $(TARGET).py
