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


/*BEGIN: DAC Channels mask definitions */

// Mask servers to write required address in the 16bit word to write to DACs
#define DAC_CHANNEL_A_ADDR_8Bit_MASK 0x00 // 0b00000000
#define DAC_CHANNEL_B_ADDR_8Bit_MASK 0x10 // 0b00010000
#define DAC_CHANNEL_C_ADDR_8Bit_MASK 0x20 // 0b00100000
#define DAC_CHANNEL_D_ADDR_8Bit_MASK 0x30 // 0b00110000
#define DAC_CHANNEL_E_ADDR_8Bit_MASK 0x40 // 0b01000000
#define DAC_CHANNEL_F_ADDR_8Bit_MASK 0x50 // 0b01010000
#define DAC_CHANNEL_G_ADDR_8Bit_MASK 0x60 // 0b01100000
#define DAC_CHANNEL_H_ADDR_8Bit_MASK 0x70 // 0b01110000



typedef enum {
	CHANNEL_A = 0, //0b000
	CHANNEL_B = 1, //0b001
	CHANNEL_C = 2, //0b010
	CHANNEL_D = 3, //0b011
	CHANNEL_E = 4, //0b100
	CHANNEL_F = 5, //0b101
	CHANNEL_G = 6, //0b110
	CHANNEL_H = 7  //0b111
}DAC_Channel;

/*END: DAC Channels mask definitions */


/*BEGIN: DACs identification */

typedef enum {
	DAC_A = 0,
	DAC_B = 1,
	DAC_C = 2,
	DAC_D = 3
}DAC_Tag;

/*END: DACs identification */

typedef uint16_t DAC_Config;

void config_DACs();
void waiting_simulation_config();
void process_simulation();
void release_latch();
void feed_DAC();
void idle_mode();
void execute_config();

void all_DACs_array_init(SPI_HandleTypeDef *hspi1, SPI_HandleTypeDef *hspi2, SPI_HandleTypeDef *hspi3, SPI_HandleTypeDef *hspi4);

void test_sine_wave_1DAC_1Channel(DAC_Tag dac_tag, DAC_Channel dac_channel);
void test_sine_wave_1DAC_all_channels(SPI_HandleTypeDef **hspi);

uint8_t get_DAC_Channel_Addr_mask(DAC_Channel dac_channel);
SPI_HandleTypeDef * get_DAC_SPI_handler(DAC_Tag dac_tag);






#endif /* INC_EEG_SIMULATION_H_ */
