#include "main.h"
#include "usbd_cdc_if.h"

#define BUFFER_SIZE 1024

TaskHandle_t processingTaskHandle;

// Buffer for storing incoming data
uint8_t dataBuffer[BUFFER_SIZE];
uint32_t dataLength = 0;

// Timer handle for controlling the rate of byte processing
TIM_HandleTypeDef htim;

void processingTask(void *pvParameters) {
    uint32_t lastByteTime = 0;
    uint32_t byteInterval = 10; // process each byte every 10ms

    while (1) {
        // Process each byte in the data buffer
        for (uint32_t i = 0; i < dataLength; i++) {
            // Wait for the specified interval before processing the next byte
            while (HAL_GetTick() - lastByteTime < byteInterval) {
                vTaskDelay(1);
            }
            lastByteTime = HAL_GetTick();

            // Process the byte
            processByte(dataBuffer[i]);
        }

        // Reset the data buffer length after processing is complete
        dataLength = 0;
    }
}

void CDC_Receive_Callback(uint8_t *buf, uint32_t len) {
    // Append the received data to the end of the data buffer
    if (dataLength + len > BUFFER_SIZE) {
        // Data buffer overflow, discard the excess data
        len = BUFFER_SIZE - dataLength;
    }
    memcpy(dataBuffer + dataLength, buf, len);
    dataLength += len;
}

void processByte(uint8_t byte) {
    // Process the byte data here
    // ...
}

int main(void) {
    // Initialize the HAL and USB CDC interface
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_USB_DEVICE_Init();

    // Configure the timer for byte processing rate control
    TIM_ClockConfigTypeDef sClockSourceConfig = {0};
    TIM_MasterConfigTypeDef sMasterConfig = {0};
    htim.Instance = TIM2;
    htim.Init.Prescaler = (SystemCoreClock / 1000) - 1;
    htim.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim.Init.Period = 1;
    htim.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    HAL_TIM_Base_Init(&htim);
    sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
    HAL_TIM_ConfigClockSource(&htim, &sClockSourceConfig);
    sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
    sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
    HAL_TIMEx_MasterConfigSynchronization(&htim, &sMasterConfig);

    // Create the processing task
    xTaskCreate(processingTask, "ProcessingTask", configMINIMAL_STACK_SIZE, NULL, tskIDLE_PRIORITY + 1, &processingTaskHandle);

    // Start the timer for byte processing rate control
    HAL_TIM_Base_Start(&htim);

    // Start the scheduler
    vTaskStartScheduler();

    // Infinite loop
    while (1) {}
}