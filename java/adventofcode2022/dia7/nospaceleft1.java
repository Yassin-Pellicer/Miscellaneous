package dia7;
import java.io.*;
import java.util.*;

public class nospaceleft1 {
    public static List<Directory> directories = new ArrayList<>();

    public static void main(String[] args) throws Exception{
        solve();
    }

    public static void part1(){
        // total up the directories to see who to delete
        int sum = 0;
    
        for (Directory dir: directories) {
            if(dir.getSize() < 100000){
                sum += dir.getSize();
            }
        }
    
        System.out.println("By deleting the chosen directories you can save " + sum + " space.");
    }

    public static void part2(){

        // part 2
        int freeSpace = 70000000 - directories.get(0).getSize();
        int spaceNeeded = 30000000 - freeSpace;
    
        // we have 25,640,133 gb free space
        // we need to free up 4,359,867 gb
        System.out.println("You have " + freeSpace + " free space.");
        System.out.println("You need to free up " + spaceNeeded + " to perform the update.");
    
        int smallest = directories.get(0).getSize();
        for (Directory dir: directories) {
            if(dir.getSize() <= smallest && dir.getSize() >= spaceNeeded){
                smallest = dir.getSize();
            }
        }
    
        System.out.println("The smallest directory you can get away with deleting has a size of " + smallest);
    }

    public static void solve() throws FileNotFoundException {
        Scanner scr = new Scanner(new File("adventofcode2022/dia7/input.txt"));

        // add the root
        Directory root = new Directory("/", null);
        Directory cur = root;
        directories.add(cur);

        // skip the first two lines of input, they don't matter.
        scr.nextLine();
        scr.nextLine();

        // build the file system
        while(scr.hasNextLine()){

            String s = scr.next();

            // handle the finding of a new directory
            if(s.equals("dir")){
                String dirName = scr.next();
                //print("New Directory found in " + cur.name + " called " + dirName);
                Directory temp = new Directory(dirName, cur);
                cur.subDirs.add(temp);
                directories.add(temp);
            }

            // handle the changing of a directory
            if(s.equals("cd")){

                String next = scr.next();

                // handle going out
                if(next.equals("..")){
                    //print("moving up to directory " + cur.parent.name);
                    cur = cur.parent;
                } else {
                    // handle going in
                    //print("moving in to directory " + next);
                    cur = cur.subDirs.get(cur.subDirs.indexOf(new Directory(next, cur)));
                }
            }

            // handle the finding of a file
            if(Character.isDigit(s.charAt(0))){
                String fileSize = s;
                System.out.println(fileSize);

                //print("found a file of size " + fileSize + ", which will be added to directory " + cur.name);
                cur.files.add(Integer.parseInt(fileSize));
            }

        }
        
        part1();
        part2();
    }
}
