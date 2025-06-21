package dia3;
import java.util.*;
import java.io.File;

public class rucksack1 {
    public static void main(String[] args) {
        Scanner sc = null;
        try{
            sc = new Scanner(new File("adventofcode2022/dia3/input"));
        }
        catch(Exception e){
            System.err.println("File could not be opened.");
        }
        
        int n = 0;

        while(sc.hasNextLine()){
            String s = sc.nextLine();
            String firstCompartiment = s.substring(0, (s.length())/2);
            String secondCompartiment = s.substring((s.length())/2);
            
            System.out.print(firstCompartiment+" ");
            System.out.println(secondCompartiment);
            
            boolean found = false;

            int i = 0;
            while(i < firstCompartiment.length() && !found){
                int j = 0; 
                while(j < secondCompartiment.length() && !found){
                    if(firstCompartiment.charAt(i) == secondCompartiment.charAt(j)){

                        System.out.println(firstCompartiment.charAt(i));
                        if(Character.isUpperCase(firstCompartiment.charAt(i))){n += (Character.getNumericValue(firstCompartiment.charAt(i)) + 17);}
                        else{n += (Character.getNumericValue(firstCompartiment.charAt(i)) - 9);}
                        System.out.println(n);

                        found = !found;
                    }
                    j++;
                }
                i++;
            }
        }
    }
}
