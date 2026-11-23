import java.util.Scanner;
/** Simple unit converter. */
public class Converter {
    /** Convert kilometres, metres, Celsius and Fahrenheit. */
    public static double convert(int operation, double value) {
        switch (operation) {
            case 1: return value * 1000;
            case 2: return value / 1000;
            case 3: return value * 9 / 5 + 32;
            case 4: return (value - 32) * 5 / 9;
            default: throw new IllegalArgumentException("Unknown operation");
        }
    }
    /** Read operation and value. */
    public static void main(String[] args) {
        try (Scanner input = new Scanner(System.in)) {
            System.out.println("1 km->m; 2 m->km; 3 C->F; 4 F->C");
            int operation = input.nextInt();
            double value = input.nextDouble();
            System.out.println("Result: " + convert(operation, value));
        }
    }
}
