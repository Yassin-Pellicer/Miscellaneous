public class fibonacci{
    public static void main(String[] args) {
        System.out.println(fibonacciSequence(14));
    }

    //solución iterativa
    public static int fibonacciSequence(int n){
        int i = 1;
        int Result = 1;
        int prevResult = 0;
        
        if(n == 0){
            return 0;
        }

        while(i < n){
            Result = Result + prevResult;
            prevResult = Result - prevResult;
            i++;
        }
        return Result;
    }
}