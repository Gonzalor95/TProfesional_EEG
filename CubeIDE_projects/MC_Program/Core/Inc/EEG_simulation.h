/*
 * EEG_simulation.h
 *
 *  Created on: Jun 4, 2022
 *      Author: Gonzalo
 */

#ifndef INC_EEG_SIMULATION_H_
#define INC_EEG_SIMULATION_H_


#include "stm32f4xx_hal.h"

typedef u32int_t Channel_DataPackage;

typedef enum {
	CHANNEL_FP1,
	CHANNEL_FZ,
	CHANNEL_FP2,
	CHANNEL_F3,
	CHANNEL_F4,
	CHANNEL_C3,
	CHANNEL_C4,
	CHANNEL_P3
}CHANNEL_TAG;

typedef u32int_t DAC_Config;

void config_DACs();
void waiting_simulation_config();
void process_simulation();
void release_latch();
void feed_DAC();
void idle_mode();
void execute_config();


#endif /* INC_EEG_SIMULATION_H_ */
