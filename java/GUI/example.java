package GUI;

import java.awt.BorderLayout;
import java.awt.GridLayout;
import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JPanel;

public class example{
    public example(){
        JFrame frame = new JFrame();
        JPanel panel = new JPanel();
        JButton button = new JButton("click me!");
        panel.setBorder(BorderFactory.createEmptyBorder(30, 30, 10, 10));
        panel.setLayout(new GridLayout(0, 1));
        panel.add(button);

        frame.add(panel, BorderLayout.CENTER);
        frame.setTitle("our GUI");
        frame.pack();
        frame.setVisible(true);
    }
    public static void main(String[] args){
        new example();
    }
}