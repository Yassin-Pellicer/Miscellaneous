package dia7;
import java.util.*;

public class Directory {

    String name;

    Directory parent;
    List<Integer> files;
    List<Directory> subDirs;


    Directory(String name, Directory parent) {
        this.name = name;
        this.parent = parent;

        files = new ArrayList<>();
        subDirs = new ArrayList<>();
    }

    int getSize(){

        int total = 0;

        for (int i = 0; i < files.size(); i++) {
            total += files.get(i);
        }

        for (int i = 0; i < subDirs.size(); i++) {
            total += subDirs.get(i).getSize();
        }

        return total;
    }

    @Override
    public String toString(){
        return this.name;
    }

    @Override
    public boolean equals(Object obj) {
        if(obj instanceof Directory && ((Directory) obj).name.equals(this.name)){
            return true;
        }
        return false;
    }
}