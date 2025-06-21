import java.util.Scanner;
public class PuntoComparador{

    public static void main(String[] args){

        double x = 0;
        double y = 0;

        Scanner sc = new Scanner(System.in);
        System.out.printf("Introduzca su coordenada x:\n");
        x = sc.nextDouble();
        System.out.printf("Introduzca su coordenada y:\n");       
        y = sc.nextDouble();

        System.out.printf("El valor de la x es: " +x +"\n");
        System.out.printf("El valor de la x es: "+y+"\n");

        sc.close();
    }
}