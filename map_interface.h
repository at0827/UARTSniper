/*
 * map_interface.h
 *
 *  Created on: Mar 12, 2021
 *      Author: ckemere
 */

#ifndef MAP_INTERFACE_H_
#define MAP_INTERFACE_H_
#include <msp430.h>

void servo_uart_init(void);
int map(double val, double from_min, double from_max, int to_min, int to_max);

#endif /* MAP_INTERFACE_H_ */
