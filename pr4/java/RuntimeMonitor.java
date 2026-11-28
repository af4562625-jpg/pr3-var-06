import java.lang.management.ManagementFactory;
import java.lang.management.MemoryMXBean;
import java.lang.management.ThreadMXBean;
import java.nio.file.Path;
import jdk.jfr.Event;
import jdk.jfr.Label;
import jdk.jfr.Name;
import jdk.jfr.Recording;

/** Collects JMX measurements and saves a JFR recording of the same run. */
public class RuntimeMonitor {
    @Name("pr4.Workload")
    @Label("PR4 converter workload")
    static class WorkloadEvent extends Event {
        @Label("Iterations")
        long iterations;
        @Label("Checksum")
        double checksum;
    }

    public static void main(String[] args) throws Exception {
        Path output = Path.of(args.length > 0 ? args[0] : "run.jfr");
        int expectedFailures = args.length > 1 ? Integer.parseInt(args[1]) : 0;
        MemoryMXBean memory = ManagementFactory.getMemoryMXBean();
        ThreadMXBean thread = ManagementFactory.getThreadMXBean();
        boolean cpuAvailable = thread.isCurrentThreadCpuTimeSupported();
        if (cpuAvailable && !thread.isThreadCpuTimeEnabled()) {
            thread.setThreadCpuTimeEnabled(true);
        }
        int failures;
        try (Recording recording = new Recording()) {
            // Avoid collecting environment variables or JVM arguments.
            recording.enable(WorkloadEvent.class).withThreshold(java.time.Duration.ZERO);
            recording.enable("jdk.ExecutionSample").withPeriod(java.time.Duration.ofMillis(10));
            recording.enable("jdk.GarbageCollection");
            recording.enable("jdk.GCHeapSummary");
            recording.enable("jdk.ThreadAllocationStatistics")
                    .withPeriod(java.time.Duration.ofMillis(100));
            recording.start();
            System.out.println("JFR state: " + recording.getState());
            long heapBefore = memory.getHeapMemoryUsage().getUsed();
            long cpuBefore = cpuAvailable ? thread.getCurrentThreadCpuTime() : -1;
            long started = System.nanoTime();
            WorkloadEvent event = new WorkloadEvent();
            event.begin();
            failures = Probe.check();
            event.iterations = 20_000_000;
            event.checksum = Probe.workload();
            event.end();
            event.commit();
            long elapsed = System.nanoTime() - started;
            long cpuElapsed = cpuAvailable ? thread.getCurrentThreadCpuTime() - cpuBefore : -1;
            long heapAfter = memory.getHeapMemoryUsage().getUsed();
            System.out.println("JMX MemoryMXBean heap before bytes: " + heapBefore);
            System.out.println("JMX MemoryMXBean heap after bytes: " + heapAfter);
            System.out.println("JMX ThreadMXBean CPU supported: " + cpuAvailable);
            System.out.println("JMX ThreadMXBean current thread CPU ns: " + cpuElapsed);
            System.out.println("Wall time ns: " + elapsed);
            System.out.println("checksum=" + event.checksum);
            recording.stop();
            recording.dump(output);
            System.out.println("JFR file: " + output.getFileName());
            System.out.println("BEHAVIOR: " + (3 - failures)
                    + "/3 passed; expected failures=" + expectedFailures);
        }
        if (failures != expectedFailures) {
            throw new AssertionError("Unexpected number of failed scenarios: " + failures);
        }
    }
}
