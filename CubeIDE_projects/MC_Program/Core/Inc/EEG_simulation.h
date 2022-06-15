/*
 * EEG_simulation.h
 *
 *  Created on: Jun 4, 2022
 *      Author: Gonzalo
 */

#ifndef INC_EEG_SIMULATION_H_
#define INC_EEG_SIMULATION_H_


#include "stm32f4xx_hal.h"

#define DAC_CHANNEL_A_ADDR_16Bit_MASK 0x0000 // 0b0000000000000000
#define DAC_CHANNEL_B_ADDR_16Bit_MASK 0x1000 // 0b0001000000000000
#define DAC_CHANNEL_C_ADDR_16Bit_MASK 0x2000 // 0b0010000000000000
#define DAC_CHANNEL_D_ADDR_16Bit_MASK 0x3000 // 0b0011000000000000
#define DAC_CHANNEL_E_ADDR_16Bit_MASK 0x4000 // 0b0100000000000000
#define DAC_CHANNEL_F_ADDR_16Bit_MASK 0x5000 // 0b0101000000000000
#define DAC_CHANNEL_G_ADDR_16Bit_MASK 0x6000 // 0b0110000000000000
#define DAC_CHANNEL_H_ADDR_16Bit_MASK 0x7000 // 0b0111000000000000

typedef uint16_t dac_channel_addr_16bit_mask;

typedef uint8_t Channel_DataPackage;

typedef enum {
	CHANNEL_A = 0, //0b000
	CHANNEL_B = 1, //0b001
	CHANNEL_C = 2, //0b010
	CHANNEL_D = 3, //0b011
	CHANNEL_E = 4, //0b100
	CHANNEL_F = 5, //0b101
	CHANNEL_G = 6, //0b110
	CHANNEL_H = 7 //0b111
}DAC_CHANNEL_ADDR;

typedef enum {
	DAC_A,
	DAC_B,
	DAC_C,
	DAC_D
}DAC_TAG;

typedef uint16_t DAC_Config;

void config_DACs();
void waiting_simulation_config();
void process_simulation();
void release_latch();
void feed_DAC();
void idle_mode();
void execute_config();

void test_sine_wave_1DAC_1Channel(DAC_CHANNEL_ADDR DAC_channel_tag,SPI_HandleTypeDef *hspi);


#endif /* INC_EEG_SIMULATION_H_ */
