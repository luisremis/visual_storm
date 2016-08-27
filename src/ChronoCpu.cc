#include "ChronoCpu.h"

#include <cstring>
#include <iostream>

#include <time.h>
#include <sys/time.h>

using namespace std;

// *****************************************************************************
// Public methods definitions
// *****************************************************************************
ChronoCpu::ChronoCpu(const string& name) :
		 Chrono     (name)
		,ticCounter (0)
{
	memset((void*)&lastTicTime, 0, sizeof(lastTicTime));
	memset((void*)&ticTime, 0, sizeof(ticTime));
	memset((void*)&tacTime, 0, sizeof(tacTime));

#ifdef __MACH__ // OS X does not have clock_gettime, use clock_get_time
	host_get_clock_service(mach_host_self(), CALENDAR_CLOCK, &cclock);
#endif
}

ChronoCpu::~ChronoCpu(void)
{
#ifdef __MACH__ // OS X does not have clock_gettime, use clock_get_time
	mach_port_deallocate(mach_task_self(), cclock);
#endif
}


// *****************************************************************************
// Private/Protected methods definitions
// *****************************************************************************
void ChronoCpu::doTic(void)
{
	lastTicTime = ticTime;

#ifdef __MACH__ // OS X does not have clock_gettime, use clock_get_time
	clock_get_time(cclock, &mts);
	ticTime.tv_sec = mts.tv_sec;
	ticTime.tv_nsec = mts.tv_nsec;
#else
	if (clock_gettime(CLOCK_REALTIME, &ticTime) != 0){
		++errors;
		cerr << "ChronoCpu::doTic - " << name << ": clock_gettime() failed!" << endl;
		return;
	}
#endif

	++ticCounter;

	if (ticCounter > 1){
		float period_s = (float)(ticTime.tv_sec - lastTicTime.tv_sec);
		float period_ns = (float)(ticTime.tv_nsec - lastTicTime.tv_nsec);
		periodStats.lastTime_ms = period_s * 1e3f + period_ns / 1e6f;
		updateStats(periodStats);
	}
}

void ChronoCpu::doTac(void)
{
#ifdef __MACH__ // OS X does not have clock_gettime, use clock_get_time
	clock_serv_t cclock;
	mach_timespec_t mts;
	host_get_clock_service(mach_host_self(), CALENDAR_CLOCK, &cclock);
	clock_get_time(cclock, &mts);
	mach_port_deallocate(mach_task_self(), cclock);
	tacTime.tv_sec = mts.tv_sec;
	tacTime.tv_nsec = mts.tv_nsec;

#else
	if (clock_gettime(CLOCK_REALTIME, &tacTime) != 0){
		++errors;
		cerr << "ChronoCpu::doTac - " << name << ": clock_gettime() failed!" << endl;
		return;
	}
#endif

	float elapsed_s = (float)(tacTime.tv_sec - ticTime.tv_sec);
	float elapsed_ns = (float)(tacTime.tv_nsec - ticTime.tv_nsec);
	elapsedStats.lastTime_ms = elapsed_s * 1e3f + elapsed_ns / 1e6f;
	updateStats(elapsedStats);
}

