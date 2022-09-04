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


HAL_StatusTypeDef send_data_to_dac_channel(uint16_t data, DAC_Handler *dac_handler, DAC_Channel dac_channel){

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



	HAL_GPIO_WritePin(dac_handler->dac_GPIO_peripheral, dac_handler->dac_GPIO_Pin, GPIO_PIN_RESET); // TODO:Los puertos tienen que quedar en una variable. Hacer un struct/objeto DAC
	status = HAL_SPI_Transmit(dac_handler->dac_hspi, dataToDAC, (uint16_t) sizeof(dataToDAC), HAL_MAX_DELAY);
	HAL_GPIO_WritePin(dac_handler->dac_GPIO_peripheral, dac_handler->dac_GPIO_Pin, GPIO_PIN_SET);

	return status;

}

HAL_StatusTypeDef send_data_to_multiple_dac_channels(uint16_t data, DAC_Handler *dac_handler, DAC_Channel arr_dac_channels[], size_t channel_count){

	HAL_StatusTypeDef status = HAL_OK;

	for(size_t i = 0; i < channel_count; i++ ){

		DAC_Channel dac_channel = arr_dac_channels[i];

		if( HAL_OK != (status = send_data_to_dac_channel(data,dac_handler,dac_channel)) ){
			break;
		}
	}
	return status;
}

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

void send_triangular_wave_to_dac_channels(DAC_Handler *dac_handler, DAC_Channel arr_dac_channels[], size_t channel_count, uint32_t delay_in_ms){

	uint16_t data = DAC_CHANNEL_MIN_DATA+1;
	bool ascending = true;
	int min_step = 15;
	int multiplier = 8;
	int freq_step = multiplier*min_step;
	while(1){

		if(data >= DAC_CHANNEL_MAX_DATA) ascending = false;
		else if (data <= DAC_CHANNEL_MIN_DATA) ascending = true;
		//if(data > DAC_CHANNEL_MAX_DATA) data = DAC_CHANNEL_MIN_DATA;

		if(HAL_OK != send_data_to_multiple_dac_channels(data, dac_handler, arr_dac_channels, channel_count)){
			EEG_simulation_error_Handler();
		}
	//	HAL_Delay(delay_in_ms);

		if(ascending) data += freq_step;
		else data -= freq_step;
	}

}

/* initializer, gets and setters */

void init_dac_handler(DAC_Handler *dac_handler, DAC_Tag dac_tag, SPI_HandleTypeDef *hspi, GPIO_TypeDef * GPIOx, uint16_t GPIO_Pin){
	dac_handler->dac_tag = dac_tag;
	dac_handler->dac_hspi = hspi;
	dac_handler->dac_GPIO_peripheral = GPIOx;
	dac_handler->dac_GPIO_Pin = GPIO_Pin;
}


uint8_t get_dac_channel_addr_mask(DAC_Channel dac_channel){
	return DAC_Channel_Addr8bit_mask_Dictionary[dac_channel];
}

// Errors:
void EEG_simulation_error_Handler(void){
  __disable_irq();
  while (1)
  {
  }
}

