package dia5;
import java.io.*;
import java.util.*;

public class supplystacks2 {

    public static ArrayList<ArrayList<Character>> totalCrateStacks =  new ArrayList<ArrayList<Character>>();
    public static int[] actions = new int[3];

    public static void main(String[] args) {
        Scanner sc = null;
        try{
            sc = new Scanner(new File("adventofcode2022/dia5/input.txt"));
        }
        catch(FileNotFoundException e){
            System.err.println("File could not be initialized");
        }

        while(sc.nextLine().length() != 0){
            totalCrateStacks.add(new ArrayList<Character>());
            System.out.println("Stack "+totalCrateStacks.size()+" added.");
        }
        System.out.println();

        fillInitialStacks(totalCrateStacks);
        drawStacks(totalCrateStacks);

        //interpretInstructions
        while(sc.hasNextLine()){
            String s = sc.nextLine();
            System.out.println(s);

            String[] strArray = s.split(" ");

            actions[0] = Integer.parseInt(strArray[1]);
            actions[1] = Integer.parseInt(strArray[3]);
            actions[2] = Integer.parseInt(strArray[5]);

            operation(actions, totalCrateStacks);
            System.out.println();
            drawStacks(totalCrateStacks);
        }

        result(totalCrateStacks);

    }

    //NOW, THE CRANE CAN LIFT ALL CRATES AT ONCE, AND PUT THEM IN THE ORIGINAL ORDER IN THE NEW STACK
    public static void operation(int[] act, ArrayList<ArrayList<Character>> p){
        for(int i = act[0]; i > 0; i--){
            p.get(act[2]-1).add(0, p.get(act[1]-1).remove(i-1));
        }
    }

    public static void fillInitialStacks(ArrayList<ArrayList<Character>> p){
    
        Scanner content = null;
        try{
            content = new Scanner(new File("adventofcode2022/dia5/input.txt"));
        }
        catch(FileNotFoundException e){
            System.err.println("File could not be initialized");
        }

        for(int j = 0; j < p.size(); j++){
            String s = content.nextLine();

            for(int i = 0; i < s.length(); i++){
                p.get(j).add(s.charAt(i));
            }
        }
    }

    public static void result(ArrayList<ArrayList<Character>> p){
        System.out.println();
        System.out.println("THE BOXES ON TOP ARE:");
        for(int i = 0; i < p.size(); i++){
            System.out.print(p.get(i).get(0));
        }
        System.out.println();
    }

    public static void drawStacks(ArrayList<ArrayList<Character>> p){
        for(int j = 0; j < p.size(); j++){
            for(int i = 0; i < p.get(j).size(); i++){
                System.out.print(p.get(j).get(i));
            }
            System.out.println();
        }
        System.out.println();
    }
}
