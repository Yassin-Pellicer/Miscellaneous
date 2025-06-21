package dia9;
import java.util.*;
import java.io.*;
        
public class rope1 {

    public static int x = 0;
    public static int y = 0;
    public static int xTail = 0;
    public static int yTail = 0;
    public static ArrayList<int[]> head = new ArrayList<int[]>();
    public static ArrayList<int[]> tail = new ArrayList<int[]>();

    public static void main(String[] args) {

        int[] k = {0, 0};
        tail.add(k);
        head.add(k);

        Scanner sc = null;
        try{
            sc = new Scanner(new File("adventofcode2022/dia9/input.txt"));
        }
        catch(Exception e){
            System.err.println("The file could not be opened");
        }

        while(sc.hasNextLine()){
            String s = sc.nextLine();
            updateCoordHead(s);
        }
        printPathHead();
        printPathTails();

        System.out.println("How many positions does the tail of the rope visit at least once?... "+tail.size());
    }

    public static void updateCoordHead(String s){
        String[] p = s.split(" ");
        switch(p[0]){
            case "U":
                for(int i = 0; i < Integer.parseInt(p[1]); i++){
                    y++;
                    int[] k = {x, y};
                    head.add(k);
                    updateCoordTails();
                }
            break;
            case "D":
                for(int i = 0; i < Integer.parseInt(p[1]); i++){
                    y--;
                    int[] k = {x, y};
                    head.add(k);
                    updateCoordTails();
                }
            break;
            case "L":
                for(int i = 0; i < Integer.parseInt(p[1]); i++){
                    x--;
                    System.out.println(x);
                    int[] k = {x, y};
                    head.add(k);
                    updateCoordTails();
                }
            break;
            case "R":
                for(int i = 0; i < Integer.parseInt(p[1]); i++){
                    x++;
                    int[] k = {x, y};
                    head.add(k);
                    updateCoordTails();
                }
            break;
        }
    }

    private static void updateCoordTails(){
        if(Math.abs(x-xTail) >= 2 || Math.abs(y-yTail) >= 2){
            System.out.println("act");
            xTail = head.get(head.size()-2)[0];
            yTail = head.get(head.size()-2)[1];

            int[] k = {xTail, yTail};
            int counter = 0;
            for(int i = 0; i < tail.size(); i++){
                if(k[0] == tail.get(i)[0] && k[1] == tail.get(i)[1]){
                    counter++;
                }
            }
            if(counter == 0){
                tail.add(k);
            }
        }
    }

    public static void printPathHead(){
        System.out.print("[");
        for(int i = 0; i < head.size(); i++){
            System.out.print("{"+head.get(i)[0]+", "+head.get(i)[1]+"}, ");
        }
        System.out.println("]");
    }

    public static void printPathTails(){
        System.out.print("[");
        for(int i = 0; i < tail.size(); i++){
            System.out.print("{"+tail.get(i)[0]+", "+tail.get(i)[1]+"}, ");
        }
        System.out.println("]");
    }
}
