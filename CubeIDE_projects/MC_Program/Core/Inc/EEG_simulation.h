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
#include <stdbool.h>



/*
Verde = DAC 16 = SCLK = PA5
Naranja  = DAC 15 = DIN = PA7
Pata = DAC 1 = LDAC
Azul = DAC 2 =SYNC = PA4
 *
 * */

/* BEGIN: Control/Config Words  */
// Defined according https: www.analog.com/media/en/technical-documentation/data-sheets/ad5308_5318_5328.pdf

//LDAC: 0b 101x-xxxx-xxxx-xx??
#define DAC_CONFIG_LDAC_LOW 			0xA000	// DAC registers updated continuously
#define DAC_CONFIG_LDAC_HIGH 			0xA001	// (DEFAULT) DAR reg. are latched and the input registers can change without affecting the contents of the DAC reg
#define DAC_CONFIG_LDAC_SINGLE_UPDATE 	0xA003	// Causes a single pulse on LDAC, updating the DAC registers once.
//Reset:0b 111?-xxxx-xxxx-xxxx
#define DAC_CONFIG_RESET_DATA  				0xE	// All outputs to zero
#define DAC_CONFIG_RESET_DATA_AND_CONTROL 	0xF	// reset all DAC

//Gain of output and reference selection

//Power-down:


/* END: Control Words  */

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

#define DAC_CHANNEL_MAX_DATA  0XFFF0 // 0b 1111-1111-1111-xxxx. x = ignored
#define DAC_CHANNEL_MIN_DATA  0X000F // 0b 0000-0000-0000-xxxx. x = ignored

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

/* Struct DAC:
 * dac_tag = numero identificador del DAC, relacionado con el hspi
 * *pdac_hspi = puntero al handler SPI del DAC
 * GPIO = maneja el SS (slave select)
 	 * pGPIOx = GPIOx where x can be (A..K) to select the GPIO peripheral
 	 * GPIO_Pin = GPIO_Pin specifies the port bit to be written. This parameter can be one of GPIO_PIN_x where x can be (0..15).
 */
// TODO: Change GPIO name and explain further
typedef struct DAC_Handler{
	DAC_Tag dac_tag;
	SPI_HandleTypeDef *dac_hspi;
	GPIO_TypeDef * dac_GPIO_peripheral;
	uint16_t dac_GPIO_Pin;

} DAC_Handler;

typedef enum{
	// DAC 0
	CH_Fp1 = 0,
	CH_Fz  = 1,
	CH_Fp2 = 2,
	CH_F3  = 3,
	CH_F4  = 4,
	CH_C3  = 5,
	CH_C4  = 6,
	CH_P3  = 7,
	// DAC 1
	CH_P4  = 8,
	CH_O1  = 9,
	CH_O2  = 10,
	CH_F7  = 11,
	CH_F8  = 12,
	CH_T7  = 13,
	CH_T8  = 14,
	CH_P7  = 15,
	// DAC 2
	CH_P8  = 16,
	CH_Pz  = 17,
	CH_Cz  = 18,
	CH_PG1 = 19,
	CH_PG2 = 20,
	CH_AFz = 21,
	CH_FCz = 22,
	CH_CPz = 23,
	// DAC 3
	CH_CP3 = 24,
	CH_CP4 = 25,
	CH_FC3 = 26,
	CH_FC4 = 27,
	CH_TP7 = 28,
	CH_TP8 = 29,
	CH_FT7 = 30,
	CH_FT8 = 31
}protocol_word;



// Prototipos
HAL_StatusTypeDef send_data_to_dac_channel(const DAC_Handler *dac_handler, const DAC_Channel *dac_channel, const uint16_t *data);
HAL_StatusTypeDef send_data_to_multiple_dac_channels(uint16_t data, DAC_Handler *dac_handler, DAC_Channel arr_dac_channels[], size_t channel_count); // TODO: verificar qe no se pase de 8 canales

void send_pulse_to_dac_channels(DAC_Handler *dac_handler, DAC_Channel arr_dac_channels[], size_t channel_count, uint32_t delay_in_ms);
void send_triangular_wave_to_dac_channels(DAC_Handler *dac_handler, DAC_Channel arr_dac_channels[], size_t channel_count, uint32_t delay_in_ms);


/* initializer, gets and setters */

void init_dac_handler(DAC_Handler *dac_handler, DAC_Tag dac_tag, SPI_HandleTypeDef *hspi, GPIO_TypeDef * GPIOx, uint16_t GPIO_Pin);


uint8_t get_dac_channel_addr_mask(DAC_Channel dac_channel);

void parse_recieving_buffer(uint8_t **bufferUSB, uint16_t *config, uint16_t *data);
void process_tag_and_channel_from_config(const uint16_t *config, DAC_Tag *DAC_tag, DAC_Channel *DAC_channel);

// Error functions

void EEG_simulation_error_Handler(void);


#endif /* INC_EEG_SIMULATION_H_ */
