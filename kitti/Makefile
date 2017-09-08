##
# Makefile for the Jarvis Lake microbenchmarks.

# Eliminate all default rules.
.SUFFIXES:

# Do not delete intermediate files.
.SECONDARY: $(OBJS)

# Tools.
CC := g++-4.8 
RM := rm -f
ECHO := echo

# Allow builds from a read-only source tree.
#
# $(O_ROOT) must precede all non-phony targets and dependences (without
# a separating slash).

ifeq ($O,)
    O_ROOT :=
else
    O_ROOT := $O/
endif

# Targets.
MICROS := src/yfcc src/kitti
# MICROS := src/yfcc test/concurrent

# Extra stuff to clean whose names cannot be derived from dependences.
CLEANFILES :=

# Translate targets into object file names.
OBJS := $(MICROS:%=$(O_ROOT)%.o)
BINS := $(MICROS:%=$(O_ROOT)%)
CLEANFILES += 

# Where to find Jarvis Lake
JLINCROOT := ../jarvis
JLLIBROOT := ../jarvis
	
BOOST_INCLUDE_DIR = /usr/include/boost
BOOST_LIB_DIR = /home/kspirovs/boost_1_61_0/stage/lib #/usr/local/lib

# Additional places to look for include files.
INCLUDES := -I"$(JLINCROOT)/include" -I"$(JLINCROOT)/util" -Iutil -Iinclude 

# Default optimization level.
OPT ?= -O3

# Omit the frame pointer unless we are profiling.
ifeq ($(findstring -pg,$(OPT)),)
OMIT_FRAME_POINTER := -fomit-frame-pointer
endif

# Optimization and language options.
FFLAGS := $(OMIT_FRAME_POINTER) -funit-at-a-time -finline-limit=2000000 \
	-fno-strict-aliasing -fno-threadsafe-statics
          #-fno-strict-aliasing -fno-rtti -fno-threadsafe-statics

# Warning options.
WFLAGS := -Wall -Wpointer-arith -Wcast-align -Wwrite-strings \
          -Wno-parentheses -Wno-conversion

# Flags for C++ compilation.
CFLAGS := --std=c++11 $(INCLUDES) $(OPT) $(FFLAGS) $(WFLAGS) -MP -MMD

# Jarvis Lake library.
LIBS :=  "$(JLLIBROOT)/lib/jarvis.lib" "$(JLLIBROOT)/lib/jarvis-util.lib" -lrt 

# Sprinkle noise in silent mode.
ifneq ($(findstring s,$(MAKEFLAGS)),)
    print = @$(ECHO) [$(1)] $(2)
endif

# Default goal: build everything.
all: $(BINS) 

clean:
	$(call print,CLEAN)
	$(RM) $(BINS) $(OBJS) $(DEPS) $(CLEANFILES)

# # Rule for building an object file from a C++ file.
# src/%.o: src/%.cc
# 	$(CC) $(CFLAGS) -o $@ -c $<

src/%.o: src/%.cc
	$(CC) $(CFLAGS) $(OPT) -c -o $@ $< $(LIBS)

# test/concurrent.o: src/Chrono.o src/ChronoCpu.o

# Rule for building an object file from a C++ file.
$(O_ROOT)%.o: %.cc $(MAKEFILE_LIST) 
	$(call print,COMPILE,$@)
	$(CC) $(CFLAGS) $(OPT) -o $@ -c $<

# Rule for building a binary from a single object file.
%: %.o
	$(call print,LINK,$@)
	# $(CC) $(OPT) src/Chrono.o src/ChronoCpu.o -o $@ $< $(LIBS)
	$(CC) $(OPT) -o $@ $< -L/usr/lib -L../../boost_1_61_0/stage/lib -lboost_serialization $(LIBS)


# Include dependency information if they are available.
DEPS := $(OBJS:%.o=%.d)
-include $(DEPS)
