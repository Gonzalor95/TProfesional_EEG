/*
 * EEG_simulation.c
 *
 *  Created on: Jun 4, 2022
 *      Author: Gonzalo
 */

#include <EEG_simulation.h>

void init_dac_handler(const DAC_Tag dac_tag, const SPI_HandleTypeDef *hspi, const GPIO_TypeDef *GPIOx, const uint16_t GPIO_Pin, DAC_Handler *dac_handler)
{
	dac_handler->dac_tag = dac_tag;
	dac_handler->dac_hspi = hspi;
	dac_handler->dac_SS_GPIO_port = GPIOx;
	dac_handler->dac_ss_GPIO_pin = GPIO_Pin;
}

void reset_dacs_config(const DAC_Handler list_of_dacs[], const uint8_t *dacs_count)
{
	for (int i = 0; i < (*dacs_count); i++)
	{
		uint16_t word = DAC_CONFIG_RESET_DATA_AND_CONTROL;

		if (_send_word_to_dac(word, &(list_of_dacs[i])) != HAL_OK)
		{
			break;
		}
	}
}

void init_LDAC_in_dacs(const DAC_Handler list_of_dacs[], const uint8_t *dacs_count)
{
	for (int i = 0; i < (*dacs_count); i++)
	{
		uint16_t word = DAC_CONFIG_LDAC_HIGH;
		if (_send_word_to_dac(word, &(list_of_dacs[i])) != HAL_OK)
		{
			break;
		}
	}
}

void init_LDAC(const GPIO_TypeDef *GPIOx, const uint16_t GPIO_Pin, LDAC_Handler *LDAC)
{
	LDAC->GPIO_LDAC_control_port = GPIOx;
	LDAC->GPIO_LDAC_control_pin = GPIO_Pin;

	// Initialize LDAC with fixed state
	HAL_GPIO_WritePin(LDAC->GPIO_LDAC_control_port, LDAC->GPIO_LDAC_control_pin, GPIO_PIN_SET);
}

uint16_t parse_config(const uint8_t *bufferUSB)
{
	return ((uint16_t)bufferUSB[0] << 8) | ((uint16_t)bufferUSB[1]);
}

void parse_tag_and_channel_from_config(const uint16_t *config, DAC_Tag *DAC_tag, DAC_Channel *DAC_channel)
{
	// config / 8 = {0,1,2,3} -> which corresponds to one DAC, so we use the enum defined in DAC_Tag for correlation
	*DAC_tag = (*config) / 8;
	// config % 8 = {0,1,2,3,4,5,6,7} -> which corresponds to a DAC channel, so we use the enum defined in DAC_Channel for correlation.
	*DAC_channel = (*config) % 8;
}

HAL_StatusTypeDef send_data_to_dac_channel(const DAC_Handler *dac_handler, const DAC_Channel *dac_channel, const uint8_t *bufferUSB)
{
	// dataToDAC = 0b 0AAA-DDDD-DDDD-DDDD
	/* Where:
	 * 0 = MSB (izquierda de todo) en cero para tener el "modo escritura"
	 * AAA = Address (de 0 a 8)
	 * D...D = datos
	 * dataToDAC[0] =
	 * dataToDAC[1] =
	 */
	HAL_StatusTypeDef status = HAL_OK;
	uint8_t dataToDAC[2];
	uint8_t channel_addr_mask = get_dac_channel_addr_mask(dac_channel);

	// Copy data
	dataToDAC[0] = bufferUSB[2];
	dataToDAC[1] = bufferUSB[3] >> 4;

	// Apply channel_addr_mask: 0b 0AAA-0000
	dataToDAC[1] = dataToDAC[1] | channel_addr_mask;

	// GPIO_Write sirve para avisar al DAC que le estamos escribiendo
	HAL_GPIO_WritePin(dac_handler->dac_SS_GPIO_port, dac_handler->dac_ss_GPIO_pin, GPIO_PIN_RESET);
	status = HAL_SPI_Transmit(dac_handler->dac_hspi, dataToDAC, sizeof(dataToDAC), HAL_MAX_DELAY);
	HAL_GPIO_WritePin(dac_handler->dac_SS_GPIO_port, dac_handler->dac_ss_GPIO_pin, GPIO_PIN_SET);

	return status;
}

/**
 * @brief Array containing the masks for the DAC channels
 */
uint8_t DAC_Channel_Masks[] = {
	0x00,
	0x10,
	0x20,
	0x30,
	0x40,
	0x50,
	0x60,
	0x70};
uint8_t get_dac_channel_addr_mask(const DAC_Channel *dac_channel)
{
	return DAC_Channel_Masks[*dac_channel];
}

HAL_StatusTypeDef send_configuration_to_dacs(const uint16_t *config, const DAC_Handler *list_of_dacs[], const uint8_t *dacs_count)
{
	HAL_StatusTypeDef status = HAL_OK;
	if (*config == CONF_LDAC_TRIGGER)
	{
		trigger_LDAC();
		return status;
	}
	else if (*config == CONF_LDAC_LOW)
	{
		// TODO: Complete with other configs
	}
	return status;
}

void trigger_LDAC()
{
	// To trigger LDAC. Every pin 1 (LDAC) of the DACs must be set to low to update all channels at once
	// LDAC_settings variable is declared as extern outside
	// Setting LDAC Pin to 0 (zero/low)
	//  TODO: hardcode until figure extern problem HAL_GPIO_WritePin(LDAC_settings.GPIO_LDAC_control_port, LDAC_settings.GPIO_LDAC_control_pin, GPIO_PIN_RESET);
	HAL_GPIO_WritePin(GPIOB, GPIO_PIN_2, GPIO_PIN_RESET);
	// Setting LDAC Pin to 1 (one/high)
	HAL_GPIO_WritePin(GPIOB, GPIO_PIN_2, GPIO_PIN_SET);
}

HAL_StatusTypeDef _send_word_to_dac(uint16_t word, DAC_Handler *dac_handler)
{
	HAL_StatusTypeDef status;
	uint8_t dataToDAC[2];

	dataToDAC[0] = (uint8_t)word;
	dataToDAC[1] = (uint8_t)(word >> 8);

	HAL_GPIO_WritePin(dac_handler->dac_SS_GPIO_port, dac_handler->dac_ss_GPIO_pin, GPIO_PIN_RESET);
	status = HAL_SPI_Transmit(dac_handler->dac_hspi, dataToDAC, (uint16_t)sizeof(dataToDAC), HAL_MAX_DELAY);
	HAL_GPIO_WritePin(dac_handler->dac_SS_GPIO_port, dac_handler->dac_ss_GPIO_pin, GPIO_PIN_SET);
	return status;
}

// Errors:
void EEG_simulation_error_Handler(void)
{
	__disable_irq();
	while (1)
	{
	}
}
