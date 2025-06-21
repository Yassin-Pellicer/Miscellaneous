import java.io.*;
import java.util.*;

public class launcher {

    public static Scanner sc = null;
    public static boolean Over = false;
    public static int entryNum = 0;

    public static void main(String[] args) {

        FileInputStream fileR = null;
        
        try {
            fileR = new FileInputStream("vocab");
        }
        catch (FileNotFoundException e){
            e.printStackTrace();
        }
        sc = new Scanner(fileR);

        while(sc.hasNextLine() && sc.nextLine() != null){
            entryNum++;
        }

        System.out.println("¡Bienvenido al test de vocabulario de alemán!\n\n¿Qué desea hacer?");

        do{
            init();
            System.out.print("\033\143");
        }while(!Over);

        System.out.println("Hasta la próxima!");

        try{
            Thread.sleep(2000);
        }
        catch(InterruptedException e){
            e.printStackTrace();
        }
    }

    public static String[] takeParts(String s, char t){
        String[] ret = new String[2];
        int i = 0;

        while(i < s.length()){
            if(s.charAt(i) == t){
                ret[0] = s.substring(0, i);
                break;
            }
            i++;
        }
        ret[1] = s.substring(i, s.length());

        return ret;
    }

    public static String RandEntry(){

        FileInputStream fileR = null;
        
        try {
            fileR = new FileInputStream("vocab");
        }
        catch (FileNotFoundException e){
            e.printStackTrace();
        }

        double r = Math.random();
        double n = Math.ceil(r*entryNum);

        sc = new Scanner(fileR);

        int i = 0;
        String s = "";
        while(n >= i+1){
            s = standardize(sc.nextLine());
            i++;
        }

        return s;
    }

    public static void ExamToSpanish(int NumQuest){
        String[] s = new String[2];
        System.out.println("EXAMEN DE VOCABULARIO:\n");

        System.out.println("ESCRIBA LA TRADUCCIÓN DE LA PALABRA AL ESPAÑOL:");
        System.out.println("Escriba su palabra sin acentos ni ñ (use ny).\n");

        for(int i = 0; i < NumQuest; i++){
            s = takeParts(RandEntry(), ':');
            System.out.println(s[0]);
            
            sc = new Scanner(System.in);
            String k = sc.nextLine();
            if(k == " "){};
            System.out.println("La palabra era"+s[1]+"\n");
        }
    }

    public static String standardize(String s){
        String ret = "";
        for(int i = 0; i < s.length(); i++){
            switch(s.charAt(i)){
                case 'á':
                    ret += "a";
                break;
                case 'é':
                    ret += 'e';
                break;
                case 'í':
                    ret += 'i';
                break;
                case 'ó':
                    ret += 'o';
                break;
                case 'ú':
                    ret += 'u';
                break;
                case 'ñ':
                    ret += "ny";
                break;
                default:
                    ret += s.charAt(i);
                break;
            }
        }

        return ret;
    }

    public static void ExamToGerman(int NumQuest){
        String[] s = new String[2];
        System.out.println("EXAMEN DE VOCABULARIO:\n");

        System.out.println("ESCRIBA LA TRADUCCIÓN DE LA PALABRA AL ALEMÁN CON SU VARIANTE PLURAL EN FORMATO ´, -s´:\n");
        System.out.println("Escriba su palabra sin acentos ni ñ (use ny).\n");

        for(int i = 0; i < NumQuest; i++){
            s = takeParts(RandEntry(), ':');
            System.out.println(s[1].substring(2,s[1].length()));

            sc = new Scanner(System.in);
            String k = sc.nextLine();
            if(k == ""){}
            System.out.println("La palabra era: "+s[0]+".\n");
        }
    }

    public static void Add(String filename){

        String aux = "";
        PrintWriter writer = null;
        FileInputStream fileR = null;

        try{
            FileWriter fw = new FileWriter(filename, true);
            fileR = new FileInputStream("vocab");  
            writer = new PrintWriter(fw);
        }
        catch(FileNotFoundException e){
            e.printStackTrace();
        }
        catch(IOException e){
            e.printStackTrace();
        }

        System.out.print("Escriba su palabra en alemán con su artículo correspondiente: ");
        System.out.println("Escriba su palabra sin acentos ni ñ (use ny).\n");

        sc = new Scanner(System.in);
        aux = sc.nextLine();

        sc = new Scanner(fileR);

        writer.print(aux);
        writer.flush();

        System.out.print("\nAhora, escriba su palabra en castellano: ");
        System.out.println("Escriba su palabra sin acentos ni ñ (use ny).\n");

        writer.print(" : ");
        writer.flush();
        
        sc = new Scanner(System.in);
        aux = sc.nextLine();
        writer.print(aux);
        writer.print("\n");
        writer.flush();   
        
        entryNum++;
    }

    public static void ShowList(){
        FileInputStream fileR = null;
        
        try{ 
            fileR = new FileInputStream("vocab");
        }
        catch (FileNotFoundException e){
            e.printStackTrace();
        }

        sc = new Scanner(fileR);

        System.out.println("|||--- LISTADO DE PALABRAS AÑADIDAS ---|||\n");

        int i = 1;
        while(sc.hasNextLine()){
            System.out.println("\t  "+i+". "+sc.nextLine());
            i++;
        }
    }

    public static void init(){
        
        boolean wrongInput = true;

        int caseOpt = 20;
        
        System.out.println("Elija su opción: \n");

        System.out.println("1. Iniciar un nuevo test de Alemán a Español.");
        System.out.println("2. Iniciar un nuevo test de Español a Alemán.");
        System.out.println("3. Añadir palabras nuevas.");
        System.out.println("4. Revisar palabras ya añadidas.");
        System.out.println("5. Salir de la aplicación.\n");

        do{
            try{
                sc = new Scanner(System.in);
                caseOpt = sc.nextInt();
                if(caseOpt > 5 || caseOpt <= 0){
                    System.err.println("\nElija una opción NUMÉRICA válida.\n");
                }
                else{
                    wrongInput = false;
                }
            }
            catch(InputMismatchException e){
                System.err.println("\nElija una opción NUMÉRICA válida.\n");
            }
        }while(wrongInput);

        switch(caseOpt){
            case 1:
                System.out.print("\033\143");
                System.out.println("¿Cuántas preguntas quiere que tenga su test?");
                
                wrongInput = true;

                do{
                    try{
                        sc = new Scanner(System.in);
                        caseOpt = sc.nextInt();
                        wrongInput = false;
                    }
                    catch(InputMismatchException e){
                        System.err.println("\nElija una opción NUMÉRICA válida.\n");
                    }
                }while(wrongInput);

                System.out.print("\033\143");
                ExamToSpanish(caseOpt);
                System.out.println("Presione la tecla ENTER para continuar...");
                try{
                    System.in.read();
                }  
                catch(Exception e){}  
                break;
            case 2:
                System.out.print("\033\143");
                System.out.println("¿Cuántas preguntas quiere que tenga su test?");
                
                wrongInput = true;

                do{
                    try{
                        sc = new Scanner(System.in);
                        caseOpt = sc.nextInt();
                        wrongInput = false;
                    }
                    catch(InputMismatchException e){
                        System.err.println("\nElija una opción NUMÉRICA válida.\n");
                    }
                }while(wrongInput);

                System.out.print("\033\143");
                ExamToGerman(caseOpt);
                System.out.println("Presione la tecla ENTER para continuar...");
                try{
                    System.in.read();
                }  
                catch(Exception e){}  
                break;
            case 3:
                System.out.print("\033\143");   
                Add("vocab");
                break;
            case 4:
                System.out.print("\033\143");
                ShowList();
                System.out.println("\nPresione la tecla ENTER para continuar...");
                try{
                    System.in.read();
                }  
                catch(Exception e){}  
                break;
            case 5:
                Over = true;
                break;
        }
    }
}
