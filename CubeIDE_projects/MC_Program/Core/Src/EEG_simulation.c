/*
 * EEG_simulation.c
 *
 *  Created on: Jun 4, 2022
 *      Author: Gonzalo
 */

#include <EEG_simulation.h>


// The order of the next array must be consistent with the "enum{} DAC_Channel_Addr" position
uint8_t DAC_Channel_Addr8bit_mask_Dictionary[] = {
		DAC_CHANNEL_A_ADDR_8Bit_MASK,
		DAC_CHANNEL_B_ADDR_8Bit_MASK,
		DAC_CHANNEL_C_ADDR_8Bit_MASK,
		DAC_CHANNEL_D_ADDR_8Bit_MASK,
		DAC_CHANNEL_E_ADDR_8Bit_MASK,
		DAC_CHANNEL_F_ADDR_8Bit_MASK,
		DAC_CHANNEL_G_ADDR_8Bit_MASK,
		DAC_CHANNEL_H_ADDR_8Bit_MASK
};


// Receives the USB buffer and parse it to config and data variables
void parse_receiving_buffer(uint8_t bufferUSB[], uint16_t *config, uint16_t *data){
	// config = {1,0}
	*config = ((uint16_t)bufferUSB[0] << 8) | ((uint16_t)bufferUSB[1]);
	// data = {3,2}
	*data = ((uint16_t)bufferUSB[2] << 8) | ((uint16_t)bufferUSB[3]);
}


// Recovers the values for DAC_Tag and DAC_Channel
/* We expect 0=< config <= 31. So:
 * config / 8 = {0,1,2,3} -> which corresponds to one DAC, so we use the enum defined in DAC_Tag for correlation.
 * config % 8 = {0,1,2,3,4,5,6,7} -> which corresponds to a DAC channel, so we use the enum defined in DAC_Channel for correlation.
 * */
void process_tag_and_channel_from_config(const uint16_t *config, DAC_Tag *DAC_tag, DAC_Channel *DAC_channel){
	*DAC_tag = (*config) / 8;
	*DAC_channel = (*config) % 8;
}


HAL_StatusTypeDef send_data_to_dac_channel(const DAC_Handler *dac_handler, const DAC_Channel *dac_channel, uint16_t data){

	// dataToDAC = 0b 0AAA - DDDD - DDDD - DDDD
    /* Donde:
     * 0 = MSB (izquierda de todo) en cero para tener el "modo escritura"
     * AAA = Address (de 0 a 8)
     * D...D = datos
    */
    uint8_t dataToDAC[2];
    HAL_StatusTypeDef status = HAL_OK;

    uint8_t channel_addr_mask = get_dac_channel_addr_mask(dac_channel);

    // 1) Inicializar dataToDAC a 0:
    dataToDAC[0] = 0;
    dataToDAC[1] = 0;

    // 2) Recibo data:
    // uint16_t data = 0x8A5F; // 0b 1000-1010-0101-1111

    // 3) Desestimo (shifteando) los ultimos 4 LSB (derecha de todo)
    data = data >> 4; // 0b 0000-1000-1010-0101

    // 4) Paste data
	dataToDAC[0] = (uint8_t) data;
	dataToDAC[1] = (uint8_t) (data >> 8);

    // 5) aplico mascara
    // uint8_t channel_addr_mask = 0x70; // 0b 0111-0000
    dataToDAC[1] = dataToDAC[1] | channel_addr_mask;

    // GPIO_Write sirve para avisar al DAC que le estamos escribiendo
	HAL_GPIO_WritePin(dac_handler->dac_SS_GPIO_port, dac_handler->dac_ss_GPIO_pin, GPIO_PIN_RESET);
	status = HAL_SPI_Transmit(dac_handler->dac_hspi, dataToDAC, (uint16_t) sizeof(dataToDAC), HAL_MAX_DELAY);
	HAL_GPIO_WritePin(dac_handler->dac_SS_GPIO_port, dac_handler->dac_ss_GPIO_pin, GPIO_PIN_SET);

	return status;
}


/* Sends any word of 16 bits to the DAC. Used for configs*/
HAL_StatusTypeDef _send_word_to_dac(uint16_t word, DAC_Handler * dac_handler){

	HAL_StatusTypeDef status;
	uint8_t dataToDAC[2];

	dataToDAC[0] = (uint8_t) word;
	dataToDAC[1] = (uint8_t) (word >> 8);

	HAL_GPIO_WritePin(dac_handler->dac_SS_GPIO_port, dac_handler->dac_ss_GPIO_pin, GPIO_PIN_RESET);
	status = HAL_SPI_Transmit(dac_handler->dac_hspi, dataToDAC, (uint16_t) sizeof(dataToDAC), HAL_MAX_DELAY);
	HAL_GPIO_WritePin(dac_handler->dac_SS_GPIO_port, dac_handler->dac_ss_GPIO_pin, GPIO_PIN_SET);
	return status;
}

void trigger_LDAC(){
	// To trigger LDAC. Every pin 1 (LDAC) of the DACs must be set to low to update all channels at once

	// LDAC_settings variable is declared as extern outside

	//Setting LDAC Pin to 0 (zero/low)
	// TODO: hardcode until figure extern problem HAL_GPIO_WritePin(LDAC_settings.GPIO_LDAC_control_port, LDAC_settings.GPIO_LDAC_control_pin, GPIO_PIN_RESET);
	HAL_GPIO_WritePin(GPIOB, GPIO_PIN_2, GPIO_PIN_RESET);


	//Setting LDAC Pin to 1 (one/high)
	HAL_GPIO_WritePin(GPIOB, GPIO_PIN_2, GPIO_PIN_SET);
}

HAL_StatusTypeDef send_configuration_to_dacs(uint16_t config, DAC_Handler * list_of_dacs[], uint8_t dacs_count){

	HAL_StatusTypeDef status = HAL_OK;
	if(config == CONF_LDAC_TRIGGER){

		trigger_LDAC();

		return status;

	}else if(config == CONF_LDAC_LOW){
		// TODO: Complete with other configs
	}

	return status;
}

HAL_StatusTypeDef send_data_to_multiple_dac_channels(uint16_t data, DAC_Handler *dac_handler, DAC_Channel arr_dac_channels[], size_t channel_count){

	HAL_StatusTypeDef status = HAL_OK;

	for(size_t i = 0; i < channel_count; i++ ){

		DAC_Channel dac_channel = arr_dac_channels[i];

		if( HAL_OK != (status = send_data_to_dac_channel(dac_handler,&dac_channel, data)) ){
			break;
		}
	}
	return status;
}

// WARNING: TEST FUNCTION! Blocks functioning on infinite loop
void send_pulse_to_dac_channels(DAC_Handler *dac_handler, DAC_Channel arr_dac_channels[], size_t channel_count, uint32_t delay_in_ms){

	uint16_t data = 0;
	size_t i = 0;

	while(1){
		if(i%2) data = 0xFFFF;
		else data = 0;

		if(HAL_OK != send_data_to_multiple_dac_channels(data, dac_handler, arr_dac_channels, channel_count)){
			EEG_simulation_error_Handler();
		}
		HAL_Delay(delay_in_ms);
		i++;
	}

}

// WARNING: TEST FUNCTION! Blocks functioning on infinite loop
void send_triangular_wave_to_dac_channels(DAC_Handler *dac_handler, DAC_Channel arr_dac_channels[], size_t channel_count, uint32_t delay_in_ms){

	uint16_t data = DAC_CHANNEL_MIN_DATA+1;
	bool ascending = true;
	int min_step = 15;
	int multiplier = 8*16;
	int freq_step = multiplier*min_step;
	while(1){

		if(data >= DAC_CHANNEL_MAX_DATA) ascending = false;
		else if (data <= DAC_CHANNEL_MIN_DATA) ascending = true;
		//if(data > DAC_CHANNEL_MAX_DATA) data = DAC_CHANNEL_MIN_DATA;

		if(HAL_OK != send_data_to_multiple_dac_channels(data, dac_handler, arr_dac_channels, channel_count)){
			EEG_simulation_error_Handler();
		}
		HAL_Delay(delay_in_ms);

		if(ascending) data += freq_step;
		else data -= freq_step;
	}

}

/* initializer, gets and setters */

// Init variables for dac_handler variable
void init_dac_handler(DAC_Handler *dac_handler, DAC_Tag dac_tag, SPI_HandleTypeDef *hspi, GPIO_TypeDef * GPIOx, uint16_t GPIO_Pin){
	dac_handler->dac_tag = dac_tag;
	dac_handler->dac_hspi = hspi;
	dac_handler->dac_SS_GPIO_port = GPIOx;
	dac_handler->dac_ss_GPIO_pin = GPIO_Pin;
}

// Init the ports that control LDAC in the LDAC_settings variable.
// LDAC_settings must be an "extern" variable to be accessible on trigger_LDAC()

void init_LDAC_settings(LDAC_Settings * LDAC_settings, GPIO_TypeDef * GPIOx, uint16_t GPIO_Pin){
	LDAC_settings->GPIO_LDAC_control_port = GPIOx;
	LDAC_settings->GPIO_LDAC_control_pin = GPIO_Pin;

	// Initialize LDAC with fixed state
	HAL_GPIO_WritePin(LDAC_settings->GPIO_LDAC_control_port, LDAC_settings->GPIO_LDAC_control_pin, GPIO_PIN_SET);
}

void init_LDAC_in_dacs(DAC_Handler  list_of_dacs[], uint8_t dacs_count){

	for(int i = 0 ; i < dacs_count; i++){
		uint16_t word = DAC_CONFIG_LDAC_HIGH;

		if( _send_word_to_dac(word, &(list_of_dacs[i])) != HAL_OK){
			break;
		}

	}
}

// Resets DACs.
// Data in all channels  = 0
// Config in all DACs = DEFAULT
void reset_dacs_config(DAC_Handler list_of_dacs[], uint8_t dacs_count){

	for(int i = 0 ; i < dacs_count; i++){
		uint16_t word = DAC_CONFIG_RESET_DATA_AND_CONTROL;

		if( _send_word_to_dac(word, &(list_of_dacs[i])) != HAL_OK){
			break;
		}

	}
}


uint8_t get_dac_channel_addr_mask(const DAC_Channel *dac_channel){
	return DAC_Channel_Addr8bit_mask_Dictionary[*dac_channel];
}

// Errors:
void EEG_simulation_error_Handler(void){
  __disable_irq();
  while (1)
  {
  }
}
