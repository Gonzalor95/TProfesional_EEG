# TProfesional_EEG

Trabajo Profesional para la carrera de Ingeniería Electrónica de FIUBA

Alumnos:
Rizzo Gonzalo
Davila Galesio Ignacio
Carosella Juan Manuel

Este repositorio contiene los archivos de software (codigo fuente y simulacion) generados para el trabajo final. Se divide en dos carpetas:

- CubeIDE_projects contiene los archivos relacionados a la programación y configuracion del microcontrolador junto con el software escrito para el mismo
- Proteus_projects contiene los archivos de simulacion

# Notas de reuniones

## 23/9/2021

Microprocesador para experimentar: STM32F103c8t6 (BluePill)  

Simular alternativas:

-I2C: 
  * Definir si la baja velocidad del clock afecta significativamente la performance.
  * Simular un sistema lo más parecido posible a lo que nos proponemos. Es decir, debemos tener 32 salidas. En el caso de utilizar el LTC2631-HZ12 que solo tiene una salida y solo logra 9 direcciones, simular el caso de 32 canales repitiendo reiteradas veces la escritura en cada DAC.
  * Revisar si el Proteus no tiene un modelo con I2C con mayor cantidad de salidas.

-SPI:
  * En este caso, dado que el Blue Pill tiene solo 2 salidas de SPI disponibles, simular con un DAC con la mayor cantidad de salidas posibles.
  * La velocidad en este caso, no debería ser un factor limitante (REVISAR)

Definir cual conviene para proseguir. Pros y contras de cada una.

Comenzar a pensar las características importantes para el usuario (debe utilizar computadora, como se va a conectar al micro, como va a cargar las librerias, si se utiliza una memoria externa, etc)

Experimentar con la librería EDF, ver si en una simulación podemos obteenr un output utilizando dicha librería.
