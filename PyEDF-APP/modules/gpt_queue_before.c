#include "main.h"
#include "usbd_cdc_if.h"

#define BUFFER_SIZE 1024
#define QUEUE_SIZE 32

TaskHandle_t processingTaskHandle;

// Queue handle for storing incoming data batches
QueueHandle_t dataQueue;

// Buffer for storing incoming data
uint8_t dataBuffer[BUFFER_SIZE];

// Data structure for storing batch information
typedef struct {
    uint8_t *data;
    uint32_t length;
} Batch;

void processingTask(void *pvParameters) {
    Batch batch;
    uint32_t lastBatchTime = 0;
    uint32_t batchInterval = 100; // process batches every 100ms

    while (1) {
        if (xQueueReceive(dataQueue, &batch, portMAX_DELAY) == pdTRUE) {
            // Process the batch
            processBatch(batch);

            // Wait for the next batch interval
            while (HAL_GetTick() - lastBatchTime < batchInterval) {
                vTaskDelay(1);
            }
            lastBatchTime = HAL_GetTick();
        }
    }
}

void CDC_Receive_Callback(uint8_t *buf, uint32_t len) {
    // Create a new batch structure and copy the received data into it
    Batch batch;
    batch.data = malloc(len);
    memcpy(batch.data, buf, len);
    batch.length = len;

    // Add the batch to the queue
    if (xQueueSend(dataQueue, &batch, 0) != pdPASS) {
        // Failed to add batch to the queue, free the memory allocated for the batch
        free(batch.data);
    }
}

int main(void) {
    // Initialize the HAL and USB CDC interface
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_USB_DEVICE_Init();

    // Create the data queue
    dataQueue = xQueueCreate(QUEUE_SIZE, sizeof(Batch));

    // Create the processing task
    xTaskCreate(processingTask, "ProcessingTask", configMINIMAL_STACK_SIZE, NULL, tskIDLE_PRIORITY + 1, &processingTaskHandle);

    // Start the scheduler
    vTaskStartScheduler();

    // Infinite loop
    while (1) {}
}

void processBatch(Batch batch) {
    // Process the batch data here
    // ...

    // Free the memory allocated for the batch data
    free(batch.data);
}