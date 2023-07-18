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
#include <math.h>
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

// LDAC: 0b 101x-xxxx-xxxx-xx??
#define DAC_CONFIG_LDAC_LOW 0xA000			 // DAC registers updated continuously
#define DAC_CONFIG_LDAC_HIGH 0xA001			 // (DEFAULT) DAR reg. are latched and the input registers can change without affecting the contents of the DAC reg
#define DAC_CONFIG_LDAC_SINGLE_UPDATE 0xA003 // Causes a single pulse on LDAC, updating the DAC registers once.
// Reset:0b 111?-xxxx-xxxx-xxxx
#define DAC_CONFIG_RESET_DATA 0xE000			  // All outputs to zero
#define DAC_CONFIG_RESET_DATA_AND_CONTROL 0xF000 // reset all DAC

// Gain of output and reference selection

// Power-down:

/* END: Control Words  */

#define BUFFER_SIZE 64			// in bytess
#define PROTOCOL_WORD_SIZE 4 	// in bytes
#define SAMPLE_RATE 10			// Default sample_rate in msecs
#define DATA_QUEUE_CAPACITY 8192  // in DAC packages (16 bits or 2 bytes). Must be 32 at minimun
#define DACS_COUNT 4
#define DACS_CHANNEL_COUNT 8
#define SIMULATION_CHANNEL_COUNT 1 // This is the amount of data to dequeue by default

/**
 * @brief Structure of FIFO data queue
 */
/*
typedef struct Data_Queue{
	int front;	// = 0
	int rear; 	// = DATA_QUEUE_CAPACITY - 1;
	int size; 	// = 0;
	uint16_t capacity;	// = DATA_QUEUE_CAPACITY;
    uint16_t array[DATA_QUEUE_CAPACITY][2];
    	// [*][0] = config
    	// [*][1] = data
} Data_Queue;
*/

typedef struct Data_Queue{
    size_t head;
    size_t tail;
    size_t size;
    uint16_t array[DATA_QUEUE_CAPACITY][2];
    	// [*][0] = config
    	// [*][1] = data
} Data_Queue;

/**
 * @brief Array defining the DAC identifier
 */
typedef enum
{
	DAC_A = 0,
	DAC_B = 1,
	DAC_C = 2,
	DAC_D = 3
} DAC_Tag;

/**
 * @brief Array defining the DAC channels identifiers
 */
typedef enum
{
	CHANNEL_A = 0, // 0b000
	CHANNEL_B = 1, // 0b001
	CHANNEL_C = 2, // 0b010
	CHANNEL_D = 3, // 0b011
	CHANNEL_E = 4, // 0b100
	CHANNEL_F = 5, // 0b101
	CHANNEL_G = 6, // 0b110
	CHANNEL_H = 7  // 0b111
} DAC_Channel;

/**
 * @brief Struct to save the information about a DAC
 *
 * @param dac_tag Identifier for the DAC
 * @param dac_hspi SPI handler assigned to this DAC
 * @param dac_SS_GPIO_port Slave select port assigned to this DAC
 * @param dac_ss_GPIO_pin Slave select pin assigned to this DAC
 */
typedef struct DAC_Handler
{
	DAC_Tag dac_tag;
	SPI_HandleTypeDef *dac_hspi;
	GPIO_TypeDef *dac_SS_GPIO_port;
	uint16_t dac_ss_GPIO_pin;
} DAC_Handler;

/**
 * @brief Struct to save port and pin where LDAC is configured
 */
typedef struct LDAC_Handler
{
	GPIO_TypeDef *GPIO_LDAC_control_port;
	uint16_t GPIO_LDAC_control_pin;
} LDAC_Handler;

typedef enum
{
	// LDAC TRIGGER
	CONF_LDAC_TRIGGER = 33, // triggers all channels to write respective outputs
	// LDAC Config
	CONF_LDAC_LOW = 34,
	// RESET Config
	CONF_RESET = 35,
	// Power-down Config
	CONF_SIMULATION_CHANNEL_COUNT = 39,
	CONF_SAMPLE_RATE = 40
} config_protocol_word;

/**
 * @brief Enum that relates EEG channels to values
 */
typedef enum
{
	// DAC A
	CH_Fp1 = 0,
	CH_Fz = 1,
	CH_Fp2 = 2,
	CH_F3 = 3,
	CH_F4 = 4,
	CH_C3 = 5,
	CH_C4 = 6,
	CH_P3 = 7,
	// DAC B
	CH_P4 = 8,
	CH_O1 = 9,
	CH_O2 = 10,
	CH_F7 = 11,
	CH_F8 = 12,
	CH_T7 = 13,
	CH_T8 = 14,
	CH_P7 = 15,
	// DAC C
	CH_P8 = 16,
	CH_Pz = 17,
	CH_Cz = 18,
	CH_PG1 = 19,
	CH_PG2 = 20,
	CH_AFz = 21,
	CH_FCz = 22,
	CH_CPz = 23,
	// DAC D
	CH_CP3 = 24,
	CH_CP4 = 25,
	CH_FC3 = 26,
	CH_FC4 = 27,
	CH_TP7 = 28,
	CH_TP8 = 29,
	CH_FT7 = 30,
	CH_FT8 = 31,

	MAX_DAC_CHANNEL_WORD = 32 // RESERVED: no significa nada, pero sirve para identificar que hasta el enum = 31 nos referimos a un canal de DAC
} channel_protocol_word;

/* Functions */

/**
 * @brief Initializes a DAC handler structure
 *
 * @param[in] dac_tag DAC tag assigned to this DAC
 * @param[in] hspi SPI handler assigned to this DAC
 * @param[in] GPIOx GPIO group assigned to this DAC
 * @param[in] GPIO_Pin GPIO pin assigned to this DAC
 * @param[out] dac_handler Filled structure containing the DAC information
 */
void init_dac_handler(const DAC_Tag dac_tag, const SPI_HandleTypeDef *hspi, const GPIO_TypeDef *GPIOx, const uint16_t GPIO_Pin, DAC_Handler *dac_handler);

/**
 * @brief Resets DACs configuration
 *
 * @param[in] list_of_dacs List of DACs to reset
 * @param[in] dacs_count Amount of DACs in list
 */
void reset_dacs_config(const DAC_Handler list_of_dacs[], const uint8_t *dacs_count);

/**
 * @brief Sets the LDAC flag in the DACs
 *
 * @param[in] list_of_dacs List of DACs to reset
 * @param[in] dacs_count Amount of DACs in list
 */
void init_LDAC_in_dacs(const DAC_Handler list_of_dacs[], const uint8_t *dacs_count);

// Init the ports that control LDAC in the LDAC_settings variable.
/**
 * @brief Initializes the LDAC handler variable
 *
 * @param[in] GPIOx GPIO group assigned to the LDAC
 * @param[in] GPIO_Pin GPIO pin assigned to the LDAC
 * @param[out] LDAC_settings LDAC structure to fill
 */
void init_LDAC(const GPIO_TypeDef *GPIOx, const uint16_t GPIO_Pin, LDAC_Handler *LDAC_settings);

/**
 * @brief Parses the configuration from the incoming package
 *
 * @param[in] bufferUSB Received bytes package
 * @param[in] pconfig to store config word
 * @param[in] pdata to store data word
 *
 * @return config and data with respective values
 */
void parse_receiving_buffer(const uint8_t *bufferUSB, uint16_t *config, uint16_t *data);

/**
 * @brief Parses the DAC_tag and DAC_channel from the received config
 * @details Used only if the received configuration indicates to send this package to a DAC
 *
 * @param[in] config Received configuration
 * @param[out] DAC_tag Tag representing which DAC to send the data to
 * @param[out] DAC_channel Int representing which channel of the DAC to send the data to
 */
void parse_tag_and_channel_from_config(const uint16_t *config, DAC_Tag *DAC_tag, DAC_Channel *DAC_channel);

/**
 * @brief Sends data to the channel of a DAC
 * @details Does not trigger the DAC output, this is done separately
 *
 * @param[in] dac_handler Indicates to which DAC to send the data to
 * @param[in] dac_channel Indicates the DAC channel to sent the data to
 * @param[in] data to send
 */
HAL_StatusTypeDef send_data_to_dac_channel(const DAC_Handler *dac_handler, const DAC_Channel *dac_channel, uint16_t data);

/**
 * @brief Gets the channel address mask
 *
 * @returns The channel address mask for a particular DAC channel
 */
uint8_t get_dac_channel_addr_mask(const DAC_Channel *dac_channel);

/**
 * @brief Sends a configuration package to the DAC
 *
 * @param[in] config Configuration package to send
 * @param[in] list_of_dacs DACs to send the config to
 * @param[in] dacs_count Amount of DACs in the list
 */
HAL_StatusTypeDef send_configuration_to_dacs(const uint16_t *config, const uint16_t *data, const DAC_Handler *list_of_dacs[], const uint8_t *dacs_count, Data_Queue * data_queue );

/**
 * @brief Sends a word to the DAC, used for the configs
 *
 * @param[in] word Word to send
 * @param[in] dac_handler DAC handler containing the information of where to send it
*/
HAL_StatusTypeDef _send_word_to_dac(uint16_t word, DAC_Handler *dac_handler);

/**
 * @brief Triggers the LDAC pin
 */
void trigger_LDAC();

/**
 * @brief Sets sample_rate global variable value
 */
void config_sample_rate_delay(const uint16_t data);

/**
 * @brief Sets How many channels will be used in next simulation
 */
void config_simulation_channel_count(const uint16_t data);


/************* Test functions *************/

/**
 * @brief Test a pulse signal in all DACs and Channels
 */
void test_send_pulse(const DAC_Handler list_of_dacs[]);

/**
 * @brief Test a pulse signal in all DACs and Channels
 */
void test_send_saw(const DAC_Handler list_of_dacs[]);



/************* Error functions *************/
void EEG_simulation_error_Handler(void);


/************* Queue functions *************/

/**
 * @brief enqueue data in the rear of the queue
 */
void init_data_queue(Data_Queue * data_queue);

/**
 * @brief enqueue data in the rear of the queue
 */
void enqueue_data(uint16_t config, uint16_t data, Data_Queue * data_queue);

/**
 * @brief dequeue data in the front of the queue
 */
void dequeue_data(uint16_t * config, uint16_t * data, Data_Queue * data_queue);

/**
 * @brief Is the queue full?. 1 = True. 0 = False
 */
int is_queue_full(Data_Queue * data_queue);


/**
 * @brief Is the queue empty?. 1 = True. 0 = False
 */
int is_queue_empty(Data_Queue * data_queue);

/**
 * @brief Dequeue discarded channels
 */
void flush_discard_channels(Data_Queue * data_queue, int discarded_channels);

#endif /* INC_EEG_SIMULATION_H_ */
