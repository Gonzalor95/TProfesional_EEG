/*
 * EEG_simulation.c
 *
 *  Created on: Jun 4, 2022
 *      Author: Gonzalo
 */

#include <EEG_simulation.h>

uint32_t sample_rate = SAMPLE_RATE;
uint32_t simulation_channel_count = SIMULATION_CHANNEL_COUNT;
uint8_t delay_flag = 0;

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
			continue;
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
			continue;
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

void parse_receiving_buffer(const uint8_t *bufferUSB, uint16_t *config, uint16_t *data)
{
	*config = ((uint16_t)bufferUSB[0] << 8) | ((uint16_t)bufferUSB[1]);
	*data = ((uint16_t)bufferUSB[2] << 8) | ((uint16_t)bufferUSB[3]);
}

void parse_tag_and_channel_from_config(const uint16_t *config, DAC_Tag *DAC_tag, DAC_Channel *DAC_channel)
{
	// config / 8 = {0,1,2,3} -> which corresponds to one DAC, so we use the enum defined in DAC_Tag for correlation
	*DAC_tag = (*config) / 8;
	// config % 8 = {0,1,2,3,4,5,6,7} -> which corresponds to a DAC channel, so we use the enum defined in DAC_Channel for correlation.
	*DAC_channel = (*config) % 8;
}

HAL_StatusTypeDef send_data_to_dac_channel(const DAC_Handler *dac_handler, const DAC_Channel *dac_channel, uint16_t data)
{
	// dataToDAC = 0b 0AAA-DDDD-DDDD-DDDD
	/* Where:
	 * 0 = MSB (izquierda de todo) en cero para tener el "modo escritura"
	 * AAA = Address (de 0 a 8)
	 * D...D = datos
	 * dataToDAC[0] = DDDD-DDDD (LSB)
	 * dataToDAC[1] = 0AAA-DDDD (MSB)
	 */
	HAL_StatusTypeDef status = HAL_OK;
	uint8_t dataToDAC[2];
	uint8_t channel_addr_mask = get_dac_channel_addr_mask(dac_channel);

	data = data >> 4;
	// Copy data
	dataToDAC[0] = (uint8_t) data;
	dataToDAC[1] = ((uint8_t)(data >> 8)) | channel_addr_mask; // Apply channel_addr_mask: 0b 0AAA-0000

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

HAL_StatusTypeDef send_configuration_to_dacs(const uint16_t *config, const uint16_t *data, const DAC_Handler *list_of_dacs[], const uint8_t *dacs_count)
{
	HAL_StatusTypeDef status = HAL_OK;

	switch (*config) {
	case CONF_LDAC_TRIGGER:
		trigger_LDAC();
		break;
	case CONF_LDAC_LOW:
		//TODO: Complete with other configs
	case CONF_SAMPLE_RATE:
		config_sample_rate_delay(*data);
		break;
	case CONF_SIMULATION_CHANNEL_COUNT:
		config_simulation_channel_count(*data);

	default:
		status = HAL_ERROR;
		break;
	}

	return status;
}

void trigger_LDAC()
{
	// To trigger LDAC. Every pin 1 (LDAC) of the DACs must be set to low to update all channels at once
	// LDAC_settings variable is declared as extern outside
	// Setting LDAC Pin to 0 (zero/low)
	// TODO: hardcode until figure extern problem HAL_GPIO_WritePin(LDAC_settings.GPIO_LDAC_control_port, LDAC_settings.GPIO_LDAC_control_pin, GPIO_PIN_RESET);
	HAL_GPIO_WritePin(GPIOB, GPIO_PIN_2, GPIO_PIN_RESET);
	// Setting LDAC Pin to 1 (one/high)
	HAL_GPIO_WritePin(GPIOB, GPIO_PIN_2, GPIO_PIN_SET);
}


/*
 * Since sample_rate = sample per second.
 * TIM3 = LDAC trigger has a clock that triggers every 100useg
 * trigger_LDAC() cout = 10.000 / sample rate
 */
void config_sample_rate_delay(const uint16_t data){
	sample_rate = data;
	sample_rate = 10000/sample_rate;
}

void config_simulation_channel_count(const uint16_t data){
	simulation_channel_count = data;
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

// Test signals (do not delete):

void test_send_data_value_to_all_dacs(const DAC_Handler  list_of_dacs[], uint16_t data){
	DAC_Channel dac_channel[DACS_CHANNEL_COUNT] = {CHANNEL_A, CHANNEL_B, CHANNEL_C, CHANNEL_D, CHANNEL_E, CHANNEL_F, CHANNEL_G, CHANNEL_H};

	for(int j = 0 ; j < DACS_COUNT; j++){
		for(int k = 0; k < DACS_CHANNEL_COUNT; k++){
			send_data_to_dac_channel(&(list_of_dacs[j]), &(dac_channel[k]), data);
		}
	}
	trigger_LDAC();
}

/**
 * @brief BLOCKING FUNCTION, will enter a infinite loop
 */
void test_send_pulse(const DAC_Handler  list_of_dacs[]){

	uint16_t data = 0;
	DAC_Channel dac_channel[] = {CHANNEL_A, CHANNEL_B, CHANNEL_C, CHANNEL_D, CHANNEL_E, CHANNEL_F, CHANNEL_G, CHANNEL_H};

	int channel_count = 8;
	int dac_count = 4;
	int i = 0;

	while(1){
		if(i % 2)
			data = 0x00;
		else
			data = 0xFFFF;

		for(int j = 0 ; j < dac_count; j++){
			for(int k = 0; k < channel_count; k++){
				send_data_to_dac_channel(&(list_of_dacs[j]), &(dac_channel[k]), data);
			}
		}
		trigger_LDAC();
		HAL_Delay(10);
		i++;
	}


}

/**
 * @brief BLOCKING FUNCTION, will enter a infinite loop
 */
void test_send_saw(const DAC_Handler list_of_dacs[]){

	DAC_Channel dac_channel[] = {CHANNEL_A, CHANNEL_B, CHANNEL_C, CHANNEL_D, CHANNEL_E, CHANNEL_F, CHANNEL_G, CHANNEL_H};

	int channel_count = 8;
	int dac_count = 4;
	uint16_t i = 0;

	while(1){

		for(int j = 0 ; j < dac_count; j++){
			for(int k = 0; k < channel_count; k++){
				send_data_to_dac_channel(&(list_of_dacs[j]), &(dac_channel[k]), i);
			}
		}
		trigger_LDAC();
		i += 1000 ;
	}


}


// Errors:
void EEG_simulation_error_Handler(void)
{
	__disable_irq();
	while (1)
	{
	}
}

// Queue functions
void init_data_queue(Data_Queue * data_queue){
	data_queue->front = data_queue->size = 0;
	data_queue->rear = DATA_QUEUE_CAPACITY - 1;
	data_queue->capacity = DATA_QUEUE_CAPACITY;
}

void enqueue_data(uint16_t config, uint16_t data, Data_Queue * data_queue){
	data_queue->rear = (data_queue->rear + 1) % data_queue->capacity;
	data_queue->array[data_queue->rear][0] = config;
	data_queue->array[data_queue->rear][1] = data;
	data_queue->size = data_queue->size + 1;
}

void dequeue_data(uint16_t * config, uint16_t * data, Data_Queue * data_queue){
	if(!is_queue_empty(data_queue)){
		*config = data_queue->array[data_queue->front][0];
		*data = data_queue->array[data_queue->front][1];
		data_queue->front = (data_queue->front + 1) % data_queue->capacity;
		data_queue->size = data_queue->size - 1;
	}else{
		*data = *config = 0;
	}
}

int is_queue_full(Data_Queue * data_queue){
	return (data_queue->size == data_queue->capacity);
}

int is_queue_empty(Data_Queue * data_queue){
	return (data_queue->size == 0);
}

//void flush_latest(int discarded_channels){
	//data_queue->front = (data_queue->front + discarded_channels) % data_queue->capacity;
	//data_queue->size = data_queue->size - discarded_channels;
//}
