public class Probe {
  public static void main(String[] args) {
    int[] op={2,3,4}; double[] in={1000,0,32}; double[] want={1,32,0};
    for(int i=0;i<3;i++){
      double actual=Converter.convert(op[i],in[i]);
      System.out.printf("case %d: actual=%.2f expected=%.2f %s%n",op[i],actual,want[i],Math.abs(actual-want[i])<1e-9?"PASS":"FAIL");
    }
    double sum=0; for(int i=0;i<20000000;i++) sum+=Converter.convert(1,i);
    System.out.println("checksum="+sum);
  }
}
