package dia6;
import java.io.*;
import java.util.*;

public class string1 {
    public static void main(String[] args) {
        Scanner sc = null;
        try{
            sc = new Scanner(new File("adventofcode2022/dia6/input.txt"));
        }
        catch(FileNotFoundException e){
            System.err.println("File could not be initialized");
        }

        String s = sc.nextLine();
        System.out.println(findFirstPacket(s));
        System.out.println(findFirstMessage(s));

    }

    public static int findFirstPacket(String s){
        int n = 0;
        int result = 0;

        for(int i = 0; i < s.length()-3; i++){
            String subFour = s.substring(i,i+4);
            System.out.println(subFour);
            int count = 0;
            for(int j = 0; j < subFour.length(); j++){
                for(int k = 0; k < subFour.length(); k++){
                    if(subFour.charAt(j) == subFour.charAt(k) && j != k){         
                        count++;
                    }
                }
            }
            if(count == 0){
                result = n + 4;
                return (result);
            }
            n++;
        }

        return 0;
    }

    public static int findFirstMessage(String s){
        int n = 0;
        int result = 0;

        for(int i = 0; i < s.length()-13; i++){
            String subFour = s.substring(i,i+14);
            System.out.println(subFour);
            int count = 0;
            for(int j = 0; j < subFour.length(); j++){
                for(int k = 0; k < subFour.length(); k++){
                    if(subFour.charAt(j) == subFour.charAt(k) && j != k){         
                        count++;
                    }
                }
            }
            if(count == 0){
                result = n + 14;
                return (result);
            }
            n++;
        }

        return 0;
    }
}
