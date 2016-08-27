#ifndef CHRONO_H_
#define CHRONO_H_

#include <ostream>
#include <stdint.h>
#include <string.h>
#include <string>

#include <time.h>

#ifdef __MACH__
#include <mach/clock.h>
#include <mach/mach.h>
#endif

// *****************************************************************************
// Chrono Base clase
// *****************************************************************************
class Chrono {
public:
	Chrono(const std::string& name, const bool asyncEnabled=false);
	virtual ~Chrono(void);

	void tic(void);
	void tac(void);
	void reset(void);
	void setEnabled(const bool val);

	struct ChronoStats{
		std::string name;
		uint32_t counter;
		float totalTime_ms;
		float totalSquaredTime_ms2;
		float averageTime_ms;
		float stdDevTime_ms;
		float lastTime_ms;
		float minTime_ms;
		float maxTime_ms;
	};

	const Chrono::ChronoStats& getElapsedStats(void) const;
	const Chrono::ChronoStats& getPeriodStats(void) const;

	std::ostream& printStats(const Chrono::ChronoStats& stats, std::ostream& os) const;
	std::ostream& printAvgTime(const Chrono::ChronoStats& stats, std::ostream& os) const;
	std::ostream& printAvgTime(const Chrono::ChronoStats& stats, std::ostream& os, const float ref) const;

protected:
	std::string name;

	// Estado y estadisticas del timer
	bool enabled;
	bool ticIdle;
	uint32_t errors;

	ChronoStats elapsedStats;
	ChronoStats periodStats;

	void resetStats(ChronoStats& stats);
	void updateStats(ChronoStats& stats);

	// Metodos que deben ser implementados en la clase derivada
	virtual void doTic(void) = 0;
	virtual void doTac(void) = 0;
};


// *****************************************************************************
// Chrono Cpu Implementation
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



#endif	// CHRONO_H_
