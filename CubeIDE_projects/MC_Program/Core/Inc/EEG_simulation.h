/*
 * EEG_simulation.h
 *
 *  Created on: Jun 4, 2022
 *      Author: Gonzalo
 */

#ifndef INC_EEG_SIMULATION_H_
#define INC_EEG_SIMULATION_H_


#include "stm32f4xx_hal.h"
#include "stdint.h"

#define DAC_CHANNEL_A_ADDR_8Bit_MASK 0x00 // 0b00000000
#define DAC_CHANNEL_B_ADDR_8Bit_MASK 0x10 // 0b00010000
#define DAC_CHANNEL_C_ADDR_8Bit_MASK 0x20 // 0b00100000
#define DAC_CHANNEL_D_ADDR_8Bit_MASK 0x30 // 0b00110000
#define DAC_CHANNEL_E_ADDR_8Bit_MASK 0x40 // 0b01000000
#define DAC_CHANNEL_F_ADDR_8Bit_MASK 0x50 // 0b01010000
#define DAC_CHANNEL_G_ADDR_8Bit_MASK 0x60 // 0b01100000
#define DAC_CHANNEL_H_ADDR_8Bit_MASK 0x70 // 0b01110000



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

void test_sine_wave_1DAC_1Channel(uint8_t dac_channel_addr_8bMask,SPI_HandleTypeDef *hspi);
void test_sine_wave_1DAC_all_channels(SPI_HandleTypeDef **hspi);




#endif /* INC_EEG_SIMULATION_H_ */
