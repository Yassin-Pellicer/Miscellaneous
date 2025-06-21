package dia8;
import java.util.*;
import java.io.*;

public class visibletree1{

    public static int heigth = 0;
    public static int width = 0;
    public static ArrayList<ArrayList<Integer>> forest = null;
    

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
        int retVal = heigth*2 + width*2 - 4;

        for(int i = 1; i < width-1; i++){
            for(int j = 1; j < heigth-1; j++){
                if(top(i, j)){retVal++;System.out.println("visible "+forest.get(i).get(j));}
                else if(bottom(i, j)){retVal++;System.out.println("visible "+forest.get(i).get(j));}
                else if(left(i, j)){retVal++;System.out.println("visible "+forest.get(i).get(j));}
                else if(right(i, j)){retVal++;System.out.println("visible "+forest.get(i).get(j));}
            }
        }
        return retVal;
    }

    public static boolean top(int i, int j){
        int num = forest.get(i).get(j);
        for(int k = 0; k < i; k++){
            if(forest.get(k).get(j) >= num){
                return false;
            }
        }
        return true;
    }
    public static boolean bottom(int i, int j){
        int num = forest.get(i).get(j);
        for(int k = heigth-1; k > i; k--){
            if(forest.get(k).get(j) >= num){
                return false;
            }
        }
        return true;
        
    }
    public static boolean left(int i, int j){
        int num = forest.get(i).get(j);
        for(int k = 0; k < j; k++){
            if(forest.get(i).get(k) >= num){
                return false;
            }
        }
        return true;
        
    }
    public static boolean right(int i, int j){
        int num = forest.get(i).get(j);
        for(int k = width-1; k > j; k--){
            if(forest.get(i).get(k) >= num){
                return false;
            }
        }
        return true;
        
    }
}