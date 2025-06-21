package dia8;
import java.util.*;
import java.io.*;

public class visibletree2{

    public static int heigth = 0;
    public static int width = 0;
    public static ArrayList<ArrayList<Integer>> forest = null;
    public static int hiscore = 0;
    

    public static void main(String[] args) {
        forest = matrix();
        System.out.println(visibleTrees());
    }

    public static ArrayList<ArrayList<Integer>> matrix(){

        ArrayList<ArrayList<Integer>> matrixData = new ArrayList<ArrayList<Integer>>();

        Scanner sc = null;
        try{
            sc = new Scanner(new File("adventofcode2022/dia8/input.txt"));
        }
        catch(Exception e){
            System.err.println("The file could not be opened");
        }

        while(sc.hasNextLine()){
            String s = sc.nextLine();
            width = s.length();
            
            matrixData.add(new ArrayList<Integer>());
            for(int i = 0; i < s.length(); i++){
                matrixData.get(heigth).add(Integer.parseInt(s.substring(i,i+1)));
            }
            heigth++;
        }
        return matrixData;
    }

    public static int visibleTrees(){
        for(int i = 0; i < width; i++){
            for(int j = 0; j < heigth; j++){;
                if(top(i, j)*right(i, j)*left(i, j)*bottom(i, j) > hiscore){
                    hiscore = top(i, j)*right(i, j)*left(i, j)*bottom(i, j);
                }
            }
        }
        return hiscore;
    }
 
    public static int top(int i, int j){
        int score = 0;
        int num = forest.get(i).get(j);
        for(int k = i; k > 0; k--){
            if(forest.get(k).get(j) >= num && k != i){
                return score;
            }
            score++;
        }
        return score;   
    }
    public static int bottom(int i, int j){
        int score = 0;
        int num = forest.get(i).get(j);
        for(int k = i; k < heigth-1; k++){
            if(forest.get(k).get(j) >= num && k != i){
                return score;
            }
            score++;
        }
        return score;
    }
    public static int left(int i, int j){
        int score = 0;
        int num = forest.get(i).get(j);
        for(int k = j; k > 0; k--){
            if(forest.get(i).get(k) >= num && k != j){
                return score;
            }
            score++;
        }
        return score;
    }
    public static int right(int i, int j){
        int score = 0;
        int num = forest.get(i).get(j);
        for(int k = j; k < width-1; k++){
            if(forest.get(i).get(k) >= num && k != j){
                return score;
            }
            score++;
        }
        return score;
    }
}