/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * <h2><center>&copy; Copyright (c) 2021 STMicroelectronics.
  * All rights reserved.</center></h2>
  *
  * This software component is licensed by ST under BSD 3-Clause license,
  * the "License"; You may not use this file except in compliance with the
  * License. You may obtain a copy of the License at:
  *                        opensource.org/licenses/BSD-3-Clause
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
SPI_HandleTypeDef hspi1;

/* USER CODE BEGIN PV */

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_SPI1_Init(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_SPI1_Init();
  /* USER CODE BEGIN 2 */

  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  uint8_t  sine_wave[256*2] = {
  	        0x0, 0x20,0xc0, 0x20,0x80, 0x21,0x40, 0x22,0x0, 0x23,0x0, 0x24,0xc0, 0x24,0x80, 0x25,0x40, 0x26,
  	        0x0, 0x27,0xc0, 0x27,0x80, 0x28,0x40, 0x29,0x0, 0x2a,0xc0, 0x2a,0x80, 0x2b,0x40, 0x2c,0xc0, 0x2c,
  	        0x80, 0x2d,0x40, 0x2e,0x0, 0x2f,0xc0, 0x2f,0x40, 0x30,0x0, 0x31,0xc0, 0x31,0x40, 0x32,0x0, 0x33,
  	        0x80, 0x33,0x40, 0x34,0xc0, 0x34,0x40, 0x35,0x0, 0x36,0x80, 0x36,0x0, 0x37,0x80, 0x37,0x0, 0x38,
  	        0x80, 0x38,0x0, 0x39,0x80, 0x39,0x0, 0x3a,0x80, 0x3a,0xc0, 0x3a,0x40, 0x3b,0xc0, 0x3b,0x0, 0x3c,
  	        0x40, 0x3c,0xc0, 0x3c,0x0, 0x3d,0x40, 0x3d,0x80, 0x3d,0x0, 0x3e,0x40, 0x3e,0x80, 0x3e,0x80, 0x3e,
  	        0xc0, 0x3e,0x0, 0x3f,0x40, 0x3f,0x40, 0x3f,0x80, 0x3f,0x80, 0x3f,0x80, 0x3f,0xc0, 0x3f,0xc0, 0x3f,
  	        0xc0, 0x3f,0xc0, 0x3f,0xc0, 0x3f,0xc0, 0x3f,0xc0, 0x3f,0x80, 0x3f,0x80, 0x3f,0x80, 0x3f,0x40, 0x3f,
  	        0x40, 0x3f,0x0, 0x3f,0xc0, 0x3e,0x80, 0x3e,0x80, 0x3e,0x40, 0x3e,0x0, 0x3e,0x80, 0x3d,0x40, 0x3d,0x0,
  	         0x3d,0xc0, 0x3c,0x40, 0x3c,0x0, 0x3c,0xc0, 0x3b,0x40, 0x3b,0xc0, 0x3a,0x80, 0x3a,0x0, 0x3a,0x80, 0x39,
  	         0x0, 0x39,0x80, 0x38,0x0, 0x38,0x80, 0x37,0x0, 0x37,0x80, 0x36,0x0, 0x36,0x40, 0x35,0xc0, 0x34,0x40,
  	         0x34,0x80, 0x33,0x0, 0x33,0x40, 0x32,0xc0, 0x31,0x0, 0x31,0x40, 0x30,0xc0, 0x2f,0x0, 0x2f,0x40, 0x2e,
  	         0x80, 0x2d,0xc0, 0x2c,0x40, 0x2c,0x80, 0x2b,0xc0, 0x2a,0x0, 0x2a,0x40, 0x29,0x80, 0x28,0xc0, 0x27,0x0,
  	          0x27,0x40, 0x26,0x80, 0x25,0xc0, 0x24,0x0, 0x24,0x0, 0x23,0x40, 0x22,0x80, 0x21,0xc0, 0x20,0x0, 0x20,0x40,
  	           0x1f,0x80, 0x1e,0xc0, 0x1d,0x0, 0x1d,0x0, 0x1c,0x40, 0x1b,0x80, 0x1a,0xc0, 0x19,0x0, 0x19,0x40, 0x18,0x80,
  	            0x17,0xc0, 0x16,0x0, 0x16,0x40, 0x15,0x80, 0x14,0xc0, 0x13,0x40, 0x13,0x80, 0x12,0xc0, 0x11,0x0, 0x11,0x40,
  	             0x10,0xc0, 0xf,0x0, 0xf,0x40, 0xe,0xc0, 0xd,0x0, 0xd,0x80, 0xc,0xc0, 0xb,0x40, 0xb,0xc0, 0xa,0x0, 0xa,0x80,
  	              0x9,0x0, 0x9,0x80, 0x8,0x0, 0x8,0x80, 0x7,0x0, 0x7,0x80, 0x6,0x0, 0x6,0x80, 0x5,0x40, 0x5,0xc0, 0x4,0x40,
  	               0x4,0x0, 0x4,0xc0, 0x3,0x40, 0x3,0x0, 0x3,0xc0, 0x2,0x80, 0x2,0x0, 0x2,0xc0, 0x1,0x80, 0x1,0x80,
  	                0x1,0x40, 0x1,0x0, 0x1,0xc0, 0x0,0xc0, 0x0,0x80, 0x0,0x80, 0x0,0x80, 0x0,0x40, 0x0,0x40, 0x0,0x40,
  	                 0x0,0x40, 0x0,0x40, 0x0,0x40, 0x0,0x40, 0x0,0x80, 0x0,0x80, 0x0,0x80, 0x0,0xc0, 0x0,0xc0, 0x0,0x0,
  	                  0x1,0x40, 0x1,0x80, 0x1,0x80, 0x1,0xc0, 0x1,0x0, 0x2,0x80, 0x2,0xc0, 0x2,0x0, 0x3,0x40, 0x3,0xc0,
  	                   0x3,0x0, 0x4,0x40, 0x4,0xc0, 0x4,0x40, 0x5,0x80, 0x5,0x0, 0x6,0x80, 0x6,0x0, 0x7,0x80, 0x7,0x0,
  	                    0x8,0x80, 0x8,0x0, 0x9,0x80, 0x9,0x0, 0xa,0xc0, 0xa,0x40, 0xb,0xc0, 0xb,0x80, 0xc,0x0, 0xd,0xc0,
  	                     0xd,0x40, 0xe,0x0, 0xf,0xc0, 0xf,0x40, 0x10,0x0, 0x11,0xc0, 0x11,0x80, 0x12,0x40, 0x13,0xc0,
  	                      0x13,0x80, 0x14,0x40, 0x15,0x0, 0x16,0xc0, 0x16,0x80, 0x17,0x40, 0x18,0x0, 0x19,0xc0, 0x19,
  	                      0x80, 0x1a,0x40, 0x1b,0x0, 0x1c,0x0, 0x1d,0xc0, 0x1d,0x80, 0x1e
    };


  while (1)
  {
		 HAL_GPIO_TogglePin(GPIOA,GPIO_PIN_1);

		 HAL_SPI_Transmit(&hspi1, sine_wave, 256-1, 1);
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }

  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_NONE;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }
  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_HSI;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_0) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief SPI1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_SPI1_Init(void)
{

  /* USER CODE BEGIN SPI1_Init 0 */

  /* USER CODE END SPI1_Init 0 */

  /* USER CODE BEGIN SPI1_Init 1 */

  /* USER CODE END SPI1_Init 1 */
  /* SPI1 parameter configuration*/
  hspi1.Instance = SPI1;
  hspi1.Init.Mode = SPI_MODE_MASTER;
  hspi1.Init.Direction = SPI_DIRECTION_2LINES;
  hspi1.Init.DataSize = SPI_DATASIZE_16BIT;
  hspi1.Init.CLKPolarity = SPI_POLARITY_LOW;
  hspi1.Init.CLKPhase = SPI_PHASE_1EDGE;
  hspi1.Init.NSS = SPI_NSS_HARD_OUTPUT;
  hspi1.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_2;
  hspi1.Init.FirstBit = SPI_FIRSTBIT_MSB;
  hspi1.Init.TIMode = SPI_TIMODE_DISABLE;
  hspi1.Init.CRCCalculation = SPI_CRCCALCULATION_DISABLE;
  hspi1.Init.CRCPolynomial = 10;
  if (HAL_SPI_Init(&hspi1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN SPI1_Init 2 */

  /* USER CODE END SPI1_Init 2 */

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOA_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOA, GPIO_PIN_1, GPIO_PIN_RESET);

  /*Configure GPIO pin : PA1 */
  GPIO_InitStruct.Pin = GPIO_PIN_1;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
