import java.lang.management.ManagementFactory;
import java.lang.management.MemoryMXBean;
import java.lang.management.ThreadMXBean;
public class RuntimeMonitor {
  public static void main(String[] args) {
    MemoryMXBean memory=ManagementFactory.getMemoryMXBean();
    ThreadMXBean cpu=ManagementFactory.getThreadMXBean();
    long start=cpu.getCurrentThreadCpuTime();
    long used=memory.getHeapMemoryUsage().getUsed();
    Probe.main(new String[0]);
    long elapsed=cpu.getCurrentThreadCpuTime()-start;
    System.out.println("Thread CPU ns: "+elapsed);
    System.out.println("Heap before bytes: "+used);
    System.out.println("Heap after bytes: "+memory.getHeapMemoryUsage().getUsed());
  }
}
