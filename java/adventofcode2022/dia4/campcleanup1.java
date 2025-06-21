package dia4;
import java.io.*;
import java.util.*;

public class campcleanup1 {
    public static void main(String[] args) {
        Scanner sc = null;
        try{
            sc = new Scanner(new File("input"));
        }
        catch(Exception e){
            System.err.println("File could not be found/open.");
        }

        int counter = 0;

        while(sc.hasNextLine()){
            String s = sc.nextLine();
            
            String[] parts = takePartsString(s, ',');
            System.out.println(parts[0]+" "+parts[1]);

            String[] firstNums = takePartsString(parts[0],'-');
            String[] secondNums = takePartsString(parts[1],'-');

            if(Integer.parseInt(firstNums[0]) <= Integer.parseInt(secondNums[0]) && Integer.parseInt(firstNums[1]) >= Integer.parseInt(secondNums[1])){ counter++; }
            else if(Integer.parseInt(firstNums[0]) >= Integer.parseInt(secondNums[0]) && Integer.parseInt(firstNums[1]) <= Integer.parseInt(secondNums[1])){ counter++; }
        }

        System.out.println(counter);
    }

    public static String[] takePartsString(String s, char t){

        String[] retString = new String[2];
        int i;

        for(i = 0; i < s.length(); i++){
            if(s.charAt(i) == t){
                retString[0] = s.substring(0,i);
                break;
            }
        }

        retString[1] = s.substring(i+1);
        return retString;
    }
}
