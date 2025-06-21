package dia2;
import java.util.*;
import java.io.*;

public class rockpaperscissors1 {
    public static void main(String[] args) {
        Scanner sc = null;
        try{
            sc = new Scanner(new File("adventofcode2022/dia2/input"));
        }
        catch(Exception e){
            System.err.println("The file could not be opened");
        }

        int score = 0;

        while(sc.hasNextLine()){
            String s = sc.nextLine();
            char elfMove = s.charAt(0);
            char OurMove = s.charAt(2);

            /*
             * A == rock == X | +1
             * B == paper == Y | +2
             * C == scissors == Z | +3
             * 
             * win += 6
             * draw += 3
             * loss += 0
             */

            switch(elfMove){
                case 'A':
                    if(OurMove != 'Y'){
                        if(OurMove == 'X'){ score += 4; } //draw
                        if(OurMove == 'Z'){ score += 3; } //lose
                    }
                    else{
                        score += 8;
                    }
                break;
                case 'B':
                    if(OurMove != 'Z'){
                        if(OurMove == 'X'){ score+= 1; } //lose
                        if(OurMove == 'Y'){ score+= 5; } //draw
                    }
                    else{
                        score += 9;
                    }
                break;
                case 'C':
                    if(OurMove != 'X'){
                        if(OurMove == 'Y'){ score+= 2; } //lose
                        if(OurMove == 'Z'){ score+= 6; } //draw
                    }
                    else{
                        score += 7;
                    }
                break;
            }
        }

        System.out.println(score);
    }
}
