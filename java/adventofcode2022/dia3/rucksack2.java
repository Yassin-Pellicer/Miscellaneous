package dia3;
import java.util.*;
import java.io.File;

public class rucksack2 {
    public static void main(String[] args) {
        Scanner sc = null;
        try{
            sc = new Scanner(new File("adventofcode2022/dia3/input"));
        }
        catch(Exception e){
            System.err.println("File could not be opened.");
        }
        
        int n = 0;
        String s[] = new String[3];

        while(sc.hasNextLine()){
            int lines = 0;
            while(lines < 3){
                s[lines] = sc.nextLine();
                lines++;
            }

            System.out.println(s[0]);
            System.out.println(s[1]);
            System.out.println(s[2]);

            boolean found = false;

            int i = 0;
            while(i < s[0].length() && !found){
                int j = 0; 
                while(j < s[1].length() && !found){
                    int k = 0;
                    while(k < s[2].length() && !found){
                        if(s[0].charAt(i) == s[1].charAt(j) && s[0].charAt(i) == s[2].charAt(k)){

                            System.out.println(s[0].charAt(i));
                            if(Character.isUpperCase(s[0].charAt(i))){n += (Character.getNumericValue(s[0].charAt(i)) + 17);}
                            else{n += (Character.getNumericValue(s[0].charAt(i)) - 9);}
                            System.out.println(n);

                            found = !found;
                        }
                        k++;
                    }
                    j++;
                }
                i++;
            }
        }
    }
}
