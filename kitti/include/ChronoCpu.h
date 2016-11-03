#ifndef CHRONO_CPU_H_
#define CHRONO_CPU_H_

#include "Chrono.h"

#include <time.h>

#ifdef __MACH__
#include <mach/clock.h>
#include <mach/mach.h>
#endif

// *****************************************************************************
// Class definitions
// *****************************************************************************
class ChronoCpu : public Chrono {
public:
	ChronoCpu(const std::string& name);
	~ChronoCpu(void);

protected:
	timespec lastTicTime;
	timespec ticTime;
	timespec tacTime;

#ifdef __MACH__ 
	clock_serv_t cclock;
	mach_timespec_t mts;
#endif

	uint32_t ticCounter;

	virtual void doTic(void);
	virtual void doTac(void);
};


#endif /* CHRONO_CPU_H_ */
