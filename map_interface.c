#include <map_interface.h>

void servo_uart_init(void){
    WDTCTL = WDTPW | WDTHOLD; // Stop watchdog timer.
    BCSCTL1 = CALBC1_1MHZ;    // Set DCO to 1 MHz.
    DCOCTL = CALDCO_1MHZ;

    P1SEL = BIT1 | BIT2;      // Set up pins for UART.
    P1SEL2 = BIT1 | BIT2;

    UCA0CTL1 |= UCSWRST;      // Hold USCI in reset to configure.
    UCA0CTL1 |= UCSSEL_2;     // SMCLK
    UCA0BR0 = 52;             // 1MHz / 19200 = 52.
    UCA0BR1 = 0;
    UCA0MCTL = UCBRS0;        // Modulation UCBRSx = 0.
    UCA0CTL1 &= ~UCSWRST;     // Initialize USCI state machine.
    IE2 |= UCA0RXIE;          // Enable USCI_A0 RX interrupt.

    // PWM period.
    TACCR0 = 20000;  //PWM period.

    P1DIR |= BIT6;
    P1SEL |= BIT6;  // selection for timer setting.
}

int map(double val, double from_min, double from_max, int to_min, int to_max) {

    // Calculate percentage based on how close val is to from_max rather than from_min.
    double percentage = (from_max - val) / (from_max - from_min);

    // Calculate the target value based on the reversed percentage.
    int mapped_value = percentage * (to_max - to_min) + to_min;

    // Clamp values to the specified range to avoid overflows.
    if (mapped_value < to_min) {
        return to_min;
    }

    if (mapped_value > to_max) {
        return to_max;
    }

    return mapped_value;
}




