# Ejemplo Triangular:

En el loop while() poner el siguiente código

```c
  uint8_t i = 0;
  while (1)
  {
	 HAL_GPIO_TogglePin(GPIOA,GPIO_PIN_1);
	// HAL_Delay(1);

	 //bufferTx[1] = NORMALOPERATION || (~sine_wave[i]*Escaler)>>2;
	 //bufferTx[0] = (~sine_wave[i+1]*Scaler)<<6;

	// buffer = buffer+ 1;
	 buffer[0] = i<<6;
	 buffer[1] = i>>2;
	 i++;
	// HAL_SPI_Transmit(&hspi1, (uint8_t*)(buffer), sizeof(buffer)/(sizeof(uint8_t)*2), 1);
	 HAL_SPI_Transmit(&hspi1, buffer, 1, 1);


	 //i++;
	 //if(i == 255){i = 0;}
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }
  ```
