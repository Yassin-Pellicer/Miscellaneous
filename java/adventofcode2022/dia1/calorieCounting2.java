package dia1;
import java.io.*;
import java.util.*;

class calorieCounting2{
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
        ArrayList<Integer> calorieList = new ArrayList<Integer>();

        while(sc.hasNext()){
            
            String line = sc.nextLine();

            if(line.length() != 0){
                n += Integer.parseInt(line);
            }
            else{
                calorieList.add(n); 
                n = 0;
                continue;
            }
        
            if(counter < n){
                counter = n;
            }
            Collections.sort(calorieList, Collections.reverseOrder());
        }
        for(int i = 0; i < calorieList.size(); i++){
            System.out.println(calorieList.get(i));
        }
        System.out.println("\nSum of the highest three: "+(calorieList.get(0)+calorieList.get(1)+calorieList.get(2)));
    }
}