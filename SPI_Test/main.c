#include "stm32f10x.h"
#include "systick_time.h"
#include "gp_drive.h"

/**
 * SPI 1
 * PA4 -> ss
 * PA5 -> SCLK
 * PA6 -> MISO
 * PA7 -> MOSI 
 * */


int main(void){
    // Activate SPI1 peripheral / AFIO function
    // APB2 Register pin 12 enables dthe spi1
    RCC->APB2ENR |= 1;      // Enable AFIO function
    RCC->APB2ENR |= 0x1000; // Enable SPI/1 peripheral
    // Set up the pin
    init_GP(PA,4,OUT50,O_GP_PP);
    init_GP(PA,5,OUT50,O_AF_PP);
    init_GP(PA,6,IN,I_PP);
    init_GP(PA,7,OUT50,O_AF_PP);
    /************Setup SPI peripherals*******/
    SPI1->CR1 |= 0x4;   // Master Mode
    SPI1->CR1 |= 0x31;  // Fclk / 256  (el mas lento)
    SPI1->CR1 |= 0x40;   // Enable SPI SPI periph
    W_GP(PA,4,HIGH);

    while(1){
        //Sending some data
        DelayMs(50);
        W_GP(PA,4,LOW);
        SPI1->DR = 'x';
        W_GP(PA,4,HIGH);
    }

}











