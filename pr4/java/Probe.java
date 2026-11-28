import java.util.Locale;

/** Checks converter behavior independently from profiling measurements. */
public class Probe {
    public static int check() {
        int[] operations = {2, 3, 4};
        double[] inputs = {1000, 0, 32};
        double[] expected = {1, 32, 0};
        int failures = 0;
        for (int index = 0; index < operations.length; index++) {
            double actual = Converter.convert(operations[index], inputs[index]);
            boolean passed = Double.isFinite(actual)
                    && Math.abs(actual - expected[index]) < 1e-9;
            if (!passed) failures++;
            System.out.printf(Locale.ROOT,
                    "case %d: input=%.2f actual=%.2f expected=%.2f %s%n",
                    operations[index], inputs[index], actual, expected[index],
                    passed ? "PASS" : "FAIL");
        }
        return failures;
    }

    public static double workload() {
        double checksum = 0;
        for (int index = 0; index < 20_000_000; index++) {
            checksum += Converter.convert(1, index);
        }
        return checksum;
    }

    public static void main(String[] args) {
        int failures = check();
        System.out.println("checksum=" + workload());
        int expectedFailures = args.length == 0 ? 0 : Integer.parseInt(args[0]);
        if (failures != expectedFailures) {
            throw new AssertionError("Unexpected number of failed scenarios: " + failures);
        }
    }
}
