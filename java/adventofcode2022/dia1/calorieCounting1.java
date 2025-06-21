package dia1;
import java.io.*;
import java.util.*;

class calorieCounting1{
    public static void main(String[] args) {
        Scanner sc = null;
        try{
            sc = new Scanner(new File("dia1/PuzzInp"));
        }
        catch(FileNotFoundException e){
            System.err.println("File could not be initialized");
        }

        int counter = 0;
        int n = 0;

        while(sc.hasNext()){
            
            String line = sc.nextLine();

            if(line.length() != 0){
                n += Integer.parseInt(line);
            }
            else{
                n = 0;
                continue;
            }

            if(counter < n){
                counter = n;
            }
        }

        System.out.println(counter);
    }
}