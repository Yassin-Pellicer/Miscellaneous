/* Use the slash-star style comments or the system won't see your
   identification information */
/*
ID: Yassin Pellicer Lamla [yassinp2]
LANG: JAVA
TASK: test
*/

package USACO;
import java.io.*;
import java.util.*;

public class test {
    public static void main (String [] args) throws IOException {
        // Use BufferedReader rather than RandomAccessFile; it's much faster
        BufferedReader f = new BufferedReader(new FileReader("test.in"));
                                                    // input file name goes above
        PrintWriter out = new PrintWriter(new BufferedWriter(new FileWriter("test.out")));
        // Use StringTokenizer vs. readLine/split -- lots faster
        StringTokenizer st = new StringTokenizer(f.readLine());
                            // Get line, break into tokens
        int i1 = Integer.parseInt(st.nextToken());    // first integer
        int i2 = Integer.parseInt(st.nextToken());    // second integer
        out.println(i1+i2);                           // output result
        out.close();                                  // close the output file
        f.close();
    }
}
