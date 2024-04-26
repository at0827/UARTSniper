#include <msp430.h>

#define LED BIT6  // LED is on P1.6
volatile int x_coordinate;
unsigned int PWM_value = 0;

void main(void) {
    servo_uart_init();
    __bis_SR_register(GIE); // Enter LPM0, interrupts enabled.
}

// Move to appropriate x position using the x pwm.
void engage_target(int x_pwm){
    TACCR1 = x_pwm;
    TACCTL1 = OUTMOD_7;      // CCR1 selection reset-set.
    TACTL = TASSEL_2|MC_1;   // SMCLK submain clock,upmode.

    __delay_cycles(1000);

    // The following function triggers the diode to turn on and off.
    // shoot_laser();
}

// Turn on the diode.
void shoot_laser() {

    // Turn on diode to fire.
    P2DIR |= BIT3; // Set P2.3 as output.
    P2OUT |= BIT3; // Turn on the pin.

    __delay_cycles(2500000);

    // Turn off diode when done firing.
    P2OUT &= ~BIT3; // Turn off the pin.
}

#pragma vector=USCIAB0RX_VECTOR
__interrupt void USCI0RX_ISR(void) {
    x_coordinate = UCA0RXBUF;

    // x-coordinates must be calibrated (corners of frame with LED position)!
    PWM_value = map(x_coordinate, 0, 180, 1345, 1630);

    engage_target(PWM_value);
}


