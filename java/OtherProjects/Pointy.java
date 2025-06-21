import java.util.Scanner;
public class Pointy {
    
    private static int x;
    private static int y;
    
    public Pointy(int x, int y){
        Pointy.x=x;
        Pointy.y=y;
    }
    
    public void setX(int x){
        Pointy.x=x;

    }
    public void setY(int y){
        Pointy.y=y;
    }
    public String toString(){
        return "("+ Pointy.x+","+Pointy.y+")";
    }
    
    public static void main(String[] args){

        Scanner sc = new Scanner(System.in);
        System.out.printf("¡Hola! por favor, introduzca las coordenadas x de su punto: ");
        int getx = sc.nextInt();
        System.out.printf("\nIntroduzca las coordenadas y de su punto: ");
        int gety = sc.nextInt();

        Pointy point= new Pointy(getx, gety);
                System.out.println(point.toString());
               
        sc.close();
    }
    
    
}