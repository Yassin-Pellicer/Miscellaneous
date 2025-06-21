import java.util.Scanner;
public class DatosCumpleaños {
    
    private int edad;
    private int diaNac;
    private int mesNac;

    //PARA QUE LA CALL FUNCIONE TANTO EL NOMBRE DEL ARCHIVO COMO EL NOMBRE DE LA CLASE public DatosCumpleaños HA DE SER EL MISMO//

    public DatosCumpleaños(int edad, int diaNac, int mesNac){
        this.edad = edad;
        this.diaNac = diaNac;
        this.mesNac = mesNac;
    }
        public String toString(){
        return ", de "+this.edad+" años, nacido el día "+this.diaNac+" del mes "+this.mesNac;
    }
    public static void main(String[] args){
        Scanner sc = new Scanner(System.in);

        System.out.print("Hola, dinos tu nombre por favor: ");
        String nombre = sc.nextLine();

        System.out.printf("\n\nPor favor, introduce tu edad: ");
        int i = sc.nextInt();
        System.out.printf("\nPor favor, introduce tu día de nacimiento: ");
        int j = sc.nextInt();
        System.out.printf("\nPor favor, introduce tu mes de nacimiento: ");
        int k = sc.nextInt();

            DatosCumpleaños x = new DatosCumpleaños(i, j, k);
                System.out.printf("\n"+nombre);
                System.out.printf(x.toString());
                System.out.println(", es una persona muy guapa!\n");

        sc.close();
        }
        
}
